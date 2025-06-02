from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
import os, json
from datetime import datetime
import pandas as pd

router = APIRouter()
CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'cache')

# --- Helper to group candles into longer intervals ---
def group_candles(raw, interval_minutes):
    REQUIRED_KEYS = ['time', 'open', 'high', 'low', 'close']
    cleaned = [{k: entry.get(k, None) for k in REQUIRED_KEYS} for entry in raw]

    df = pd.DataFrame(cleaned)
    for col in REQUIRED_KEYS:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df['dt'] = pd.to_datetime(df['time'], unit='s', errors='coerce')
    df.set_index('dt', inplace=True)

    df.dropna(subset=['open', 'high', 'low', 'close'], inplace=True)
    if df.empty:
        return []

    rule = f'{interval_minutes}min'
    ohlc = df.resample(rule, label='right', closed='right').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last'
    }).dropna()

    if ohlc.empty:
        return []

    ohlc.reset_index(inplace=True)
    ohlc['time'] = ohlc['dt'].astype('int64') // 10**9

    return ohlc[['time', 'open', 'high', 'low', 'close']].to_dict(orient='records')


# --- Helper to calculate EMA ---
def calculate_ema(candles, span):
    if not candles:
        return []
    closes = pd.Series([c['close'] for c in candles])
    ema = closes.ewm(span=span, adjust=False).mean()
    return [{"time": candles[i]["time"], "value": round(v, 2)} for i, v in enumerate(ema)]


# --- API Route ---
@router.get("/api/tracker-candles")
def get_tracker_candles(
    symbol: str = Query(...),
    interval: str = Query(default="30m"),
    date: str = Query(default=datetime.now().strftime("%Y-%m-%d"))
):
    interval_map = {
        "5m": 5, "10m": 10, "30m": 30,
        "1h": 60, "4h": 240, "d": 1440
    }
    if interval not in interval_map:
        raise HTTPException(status_code=400, detail="Invalid interval")

    symbol = symbol.upper()
    filename = f"tv_candles_{symbol}_{date}.json"
    filepath = os.path.join(CACHE_DIR, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"Raw candle file not found: {filename}")

    try:
        with open(filepath, "r") as f:
            raw = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse candle file: {str(e)}")

    # Normalize raw structure
    if isinstance(raw, dict):
        if "candles" in raw:
            raw = raw["candles"]
        elif interval in raw:
            raw = raw[interval]
        else:
            raise HTTPException(status_code=500, detail="Candle file missing expected keys")

    # Patch 'timestamp' → 'time' as epoch
    for entry in raw:
        if isinstance(entry, dict) and "timestamp" in entry and "time" not in entry:
            try:
                dt = pd.to_datetime(entry["timestamp"])
                entry["time"] = int(dt.timestamp())
            except:
                entry["time"] = None  # fallback to NaN-safe value

    # Final validation
    if not isinstance(raw, list) or not all(isinstance(item, dict) for item in raw):
        raise HTTPException(status_code=500, detail="Malformed candle file: expected list of dicts")

    grouped = group_candles(raw, interval_map[interval])
    if not grouped:
        raise HTTPException(status_code=400, detail="No valid candles after cleaning")

    ema10 = calculate_ema(grouped, 10)
    ema50 = calculate_ema(grouped, 50)

    return JSONResponse(content={
        "candles": grouped,
        "ema10": ema10,
        "ema50": ema50
    })
