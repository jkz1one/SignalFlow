import os, json
import pandas as pd
from datetime import datetime

CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'cache')
INTERVALS = {
    "5m": 5,
    "10m": 10,
    "30m": 30,
    "1h": 60,
    "4h": 240,
    "1d": 1440
}

def group_candles(raw, interval_minutes):
    df = pd.DataFrame(raw)
    if 'timestamp' in df.columns and 'time' not in df.columns:
        df['time'] = pd.to_datetime(df['timestamp']).astype(int) // 10**9
    df['dt'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('dt', inplace=True)

    ohlc = df.resample(f"{interval_minutes}min", label='right', closed='right').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last'
    }).dropna()

    ohlc.reset_index(inplace=True)
    ohlc['time'] = ohlc['dt'].astype('int64') // 10**9
    return ohlc[['time', 'open', 'high', 'low', 'close']].to_dict(orient='records')

def calculate_ema(candles, span):
    closes = pd.Series([c['close'] for c in candles])
    ema = closes.ewm(span=span, adjust=False).mean()
    return [{"time": candles[i]["time"], "value": round(v, 2)} for i, v in enumerate(ema)]

def build(symbol: str, date: str):
    input_path = os.path.join(CACHE_DIR, f"tv_candles_{symbol}_{date}.json")
    output_path = os.path.join(CACHE_DIR, f"tracker_candles_{symbol}_{date}.json")

    if not os.path.exists(input_path):
        print(f"❌ Missing raw candle file: {input_path}")
        return

    with open(input_path, "r") as f:
        raw = json.load(f)

    result = {
        "symbol": symbol,
        "date": date,
        "intervals": {}
    }

    raw_5m = raw.get("5m", [])
    if not raw_5m:
        print("❌ No 5m candles in raw file.")
        return

    for interval, minutes in INTERVALS.items():
        if interval == "10m":
            candles = group_candles(raw_5m, minutes)
        else:
            candles = raw.get(interval, [])

        if not candles:
            print(f"⚠️ Skipping {interval}: no data.")
            continue

        # Always patch "time" from "timestamp"
        for entry in candles:
            ts = entry.get("timestamp")
            if ts:
                try:
                    entry["time"] = int(pd.to_datetime(ts).timestamp())
                except:
                    entry["time"] = None

        ema10 = calculate_ema(candles, 10)
        ema50 = calculate_ema(candles, 50)

        result["intervals"][interval] = {
            "candles": candles,
            "ema10": ema10,
            "ema50": ema50
        }

        print(f"📦 Processed {symbol} @ {interval}: {len(candles)} bars")

    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"✅ Built tracker cache: {output_path}")

if __name__ == "__main__":
    build("SPY", datetime.now().strftime("%Y-%m-%d"))
