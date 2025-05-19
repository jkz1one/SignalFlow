## enrich_universe.py
import json
import os
from datetime import datetime
import pytz 
from pytz import timezone

# --- Setup ---
CACHE_DIR = "backend/cache"
GAP_THRESHOLD = 0.005  # 0.5% gap threshold (can be made dynamic later)


# --- Helpers ---
def load_json(path):
    if not os.path.exists(path):
        print(f"⚠️ Warning: Cache file missing: {path}")
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {path}: {e}")
        return {}

# --- Resolve Input Files ---
TODAY = datetime.now(timezone("US/Eastern")).strftime("%Y-%m-%d")

def get_latest_universe_file():
    files = []
    for f in os.listdir(CACHE_DIR):
        if f.startswith("universe_") and f.endswith(".json"):
            date_part = f[len("universe_"):-len(".json")]
            try:
                # validate YYYY-MM-DD format
                datetime.strptime(date_part, "%Y-%m-%d")
                files.append(f)
            except ValueError:
                continue
    if not files:
        raise FileNotFoundError("❌ No dated universe files found in cache.")
    files.sort(key=lambda f: os.path.getmtime(os.path.join(CACHE_DIR, f)), reverse=True)
    return os.path.join(CACHE_DIR, files[0])

UNIVERSE_PATH = get_latest_universe_file()
current_date_str = datetime.now(pytz.timezone("America/New_York")).strftime("%Y-%m-%d")
OUTPUT_PATH = os.path.join(CACHE_DIR, f"universe_enriched_{current_date_str}.json")
post_open = load_json(os.path.join(CACHE_DIR, f"post_open_signals_{TODAY}.json"))
candles = load_json(os.path.join(CACHE_DIR, f"945_signals_{TODAY}.json"))
tv_signals = post_open.get("tickers", {})  # derived from post_open_signals
sector_prices = post_open.get("sectors", {})

multi_day_data = {
    symbol: {
        "hi_10d": data.get("hi_10d"),
        "lo_10d": data.get("lo_10d")
    }
    for symbol, data in tv_signals.items()
    if data.get("hi_10d") is not None and data.get("lo_10d") is not None
}

def enrich_with_tv_signals(universe, tv_data):
    normalized_tv_data = {}
    for k, v in tv_data.items():
        base = k.split(".")[0].upper()
        normalized_tv_data[base] = v

    for symbol, info in universe.items():
        tv = normalized_tv_data.get(symbol.upper())
        if tv:
            signals = info.setdefault("signals", {})
            # Map data from post_open_signals to universe fields
            info.update({
                "pd_hi": tv.get("pd_hi"),
                "pd_lo": tv.get("pd_lo"),
                "last_price": tv.get("last_price"),
                "vol_latest": tv.get("vol_latest"),
                "pct_change": tv.get("pct_change"),
                "rel_vol": tv.get("rel_vol"),
                "avg_vol_10d": tv.get("avg_vol_10d"),
                "open_price": tv.get("open_price"),
                "prev_close": tv.get("prev_close"),
                "early_percent_move": tv.get("early_percent_move"),
                "shortPercentOfFloat": tv.get("shortPercentOfFloat"),
            })

            if abs(tv.get("early_percent_move", 0)) >= 2.5:
                signals["early_move"] = tv["early_percent_move"]

            # Import the existing squeeze_watch flag directly
            if tv.get("squeeze_watch"):
                signals["squeeze_watch"] = True

            # Tier 3: Near multi-day high / low
            if tv.get("near_multi_day_high"):
                signals["near_multi_day_high"] = True
            if tv.get("near_multi_day_low"):
                signals["near_multi_day_low"] = True

            # Import top volume gainer flag as well
            if tv.get("top_volume_gainer"):
                signals["top_volume_gainer"] = True

    return universe


