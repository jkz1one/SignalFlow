from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import os
import re
from datetime import datetime

# --- Route imports ---
from backend.routes import api_global_context
from backend.signals import fetch_global_context  # WebSocket route
from backend.routes import tracker_router as tracker_module
from backend.routes import raw_candles
from backend.routes import tracker_candles
app = FastAPI()

# --- Register routers ---
app.include_router(api_global_context.router, prefix="/api")
app.include_router(fetch_global_context.router)
app.include_router(tracker_module.router, prefix="/api")
app.include_router(raw_candles.router)
app.include_router(tracker_candles.router)

# --- CORS setup ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CACHE_DIR = "backend/cache"

# --- Utility Functions ---
def load_json_file(path: str, label: str):
    if not os.path.exists(path):
        return JSONResponse({"error": f"{label} not found at path: {path}"}, status_code=404)
    with open(path, "r") as f:
        return json.load(f)

def load_latest_file(prefix: str, label: str, required=True):
    files = [f for f in os.listdir(CACHE_DIR) if f.startswith(prefix) and f.endswith(".json")]
    if not files:
        if required:
            return {"error": f"No file found for {label} with prefix {prefix}"}
        else:
            return {}
    files.sort(key=lambda f: os.path.getmtime(os.path.join(CACHE_DIR, f)), reverse=True)
    path = os.path.join(CACHE_DIR, files[0])
    with open(path, "r") as f:
        return json.load(f)

# --- API Endpoints ---
@app.get("/api/scored")
async def get_universe():
    return JSONResponse(content=load_latest_file("universe_scored_", "Scored Universe"))

@app.get("/api/enriched")
async def get_universe_enriched():
    return JSONResponse(content=load_latest_file("universe_enriched_", "Enriched Universe"))

@app.get("/api/raw")
async def get_universe_raw():
    pattern = re.compile(r"^universe_\d{4}-\d{2}-\d{2}\.json$")
    files = [f for f in os.listdir(CACHE_DIR) if pattern.match(f)]
    if not files:
        return JSONResponse({"error": "No raw universe file found with format universe_YYYY-MM-DD.json"}, status_code=404)
    files.sort(key=lambda f: os.path.getmtime(os.path.join(CACHE_DIR, f)), reverse=True)
    latest_file = os.path.join(CACHE_DIR, files[0])
    with open(latest_file, "r") as f:
        return JSONResponse(content=json.load(f))

@app.get("/api/sector")
async def get_sector_rotation():
    files = [f for f in os.listdir(CACHE_DIR) if f.startswith("sector_") and f.endswith(".json")]
    if not files:
        return JSONResponse(content={"error": "No sector_<date>.json file found"}, status_code=404)

    files.sort(key=lambda f: os.path.getmtime(os.path.join(CACHE_DIR, f)), reverse=True)
    latest_filename = files[0]
    latest_path = os.path.join(CACHE_DIR, latest_filename)

    try:
        with open(latest_path, "r") as f:
            sector_data = json.load(f)

        file_date = latest_filename[len("sector_"):-len(".json")]

        return JSONResponse(content={
            "date": file_date,
            "data": sector_data
        })

    except Exception as e:
        return JSONResponse(
            content={"error": f"Failed to load or parse {latest_filename} — {str(e)}"},
            status_code=500
        )

@app.get("/api/autowatchlist")
async def get_watchlist():
    return JSONResponse(content=load_latest_file("autowatchlist_cache", "AutoWatchlist"))

@app.get("/api/cache-timestamps")
async def get_cache_timestamps():
    tracked_files = [
        "post_open_signals",
        "945_signals",
        "universe_enriched",
        "universe_scored",
        "autowatchlist_cache",
        "global_context.json"
    ]

    now = datetime.now()
    freshness_minutes = 1440
    output = {}

    for prefix in tracked_files:
        matching = [f for f in os.listdir(CACHE_DIR) if f.startswith(prefix)]
        if matching:
            matching.sort(key=lambda f: os.path.getmtime(os.path.join(CACHE_DIR, f)), reverse=True)
            f = matching[0]
            full_path = os.path.join(CACHE_DIR, f)
            modified_ts = os.path.getmtime(full_path)
            modified_dt = datetime.fromtimestamp(modified_ts)
            is_fresh = (now - modified_dt).total_seconds() < freshness_minutes * 60
            output[prefix] = {
                "filename": f,
                "last_modified": modified_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "is_fresh": is_fresh
            }
        else:
            output[prefix] = {
                "filename": "Missing",
                "last_modified": "Missing",
                "is_fresh": False
            }

    return JSONResponse(content=output)
