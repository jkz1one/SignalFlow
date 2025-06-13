#fetch_mometum_data.py
# backend/tracker/fetch_momentum_data.py

import os
import json
import sys
from datetime import datetime
from tvDatafeed import TvDatafeed, Interval
import traceback

# === Config ===
CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cache"))
os.makedirs(CACHE_DIR, exist_ok=True)

# Minimal set for dashboard
INTERVALS = {
    "5m": Interval.in_5_minute,
    "30m": Interval.in_30_minute,
    "1h": Interval.in_1_hour
}

BARS_CONFIG = {
    "5m": 1000,
    "30m": 120,
    "1h": 150
}

tv = TvDatafeed()

def fetch_tv_candles(symbol: str, interval_label: str, bars: int):
    try:
        interval = INTERVALS[interval_label]
        extended = interval_label == "5m"

        df = tv.get_hist(
            symbol=symbol,
            exchange="",
            interval=interval,
            n_bars=bars,
            extended_session=extended
        )

        if df is None or df.empty:
            return None

        df.reset_index(inplace=True)
        df["timestamp"] = df["datetime"].astype(str)
        return df[["timestamp", "open", "high", "low", "close", "volume"]].to_dict(orient="records")
    except Exception as e:
        print(f"❌ Failed to fetch {symbol} @ {interval_label}: {e}")
        traceback.print_exc()
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python fetch_momentum_data.py SYMBOL")
        sys.exit(1)

    symbol = sys.argv[1].upper()
    print(f"📡 Fetching momentum candles for {symbol}...")

    interval_data = {}
    for label in INTERVALS:
        candles = fetch_tv_candles(symbol, label, BARS_CONFIG[label])
        if candles:
            interval_data[label] = candles

    if not interval_data:
        print(f"⚠️ Skipping {symbol}, no candle data returned.")
        return

    output = {
        "symbol": symbol,
        "fetchedAt": datetime.now().isoformat(),
        **interval_data
    }

    out_path = os.path.join(CACHE_DIR, f"tv_candles_{symbol}_{datetime.now().strftime('%Y-%m-%d')}.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"✅ Saved: {out_path}")

if __name__ == "__main__":
    main()
