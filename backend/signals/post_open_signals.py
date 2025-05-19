import os
import json
import time
import random
from datetime import datetime
from tqdm import tqdm
import yfinance as yf
import pandas as pd

# --- Paths & Config ---
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

SQUEEZE_SHORT_PCT_THRESH = 0.20
SQUEEZE_REL_VOL_THRESH   = 1.20
SQUEEZE_PCT_MOVE_THRESH  = 1.00

TODAY_STR = datetime.now().strftime("%Y-%m-%d")
OUTPUT_PATH = os.path.join(CACHE_DIR, f"post_open_signals_{TODAY_STR}.json")
LOOKBACK_DAYS = 10
SECTOR_ETFS = [
    "XLF", "XLK", "XLE", "XLV", "XLY",
    "XLI", "XLP", "XLU", "XLRE", "XLB", "XLC"
]
BATCH_SIZE = 100


def get_latest_universe_file():
    files = [
        f for f in os.listdir(CACHE_DIR)
        if f.startswith("universe_") and f.endswith(".json")
        and "cache" not in f and "enriched" not in f and "scored" not in f
    ]
    if not files:
        raise FileNotFoundError("❌ No valid universe files found in cache.")
    files.sort(key=lambda f: os.path.getmtime(os.path.join(CACHE_DIR, f)), reverse=True)
    return os.path.join(CACHE_DIR, files[0])


def chunked(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i:i+size]


def fetch_batch_data(symbols):
    out = {}
    sym_map = {s: s.replace(".", "-") for s in symbols}

    daily = yf.download(
        tickers=list(sym_map.values()),
        period=f"{LOOKBACK_DAYS + 1}d",
        interval="1d",
        group_by="ticker",
        threads=True
    )

    intraday = yf.download(
        tickers=list(sym_map.values()),
        period="1d",
        interval="5m",
        group_by="ticker",
        threads=True
    )

    for raw_sym, yf_sym in sym_map.items():
        result = {}
        d_df = daily.get(yf_sym, pd.DataFrame())
        i_df = intraday.get(yf_sym, pd.DataFrame())

        # Early move 9:30–9:35
        if i_df is not None and not i_df.empty:
            early = i_df.between_time("09:30", "09:35")
            if not early.empty:
                o = early["Open"].iloc[0]
                c = early["Close"].iloc[-1]
                if o:
                    result["early_percent_move"] = round((c - o) / o * 100, 2)

        # Volume & high/low lookback
        if d_df is not None and not d_df.empty and len(d_df) >= LOOKBACK_DAYS:
            past_vols = d_df["Volume"][:-1]
            today_vol = d_df["Volume"].iloc[-1]
            avg_vol = past_vols.mean()
            result["rel_vol"] = round(today_vol / avg_vol, 2) if avg_vol else None
            result["avg_vol_10d"] = int(avg_vol)

            result["hi_10d"] = round(d_df["High"][:-1].max(), 2)
            result["lo_10d"] = round(d_df["Low"][:-1].min(), 2)

            if len(d_df) >= 2:
                result["pd_hi"] = round(d_df["High"].iloc[-2], 2)
                result["pd_lo"] = round(d_df["Low"].iloc[-2], 2)

        # YFinance info (including short interest)
        try:
            q = yf.Ticker(yf_sym)
            info = q.info
            result.update({
                "last_price": info.get("regularMarketPrice"),
                "vol_latest": info.get("volume"),
                "pct_change": info.get("regularMarketChangePercent"),
                "open_price": info.get("open"),
                "prev_close": info.get("previousClose"),
                "shortPercentOfFloat": info.get("shortPercentOfFloat"),
                "timestamp": datetime.now().isoformat(),
            })
        except Exception as e:
            tqdm.write(f"⚠️ Failed info lookup for {raw_sym}: {e}")
            result["timestamp"] = datetime.now().isoformat()

        out[raw_sym] = result

    return out


def main():
    universe = json.load(open(get_latest_universe_file()))
    symbols = list(universe.keys())

    combined_output = {
        "timestamp": datetime.now().isoformat(),
        "tickers": {},
        "sectors": {}
    }

    # Sector ETF snapshot
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

    # Ticker batches
    print(f"📡 Fetching post-open signals for {len(symbols)} tickers in batches...")
    for batch in tqdm(list(chunked(symbols, BATCH_SIZE)), desc="🔄 Batching"):
        batch_data = fetch_batch_data(batch)
        for sym, data in batch_data.items():
            if not data:
                continue

            # Tier 2: squeeze watch
            sp = data.get("shortPercentOfFloat") or 0
            rv = data.get("rel_vol")           or 0
            pc = data.get("pct_change")        or 0

            if (
                sp  >= SQUEEZE_SHORT_PCT_THRESH
                and rv >  SQUEEZE_REL_VOL_THRESH
                and abs(pc) >= SQUEEZE_PCT_MOVE_THRESH
            ):
                data["squeeze_watch"] = True

            # Tier 3: near multi-day high/low
            price = data.get("last_price")
            if price and data.get("hi_10d") and price >= data["hi_10d"] * 0.98:
                data["near_multi_day_high"] = True
            if price and data.get("lo_10d") and price <= data["lo_10d"] * 1.02:
                data["near_multi_day_low"] = True

            combined_output["tickers"][sym] = data
        time.sleep(random.uniform(0.5, 1.2))

    # Top-5 volume gainers
    top5 = sorted(
        combined_output["tickers"].items(),
        key=lambda kv: kv[1].get("vol_latest", 0),
        reverse=True
    )[:5]
    for sym, _ in top5:
        combined_output["tickers"][sym]["top_volume_gainer"] = True

    # Write output
    with open(OUTPUT_PATH, "w") as f:
        json.dump(combined_output, f, indent=2)
    print(f"✅ Saved post-open signals to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