def enrich_with_sector(universe, sector_data):
    for symbol, info in universe.items():
        sector = info.get("sector")
        if not sector:
            continue
        etf = sector_data.get(sector)
        if etf:
            info["sector_etf"] = etf
    return universe

def apply_sector_rotation_signals(universe, sector_data):
    SECTOR_ETFS = {
        "XLF": "Financial Services",
        "XLK": "Technology",
        "XLE": "Energy",
        "XLV": "Healthcare",
        "XLY": "Consumer Cyclical",
        "XLI": "Industrials",
        "XLP": "Consumer Defensive",
        "XLU": "Utilities",
        "XLRE": "Real Estate",
        "XLB": "Basic Materials",
        "XLC": "Communication Services"
    }

    # Reverse map for easier matching
    SECTOR_TO_ETF = {v: k for k, v in SECTOR_ETFS.items()}

    sector_changes = {}
    for etf, sector in SECTOR_ETFS.items():
        etf_info = sector_data.get(etf)
        if not etf_info:
            continue
        price = etf_info.get("last_price")
        prev_close = etf_info.get("prev_close")
        if price and prev_close:
            try:
                change = ((price - prev_close) / prev_close) * 100
                sector_changes[sector] = round(change, 2)
            except ZeroDivisionError:
                continue

    sorted_sectors = sorted(sector_changes.items(), key=lambda x: x[1], reverse=True)
    top_sectors = set(s for s, _ in sorted_sectors[:2])
    bottom_sectors = set(s for s, _ in sorted_sectors[-2:])

    for symbol, info in universe.items():
        sector = info.get("sector")
        if not sector:
            continue
        signals = info.setdefault("signals", {})
        if sector in top_sectors:
            signals["strong_sector"] = True
        elif sector in bottom_sectors:
            signals["weak_sector"] = True

    return universe

def enrich_with_candles(universe, candle_data):
    # The 945_signals output JSON has a top-level "candles" dict
    data = candle_data.get("candles", {}) if isinstance(candle_data, dict) else candle_data
    for symbol, info in universe.items():
        entry = data.get(symbol)
        if not entry:
            continue
        # If entry is a dict with range info
        if isinstance(entry, dict):
            high = entry.get("940_high")
            low = entry.get("940_low")
            if high is not None and low is not None:
                info["range_930_940_high"] = high
                info["range_930_940_low"] = low
        # If entry is a list of 5m candles (old format)
        elif isinstance(entry, list):
            highs = []
            lows = []
            for c in entry:
                high = c.get("high")
                low = c.get("low")
                if high is not None and low is not None:
                    highs.append(high)
                    lows.append(low)
            if highs and lows:
                info["range_930_940_high"] = max(highs)
                info["range_930_940_low"] = min(lows)
    return universe

def enrich_with_multi_day_levels(universe, multi_day_data):
    for symbol, info in universe.items():
        data = multi_day_data.get(symbol)
        if data and "hi_10d" in data and "lo_10d" in data:
            info["hi_10d"] = data["hi_10d"]
            info["lo_10d"] = data["lo_10d"]
    return universe

def enrich_with_short_interest(universe, tv_signals):
    """
    Pulls normalized tv_signals[symbol]["shortPercentOfFloat"] → universe[...]["shortPercentOfFloat"]
    and pre-flags squeeze_watch when criteria are met.
    """
    # Normalize tv_signals keys first (matching enrich_with_tv_signals)
    normalized_tv_data = {}
    for k, v in tv_signals.items():
        base = k.split(".")[0].upper()
        normalized_tv_data[base] = v

    flagged = 0
    for symbol, info in universe.items():
        tv = normalized_tv_data.get(symbol.upper(), {})
        sp = tv.get("shortPercentOfFloat")
        if sp is None:
            continue

        # Store shortPercentOfFloat in universe data
        info["shortPercentOfFloat"] = sp

        rel_vol = info.get("rel_vol", 0)
        pct_change = abs(info.get("pct_change", 0))

        # Debugging output
        print(f"🔍 {symbol}: short%={sp:.3f}, rel_vol={rel_vol:.2f}, pct_change={pct_change:.2f}%")

        # Squeeze Watch logic
        if sp >= 0.1 and rel_vol > 1.0 and pct_change >= 1.0:
            signals = info.setdefault("signals", {})
            signals["squeeze_watch"] = True
            flagged += 1
            print(f"🚩 Squeeze Watch flagged: {symbol}")

    print(f"📌 Total Squeeze Watch flags set: {flagged}")
    return universe

