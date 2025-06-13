from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import os, json, subprocess
from datetime import datetime
# import logging

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
        return JSONResponse(status_code=400, content={"error": "Invalid interval"})

    symbol = symbol.upper()
    path = os.path.join(CACHE_DIR, f"tracker_candles_{symbol}_{date}.json")

    try:
        if not os.path.exists(path):
            if cache_only:
                return JSONResponse(status_code=404, content={"error": "Candle cache not available"})
            subprocess.run(
                ["python", "backend/tracker/run_tracker_chart.py", symbol],
                check=True,
                capture_output=True
            )
        elif not cache_only:
            subprocess.run(
                ["python", "backend/tracker/run_tracker_chart.py", symbol],
                check=True,
                capture_output=True
            )
    except subprocess.CalledProcessError as e:
        # logging.error(f"[tracker-candles] Subprocess failed for {symbol} ({interval}): {e.stderr.decode().strip()}")
        return JSONResponse(status_code=500, content={"error": "Error loading chart data."})

    if not os.path.exists(path):
        return JSONResponse(status_code=500, content={"error": "Candle cache missing after build"})

    try:
        with open(path, "r") as f:
            data = json.load(f)
        interval_block = data.get("intervals", {}).get(interval)
        if not interval_block or "candles" not in interval_block:
            return JSONResponse(status_code=404, content={"error": f"No data for interval '{interval}'"})

        return JSONResponse(content={
            "symbol": symbol,
            "interval": interval,
            "candles": interval_block["candles"],
            "ema10": interval_block.get("ema10"),
            "ema50": interval_block.get("ema50")
        })

    except Exception as e:
        # logging.error(f"[tracker-candles] JSON load failed for {symbol}: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Failed to parse chart data."})
