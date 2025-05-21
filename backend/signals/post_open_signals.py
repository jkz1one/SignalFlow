## post_open_signals.py
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

# --- Data Source Toggle ---
USE_BATCH_DOWNLOAD = False  # True = use yf.download, False = use Ticker().history

# --- Squeeze Watch Thresholds ---
SQUEEZE_SHORT_THRESH = 0.20     # e.g. 20% short interest
SQUEEZE_REL_VOL_THRESH = 1.20   # e.g. 1.2x relative volume
SQUEEZE_PCT_MOVE_THRESH = 1.00  # e.g. 1.0% price move

# --- Sector ETF Config ---
SECTOR_ETFS = [
    "XLF", "XLK", "XLE", "XLV", "XLY",
    "XLI", "XLP", "XLU", "XLRE", "XLB", "XLC"
]

def get_latest_universe_file():
    files = [
        f for f in os.listdir(CACHE_DIR)
        if (
            f.startswith("universe_")
            and f.endswith(".json")
            and "cache" not in f
            and "enriched" not in f
            and "scored" not in f
        )
    ]
    if not files:
        raise FileNotFoundError("❌ No valid universe files found in cache.")
    files.sort(key=lambda f: os.path.getmtime(os.path.join(CACHE_DIR, f)), reverse=True)
    return os.path.join(CACHE_DIR, files[0])

def fetch_yf_data(symbol, lookback_days=10, retries=3):
    yf_symbol = symbol.replace(".", "-")
    for attempt in range(retries):
        try:
            ticker = yf.Ticker(yf_symbol)

            if USE_BATCH_DOWNLOAD:
                try:
                    daily_hist = yf.download(yf_symbol, period=f"{lookback_days + 1}d", interval="1d")
                except Exception as e:
                    tqdm.write(f"⚠️ Failed daily download for {symbol}: {e}")
                    daily_hist = None

                try:
                    intraday_hist = yf.download(yf_symbol, period="1d", interval="5m")
                except Exception as e:
                    tqdm.write(f"⚠️ Failed intraday download for {symbol}: {e}")
                    intraday_hist = None
            else:
                daily_hist = ticker.history(period=f"{lookback_days + 1}d", interval="1d")
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
                "shortPercentOfFloat": (
                    round(info.get("shortPercentOfFloat", 0), 4)
                    if isinstance(info.get("shortPercentOfFloat"), (int, float))
                    else None
                ),
                "timestamp": datetime.now().isoformat(),
            }

            if rel_vol is not None:
                output["rel_vol"] = round(rel_vol, 2)
            if avg_vol_10d is not None:
                output["avg_vol_10d"] = int(avg_vol_10d)
            if early_move is not None:
                output["early_percent_move"] = early_move

            if not daily_hist.empty:
                output["hi_10d"] = round(daily_hist["High"][:-1].max(), 2)
                output["lo_10d"] = round(daily_hist["Low"][:-1].min(), 2)
                if len(daily_hist) >= 2:
                    output["pd_hi"] = round(daily_hist["High"].iloc[-2], 2)
                    output["pd_lo"] = round(daily_hist["Low"].iloc[-2], 2)

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

    # ✅ Print the data mode being used
    print(f"📥 Mode: {'yf.download()' if USE_BATCH_DOWNLOAD else 'Ticker().history()'}")

    combined_output = {
        "timestamp": datetime.now().isoformat(),
        "tickers": {},
        "sectors": {}
    }

    print("📊 Fetching sector ETF prices...")
    for etf in SECTOR_ETFS:
        try:
            data = yf.Ticker(etf).info
            combined_output["sectors"][etf] = {
                "last_price": data.get("regularMarketPrice"),
                "prev_close": data.get("previousClose"),
                "changePercent": data.get("regularMarketChangePercent")
            }
        except Exception as e:
            tqdm.write(f"⚠️ Failed to fetch sector {etf}: {e}")

    print(f"📡 Fetching post-open signals + highs/lows for {len(symbols)} tickers...")
    for symbol in tqdm(symbols, desc="🔄 Scraping Tickers"):
        data = fetch_yf_data(symbol, LOOKBACK_DAYS)
        if not data:
            continue

        # Tier 2: squeeze watch
        short_pct = data.get("shortPercentOfFloat")
        rel_vol = data.get("rel_vol") or 0
        pct_change = data.get("pct_change")
        if (
            short_pct is not None
            and pct_change is not None
            and short_pct >= SQUEEZE_SHORT_THRESH
            and rel_vol > SQUEEZE_REL_VOL_THRESH
            and abs(pct_change) >= SQUEEZE_PCT_MOVE_THRESH
        ):
            data["squeeze_watch"] = True

        # Tier 3: near multi-day high/low
        price = data.get("last_price")
        if price and data.get("hi_10d") and price >= data["hi_10d"] * 0.98:
            data["near_multi_day_hi_10d"] = True
        if price and data.get("lo_10d") and price <= data["lo_10d"] * 1.02:
            data["near_multi_day_lo_10d"] = True

        combined_output["tickers"][symbol] = data
        time.sleep(random.uniform(0.3, 0.6))

    # Tier 3: top-5 volume gainers
    top5 = sorted(
        combined_output["tickers"].items(),
        key=lambda kv: kv[1].get("vol_latest", 0),
        reverse=True
    )[:5]
    for sym, _ in top5:
        combined_output["tickers"][sym]["top_volume_gainer"] = True

    # Single final write
    with open(OUTPUT_PATH, "w") as f:
        json.dump(combined_output, f, indent=2)
    print(f"✅ Final post-open signals saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()