# apply_signal_flags
def apply_signal_flags(universe):
    post_open_signals = post_open.get("tickers", {})
    for symbol, info in universe.items():
        signals = info.setdefault("signals", {})
        open_price = info.get("open_price")
        prev_close = info.get("prev_close")
        last_price = info.get("last_price")
        high = info.get("range_930_940_high")
        low = info.get("range_930_940_low")
        vol_latest = info.get("vol_latest", 0)
        avg_vol_10d = info.get("avg_vol_10d", 0)
        post = post_open_signals.get(symbol, {})
        pd_hi = post.get("pd_hi")
        pd_lo = post.get("pd_lo")

        # Initialize tierHits and reasons
        info.setdefault("tierHits", {"T1": [], "T2": [], "T3": []})
        info.setdefault("reasons", [])

        # --- Tier 1: Gap Up / Gap Down ---


        if open_price is not None:
            if pd_hi is not None and open_price > pd_hi:
                signals["gap_up"] = True
                info["tierHits"]["T1"].append("gap_up")
                info["reasons"].append("T1: gap_up")
            elif pd_lo is not None and open_price < pd_lo:
                signals["gap_down"] = True
                info["tierHits"]["T1"].append("gap_down")
                info["reasons"].append("T1: gap_down")


        # --- Tier 1: Break Above/Below 9:30–9:40 Range ---
        if last_price is not None and high is not None and last_price > high:
            signals["break_above_range"] = True
            info["tierHits"]["T1"].append("break_above_range")
            info["reasons"].append("T1: break_above_range")

        if last_price is not None and low is not None and last_price < low:
            signals["break_below_range"] = True
            info["tierHits"]["T1"].append("break_below_range")
            info["reasons"].append("T1: break_below_range")

        # --- Tier 1: High Relative Volume ---
        if info.get("rel_vol", 0) > 1.5:
            signals["high_rel_vol"] = True
            info["tierHits"]["T1"].append("high_rel_vol")
            info["reasons"].append("T1: high_rel_vol")

        # --- Tier 2: Early % Move ---
        if abs(post.get("early_percent_move", 0)) >= 2.5:
            signals["early_move"] = post["early_percent_move"]
            info["tierHits"]["T2"].append("early_move")
            info["reasons"].append("T2: early_move")

        # --- Tier 2: Squeeze Watch ---
        if info.get("signals", {}).get("squeeze_watch"):
            info["tierHits"]["T2"].append("squeeze_watch")
            info["reasons"] .append("T2: squeeze_watch")

        # --- Tier 2: Sector Rotation ---
        if signals.get("strong_sector"):
            info["tierHits"]["T2"].append("strong_sector")
            info["reasons"].append("T2: strong_sector")
        if signals.get("weak_sector"):
            info["tierHits"]["T2"].append("weak_sector")
            info["reasons"].append("T2: weak_sector")

        # --- Tier 3: High Volume ---
        if avg_vol_10d and vol_latest >= avg_vol_10d * 2:
            signals["high_volume"] = True
            info["tierHits"]["T3"].append("high_volume")
            info["reasons"].append("T3: high_volume")

        # --- Tier 3: Top 5 Volume Gainers ---
        if vol_latest >= 1000000:  # Example volume threshold for top gainers
            signals["top_volume_gainer"] = True
            info["tierHits"]["T3"].append("top_volume_gainer")
            info["reasons"].append("T3: top_volume_gainer")

        # --- Tier 3: Near Multi-Day High/Low ---
        if last_price and info.get("hi_10d") and last_price >= info["hi_10d"] * 0.98:
            signals["near_multi_day_high"] = True
            info["tierHits"]["T3"].append("near_multi_day_high")
            info["reasons"].append("T3: near_multi_day_high")

        if last_price and info.get("lo_10d") and last_price <= info["lo_10d"] * 1.02:
            signals["near_multi_day_low"] = True
            info["tierHits"]["T3"].append("near_multi_day_low")
            info["reasons"].append("T3: near_multi_day_low")

        # --- Tier 3: High Volume, No Breakout ---
        if (
            last_price is not None and high is not None and low is not None and
            low * 0.99 <= last_price <= high * 1.01 and
            not signals.get("break_above_range") and
            not signals.get("break_below_range") and
            (high - low) / low < 0.02
        ):
            signals["high_volume_no_breakout"] = True
            info["tierHits"]["T3"].append("high_volume_no_breakout")
            info["reasons"].append("T3: high_volume_no_breakout")

    return universe


