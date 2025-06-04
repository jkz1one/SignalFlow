from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
import os, json, subprocess
from datetime import datetime
from backend.tracker.build_tracker_candles import build as build_tracker

router = APIRouter()
CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'cache')

@router.get("/api/tracker-candles")
def get_tracker_candles(
    symbol: str = Query(...),
    interval: str = Query(default="30m"),
    date: str = Query(default=datetime.now().strftime("%Y-%m-%d")),
    cache_only: bool = Query(default=False)
):
    allowed = {"5m", "10m", "30m", "1h", "4h", "1d"}
    if interval not in allowed:
        raise HTTPException(status_code=400, detail="Invalid interval")

    symbol = symbol.upper()
    path = os.path.join(CACHE_DIR, f"tracker_candles_{symbol}_{date}.json")

    if not os.path.exists(path):
        if cache_only:
            raise HTTPException(status_code=404, detail="Cache not available")
        try:
            subprocess.run(
                ["python", "backend/tracker/run_tracker.py", symbol],
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"Tracker pipeline failed: {e.stderr.decode()}")

        try:
            build_tracker(symbol, date)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Build failed: {str(e)}")

        if not os.path.exists(path):
            raise HTTPException(status_code=500, detail="Tracker cache missing after build")

    elif not cache_only:
        try:
            subprocess.run(
                ["python", "backend/tracker/run_tracker.py", symbol],
                check=True
            )
            build_tracker(symbol, date)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")

    with open(path, "r") as f:
        data = json.load(f)

    result = data.get("intervals", {}).get(interval)
    if not result:
        raise HTTPException(status_code=404, detail=f"No data for {interval}")

    return JSONResponse(content=result)
