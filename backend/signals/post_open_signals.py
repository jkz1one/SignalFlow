## post_open_signals.py
import os
import json
import yfinance as yf
from datetime import datetime
from tqdm import tqdm

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

TODAY_STR = datetime.now().strftime("%Y-%m-%d")
OUTPUT_PATH = os.path.join(CACHE_DIR, f"post_open_signals_{TODAY_STR}.json")
LOOKBACK_DAYS = 10

SECTOR_ETFS = [
    "XLF", "XLK", "XLE", "XLV", "XLY",
    "XLI", "XLP", "XLU", "XLRE", "XLB", "XLC"
]

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

# --- Main Combined Scraper ---
def main():
    with open(UNIVERSE_PATH, "r") as f:
        universe = json.load(f)
    symbols = list(universe.keys())

    combined_output = {
        "timestamp": datetime.now().isoformat(),
        "tickers": {},
        "sectors": {}
    }

    print(f"📡 Fetching TV-style + YF enrichment + {LOOKBACK_DAYS}-day highs/lows for {len(symbols)} tickers...")

    for symbol in tqdm(symbols, desc="🔄 Scraping Tickers"):
        try:
            yf_symbol = symbol.replace(".", "-")  # Fix BRK.B -> BRK-B
            ticker = yf.Ticker(yf_symbol)

            # Get daily and intraday candles
            daily_hist = ticker.history(period=f"{LOOKBACK_DAYS + 1}d")
            intraday_hist = ticker.history(period="1d", interval="5m")

            # Relative volume
            rel_vol = None
            avg_volume_10d = None
            if not daily_hist.empty and len(daily_hist) >= 10:
                past_volumes = daily_hist['Volume'][:-1]
                avg_volume_10d = past_volumes.mean()
                today_volume = daily_hist['Volume'].iloc[-1]
                rel_vol = today_volume / avg_volume_10d if avg_volume_10d > 0 else 0

            # Early % move from 5m candles
            early_move = None
            if not intraday_hist.empty:
                early_candle = intraday_hist.between_time("09:30", "09:35")
                if not early_candle.empty:
                    early_open = early_candle['Open'].iloc[0]
                    early_close = early_candle['Close'].iloc[-1]
                    if early_open and early_close and early_open != 0:
                        early_move = round(((early_close - early_open) / early_open) * 100, 2)

            info = ticker.info
            combined_output["tickers"][symbol] = {
                "price": info.get("regularMarketPrice"),
                "volume": info.get("volume"),
                "changePercent": info.get("regularMarketChangePercent"),
                "open": info.get("open"),
                "prevClose": info.get("previousClose"),
                "timestamp": datetime.now().isoformat(),
            }

            if rel_vol is not None:
                combined_output["tickers"][symbol]["rel_vol"] = round(rel_vol, 2)
            if avg_volume_10d is not None:
                combined_output["tickers"][symbol]["avg_volume_10d"] = int(avg_volume_10d)
            if early_move is not None:
                combined_output["tickers"][symbol]["early_percent_move"] = early_move

            if not daily_hist.empty:
                high = daily_hist["High"][:-1].max()
                low = daily_hist["Low"][:-1].min()
                combined_output["tickers"][symbol].update({
                    "high": round(high, 2),
                    "low": round(low, 2),
                    "highlow_days": LOOKBACK_DAYS
                })

        except Exception as e:
            tqdm.write(f"⚠️ Failed for {symbol}: {e}")

    print(f"📊 Fetching sector ETF prices for: {', '.join(SECTOR_ETFS)}")

    for etf in SECTOR_ETFS:
        try:
            data = yf.Ticker(etf).info
            combined_output["sectors"][etf] = {
                "price": data.get("regularMarketPrice"),
                "prevClose": data.get("previousClose"),
                "changePercent": data.get("regularMarketChangePercent")
            }
        except Exception as e:
            tqdm.write(f"⚠️ Failed to fetch sector {etf}: {e}")

    # --- Save Unified Output ---
    with open(OUTPUT_PATH, "w") as f:
        json.dump(combined_output, f, indent=2)

    print(f"✅ Combined post-open signals (tickers + sectors) saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
