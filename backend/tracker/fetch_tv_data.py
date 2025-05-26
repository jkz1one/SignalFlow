import os
import json
import argparse
from datetime import datetime
from tqdm import tqdm
from tvdatafeed import TvDatafeed, Interval

# === Config ===
EXCHANGE = "AMEX"  # Update per symbol if needed
DEFAULT_SYMBOLS = ["SPY", "QQQ", "AAPL"]

USERNAME = os.getenv("TV_USER") or None
PASSWORD = os.getenv("TV_PASS") or None
tv = TvDatafeed(username=USERNAME, password=PASSWORD)

# === Helpers ===
def fetch_tv_candles(symbol: str, interval: Interval, bars: int = 500):
    try:
        df = tv.get_hist(symbol, EXCHANGE, interval=interval, n_bars=bars)
        if df is None or df.empty:
            return None
        df.reset_index(inplace=True)
        df["timestamp"] = df["datetime"].astype(str)
        return df[["timestamp", "open", "high", "low", "close", "volume"]].to_dict(orient="records")
    except Exception as e:
        print(f"❌ Failed to fetch {symbol} @ {interval}: {e}")
        return None

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbols", nargs="+", help="List of symbols to fetch", required=False)
    args = parser.parse_args()
    return args.symbols or DEFAULT_SYMBOLS

# === Main ===
def main():
    symbols = get_args()
    result = {}

    print(f"📡 Fetching TV candles for: {', '.join(symbols)}")
    for symbol in tqdm(symbols):
        result[symbol] = {}
        for label, interval in {
            "5m": Interval.in_5_min,
            "30m": Interval.in_30_min,
            "1h": Interval.in_1_hour
        }.items():
            candles = fetch_tv_candles(symbol, interval)
            if candles:
                result[symbol][label] = candles

    # Save individual files
    for symbol in result:
        out_path = f"backend/cache/tv_candles_{symbol}_{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(out_path, "w") as f:
            json.dump(result[symbol], f, indent=2)
        print(f"✅ Saved: {out_path}")

if __name__ == "__main__":
    main()
