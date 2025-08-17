from fastapi import APIRouter
from fastapi.responses import JSONResponse
import os, json
from datetime import datetime

router = APIRouter()

CACHE_DIR = "backend/cache"
LOCK_PATH = os.path.join(CACHE_DIR, "scrape.lock")
MAX_AGE_SEC = 60 * 30  # stale lock safety

def _read_lock():
    if not os.path.exists(LOCK_PATH):
        return {"scraping": False, "phase": "idle", "process": None}
    try:
        mtime = os.path.getmtime(LOCK_PATH)
        age = datetime.now().timestamp() - mtime
        if age > MAX_AGE_SEC:
            return {"scraping": False, "phase": "idle", "process": None}
        with open(LOCK_PATH, "r") as f:
            proc = f.read().strip() or None
        return {"scraping": True, "phase": "running", "process": proc}
    except Exception:
        return {"scraping": True, "phase": "running", "process": None}

@router.get("/system-status")
async def system_status():
    status = _read_lock()
    # Optional: include watchlist_count for the UI
    files = [f for f in os.listdir(CACHE_DIR) if f.startswith("autowatchlist_cache") and f.endswith(".json")]
    count = 0
    if files:
        files.sort(key=lambda f: os.path.getmtime(os.path.join(CACHE_DIR, f)), reverse=True)
        try:
            with open(os.path.join(CACHE_DIR, files[0]), "r") as f:
                data = json.load(f)
            count = len(data) if isinstance(data, list) else len(data.get("tickers", []))
        except Exception:
            count = 0

    return JSONResponse({
        "scraping": status["scraping"],
        "phase": status["phase"],
        "process": status["process"],
        "watchlist_count": count,
    })
