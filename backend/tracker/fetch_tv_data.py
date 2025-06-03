import os
import json
import argparse
from datetime import datetime
from tqdm import tqdm
from tvDatafeed import TvDatafeed, Interval
import traceback

# === Config ===
DEFAULT_SYMBOLS = ["SPY", "QQQ", "AAPL"]
CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cache"))
os.makedirs(CACHE_DIR, exist_ok=True)

# Bars per interval for extended chart logic
BARS_CONFIG = {
    "1m": 1500,     # ~2.5 days
    "5m": 1000,     # ~1 week
    "30m": 120,     # ~3–4 weeks
    "1h": 150,       # ~1 month+
    "4h": 90,       # ~3 months
    "1d": 250       # ~ 1 year
}

INTERVAL_MAP = {
#    "1m": Interval.in_1_minute,
    "5m": Interval.in_5_minute,
    "30m": Interval.in_30_minute,
    "1h": Interval.in_1_hour,
    "4h": Interval.in_4_hour,
    "1d": Interval.in_daily, 
}

tv = TvDatafeed()

def fetch_tv_candles(symbol: str, interval_label: str, bars: int):
    try:
        interval = INTERVAL_MAP[interval_label]

        # Enable extended hours only for 5m candles
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

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbols", nargs="+", help="List of symbols to fetch", required=False)
    parser.add_argument("--short", action="store_true", help="Fetch shorter set for debugging")
    args = parser.parse_args()
    return args.symbols or DEFAULT_SYMBOLS, args.short

def main():
    symbols, short_mode = get_args()
    result = {}

    print(f"📡 Fetching TV candles for: {', '.join(symbols)}")
    for symbol in tqdm(symbols):
        interval_data = {}
        for label in INTERVAL_MAP:
            bars = 250 if short_mode else BARS_CONFIG[label]
            candles = fetch_tv_candles(symbol, label, bars)
            if candles:
                interval_data[label] = candles

        if not interval_data:
            print(f"⚠️ Skipping {symbol}, no data returned.")
            continue

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
