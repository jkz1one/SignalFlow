## 945_signals.py

import os
import json
import yfinance as yf
from datetime import datetime
from tqdm import tqdm

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

TODAY_STR = datetime.now().strftime("%Y-%m-%d")
OUTPUT_PATH = os.path.join(CACHE_DIR, f"945_signals_{TODAY_STR}.json")

# --- Load Universe ---
def get_latest_universe_file():
    files = [
        f for f in os.listdir(CACHE_DIR)
        if f.startswith("universe_") and f.endswith(".json") and "cache" not in f
    ]
    if not files:
        raise FileNotFoundError("❌ No dated universe files found in cache.")
    files.sort(key=lambda f: os.path.getmtime(os.path.join(CACHE_DIR, f)), reverse=True)
    latest_file = os.path.join(CACHE_DIR, files[0])
    print(f"📄 Using universe file: {os.path.basename(latest_file)}")
    return latest_file

UNIVERSE_PATH = get_latest_universe_file()

# --- Main Scraper for 9:40 Breakout Inputs ---
def main():
    with open(UNIVERSE_PATH, "r") as f:
        universe = json.load(f)
    symbols = list(universe.keys())

    signals_output = {
        "timestamp": datetime.now().isoformat(),
        "candles": {}
    }

    print(f"📡 Pulling 09:30–09:45 5m candles for {len(symbols)} tickers...")

    for symbol in tqdm(symbols, desc="🔎 Fetching Candles"):
        try:
            yf_symbol = symbol.replace(".", "-")  # e.g. BRK.B -> BRK-B
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period="1d", interval="5m")

            # Extract relevant 5-minute candles
            candles = hist.between_time("09:30", "09:45")
            if len(candles) < 3:
                continue

            candle_930 = candles.iloc[0]  # 09:30–09:35
            candle_935 = candles.iloc[1]  # 09:35–09:40
            candle_940 = candles.iloc[2]  # 09:40–09:45

            high_range = max(candle_930['High'], candle_935['High'])
            low_range = min(candle_930['Low'], candle_935['Low'])
            close_945 = candle_940['Close']

            signals_output["candles"][symbol] = {
                "940_high": round(high_range, 2),
                "940_low": round(low_range, 2),
                "close_945": round(close_945, 2),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            tqdm.write(f"⚠️ Failed for {symbol}: {e}")

    with open(OUTPUT_PATH, "w") as f:
        json.dump(signals_output, f, indent=2)

    print(f"✅ 9:40 breakout signal input candles saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