def flag_top_volume_gainers(universe, top_n=5):
    sorted_tickers = sorted(
        universe.items(),
        key=lambda x: x[1].get("vol_latest") or 0,
        reverse=True
    )
    for symbol, info in sorted_tickers[:top_n]:
        info.setdefault("signals", {})["top_volume_gainer"] = True
    return universe

def inject_risk_flags(universe):
    for symbol, info in universe.items():
        vol = info.get("avg_volume")
        spread = info.get("spread")
        if vol is not None and vol < 500_000:
            info.setdefault("signals", {})["low_liquidity"] = True
        if spread is not None and spread > 0.30:
            info.setdefault("signals", {})["wide_spread"] = True
    return universe

def main():
    print(f"📥 Loading base universe: {UNIVERSE_PATH}")
    universe = load_json(UNIVERSE_PATH)

    if not universe:
        print("❌ No tickers found in base universe. Aborting enrichment.")
        return

    print("🚀 Starting enrichment...")
    print(f"📦 Loaded {len(universe)} tickers")

    try:
        universe = enrich_with_tv_signals(universe, tv_signals)
    except Exception as e:
        print(f"⚠️ Error enriching with TV signals: {e}")

    try:
        universe = enrich_with_sector(universe, sector_prices)
        universe = apply_sector_rotation_signals(universe, sector_prices)
    except Exception as e:
        print(f"⚠️ Error enriching with sector signals: {e}")

    try:
        universe = enrich_with_candles(universe, candles)
    except Exception as e:
        print(f"⚠️ Error enriching with candles: {e}")

    try:
        universe = enrich_with_multi_day_levels(universe, multi_day_data)
    except Exception as e:
        print(f"⚠️ Error enriching multi-day levels: {e}")

    # Final processing
    universe = flag_top_volume_gainers(universe)
    try:
        universe = apply_signal_flags(universe)
    except Exception as e:
        print(f"⚠️ Error applying signal flags: {e}")

    universe = inject_risk_flags(universe)

    # Timestamp and save
    eastern = timezone('America/New_York')
    now_eastern = datetime.now(eastern).isoformat()
    for info in universe.values():
        info.pop("yfinance_updated", None)
        info["enriched_timestamp"] = now_eastern

    # Summary
    t2_hits = sum(1 for x in universe.values() if x.get("tierHits", {}).get("T2"))
    t3_hits = sum(1 for x in universe.values() if x.get("tierHits", {}).get("T3"))
    print(f"✅ Tier 2 hits: {t2_hits}, Tier 3 hits: {t3_hits}")

    with open(OUTPUT_PATH, "w") as f:
        json.dump(universe, f, indent=2)
    print(f"✅ Enriched universe saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()