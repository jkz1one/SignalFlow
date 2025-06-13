from fastapi import APIRouter
from fastapi.responses import JSONResponse
import subprocess, os, json
# import logging

router = APIRouter()
CACHE_DIR = "backend/cache"

@router.get("/tracker/{symbol}")
def get_tracker_data(symbol: str):
    symbol = symbol.upper()

    # Step 1: Run DASHBOARD pipeline (lightweight fetch + signal calc)
    try:
        result = subprocess.run(
            ["python", "backend/tracker/run_tracker_dashboard.py", symbol],
            capture_output=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        # logging.error(f"[tracker] Subprocess failed for {symbol}: {e.stderr.decode().strip()}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error loading tracker data for {symbol}."}
        )

    # Step 2: Load prebuilt signal file
    path = os.path.join(CACHE_DIR, f"tracker_signals_{symbol}.json")
    if not os.path.exists(path):
        return JSONResponse(
            status_code=404,
            content={"error": f"No tracker output found for {symbol}"}
        )

    try:
        with open(path, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        # logging.error(f"[tracker] JSON load failed for {symbol}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to load tracker data for {symbol}."}
        )
