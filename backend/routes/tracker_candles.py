# backend/routes/tracker_candles.py

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
import os, json
from datetime import datetime
from backend.tracker.build_tracker_candles import build as build_tracker


router = APIRouter()
CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'cache')

@router.get("/api/tracker-candles")
def get_tracker_candles(
    symbol: str = Query(...),
    interval: str = Query(default="30m"),
    date: str = Query(default=datetime.now().strftime("%Y-%m-%d"))
):
    allowed = {"5m", "10m", "30m", "1h", "4h", "1d"}
    if interval not in allowed:
        raise HTTPException(status_code=400, detail="Invalid interval")

    symbol = symbol.upper()
    path = os.path.join(CACHE_DIR, f"tracker_candles_{symbol}_{date}.json")

    # Try loading; if not found, build on-demand
    if not os.path.exists(path):
        from backend.tracker.build_tracker_candles import build as build_tracker
        build_tracker(symbol, date)
        if not os.path.exists(path):
            raise HTTPException(status_code=500, detail="Failed to build tracker cache")

    with open(path, "r") as f:
        data = json.load(f)

    result = data.get("intervals", {}).get(interval)
    if not result:
        raise HTTPException(status_code=404, detail=f"No data for {interval}")

    return JSONResponse(content=result)

