import os
import json
import yfinance as yf
import time
import random
from datetime import datetime
from tqdm import tqdm

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

TODAY_STR = datetime.now().strftime("%Y-%m-%d")
OUTPUT_PATH = os.path.join(CACHE_DIR, f"post_open_signals_{TODAY_STR}.json")
LOOKBACK_DAYS = 10
SAVE_INTERVAL = 25  # Save after every N tickers

SECTOR_ETFS = [
    "XLF", "XLK", "XLE", "XLV", "XLY",
    "XLI", "XLP", "XLU", "XLRE", "XLB", "XLC"
]

def get_latest_universe_file():
    files = [
        f for f in os.listdir(CACHE_DIR)
        if f.startswith("universe_") and f.endswith(".json") and "cache" not in f
    ]
    if not files:
        raise FileNotFoundError("❌ No dated universe files found in cache.")
    files.sort(key=lambda f: os.path.getmtime(os.path.join(CACHE_DIR, f)), reverse=True)
    return os.path.join(CACHE_DIR, files[0])

def save_progress(output):
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

def fetch_yf_data(symbol, lookback_days=10, retries=3):
    yf_symbol = symbol.replace(".", "-")
    for attempt in range(retries):
        try:
            ticker = yf.Ticker(yf_symbol)
            daily_hist = ticker.history(period=f"{lookback_days + 1}d")
            intraday_hist = ticker.history(period="1d", interval="5m")
            info = ticker.info

            rel_vol, avg_vol_10d = None, None
            if not daily_hist.empty and len(daily_hist) >= 10:
                past_volumes = daily_hist['Volume'][:-1]
                avg_vol_10d = past_volumes.mean()
                today_volume = daily_hist['Volume'].iloc[-1]
                rel_vol = today_volume / avg_vol_10d if avg_vol_10d > 0 else 0

            early_move = None
            if not intraday_hist.empty:
                early_candle = intraday_hist.between_time("09:30", "09:35")
                if not early_candle.empty:
                    early_open = early_candle['Open'].iloc[0]
                    early_close = early_candle['Close'].iloc[-1]
                    if early_open and early_close and early_open != 0:
                        early_move = round(((early_close - early_open) / early_open) * 100, 2)

            output = {
                "last_price": info.get("regularMarketPrice"),
                "vol_latest": info.get("volume"),
                "pct_change": info.get("regularMarketChangePercent"),
                "open_price": info.get("open"),
                "prev_close": info.get("previousClose"),
                "timestamp": datetime.now().isoformat(),
            }

            if rel_vol is not None:
                output["rel_vol"] = round(rel_vol, 2)
            if avg_vol_10d is not None:
                output["avg_vol_10d"] = int(avg_vol_10d)
            if early_move is not None:
                output["early_percent_move"] = early_move

            if not daily_hist.empty:
                high = daily_hist["High"][:-1].max()
                low = daily_hist["Low"][:-1].min()
                output.update({
                    "high": round(high, 2),
                    "low": round(low, 2),
                    "highlow_days": lookback_days
                })

            return output

        except Exception as e:
            if attempt < retries - 1:
                sleep_time = random.uniform(1.5, 3.5)
                tqdm.write(f"🔁 Retry {attempt + 1} for {symbol} after error: {e}")
                time.sleep(sleep_time)
            else:
                tqdm.write(f"❌ Failed for {symbol} after {retries} attempts: {e}")
                return None

def main():
    universe_path = get_latest_universe_file()
    with open(universe_path, "r") as f:
        universe = json.load(f)
    symbols = list(universe.keys())

    combined_output = {
        "timestamp": datetime.now().isoformat(),
        "tickers": {},
        "sectors": {}
    }

    print(f"📡 Fetching TV-style + YF enrichment + {LOOKBACK_DAYS}-day highs/lows for {len(symbols)} tickers...")

    for i, symbol in enumerate(tqdm(symbols, desc="🔄 Scraping Tickers")):
        data = fetch_yf_data(symbol, LOOKBACK_DAYS)
        if data:
            combined_output["tickers"][symbol] = data

        # Random delay to avoid rate limiting
        time.sleep(random.uniform(0.3, 0.6))

        # Save progress in batches
        if i > 0 and i % SAVE_INTERVAL == 0:
            save_progress(combined_output)

    print("📊 Fetching sector ETF prices...")
    for etf in SECTOR_ETFS:
        try:
            data = yf.Ticker(etf).info
            combined_output["sectors"][etf] = {
                "last_price": data.get("regularMarketPrice"),
                "prev_close": data.get("previousClose"),
                "pct_change": data.get("regularMarketChangePercent")
            }
        except Exception as e:
            tqdm.write(f"⚠️ Failed to fetch sector {etf}: {e}")

    save_progress(combined_output)
    print(f"✅ Final post-open signals saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
