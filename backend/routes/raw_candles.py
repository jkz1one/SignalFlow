# backend/routes/raw_candles.py

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
import os
import json
from datetime import datetime

router = APIRouter()

CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'cache')

@router.get("/api/raw-candles")
def get_raw_candles(
    symbol: str = Query(..., description="Ticker symbol, e.g. SPY"),
    date: str = Query(default=datetime.now().strftime("%Y-%m-%d"), description="Date in YYYY-MM-DD")
):
    symbol = symbol.upper()
    filename = f"tv_candles_{symbol}_{date}.json"
    filepath = os.path.join(CACHE_DIR, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"Candle file not found: {filename}")

    with open(filepath, "r") as f:
        try:
            candles = json.load(f)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail=f"Failed to parse {filename}")

    return JSONResponse(content=candles)
