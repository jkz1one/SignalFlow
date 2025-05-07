import json
import os
from datetime import datetime
import pytz 
from pytz import timezone
from tqdm import tqdm
from collections import defaultdict

# --- Setup ---
CACHE_DIR = "backend/cache"

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
    files = [
        f for f in os.listdir(CACHE_DIR)
        if f.startswith("universe_") and f.endswith(".json") and "cache" not in f
    ]
    if not files:
        raise FileNotFoundError("❌ No dated universe files found in cache.")
    files.sort(key=lambda f: os.path.getmtime(os.path.join(CACHE_DIR, f)), reverse=True)
    return os.path.join(CACHE_DIR, files[0])

UNIVERSE_PATH = get_latest_universe_file()
current_date_str = datetime.now(pytz.timezone("America/New_York")).strftime("%Y-%m-%d")
OUTPUT_PATH = os.path.join(CACHE_DIR, f"universe_enriched_{current_date_str}.json")

ENRICHED_PATH = os.path.join(CACHE_DIR, f"universe_enriched_{TODAY}.json")
if os.path.exists(ENRICHED_PATH):
    print(f"📥 Loading previously enriched file: {ENRICHED_PATH}")
    universe = load_json(ENRICHED_PATH)
else:
    print(f"📥 No prior enriched file found. Using base universe: {UNIVERSE_PATH}")
    universe = load_json(UNIVERSE_PATH)

post_open = load_json(os.path.join(CACHE_DIR, f"post_open_signals_{TODAY}.json"))
candles = load_json(os.path.join(CACHE_DIR, f"945_signals_{TODAY}.json"))
short_interest = load_json(os.path.join(CACHE_DIR, "short_interest.json"))

tv_signals = post_open.get("tickers", {})  # derived from post_open_signals
sector_prices = post_open.get("sectors", {})

multi_day_data = {
    symbol: {
        "high": data.get("high"),
        "low": data.get("low")
    }
    for symbol, data in tv_signals.items()
    if data.get("high") is not None and data.get("low") is not None
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
            if "last_price" in tv:
                info["last_price"] = tv["last_price"]
            if "vol_latest" in tv:
                info["vol_latest"] = tv["vol_latest"]
            if "pct_change" in tv:
                info["pct_change"] = tv["pct_change"]
            if "rel_vol" in tv:
                info["rel_vol"] = tv["rel_vol"]
            if "avg_vol_10d" in tv:
                info["avg_vol_10d"] = tv["avg_vol_10d"]
            if "open_price" in tv:
                info["open_price"] = tv["open_price"]
            if "prev_close" in tv:
                info["prev_close"] = tv["prev_close"]
            if "early_percent_move" in tv:
                info["early_percent_move"] = tv["early_percent_move"]
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
        if data and "high" in data and "low" in data:
            info["high_10d"] = data["high"]
            info["low_10d"] = data["low"]
    return universe

def enrich_with_short_interest(universe, short_data):
    for symbol, info in universe.items():
        si = short_data.get(symbol.upper())
        rel_vol = info.get("rel_vol", 0)
        change = info.get("pct_change", 0)

        if si:
            short_pct = si.get("shortPercentOfFloat", 0)
            if (
                short_pct >= 0.18 and
                rel_vol > 1.2 and
                abs(change) >= 1.5
            ):
                info.setdefault("signals", {})["squeeze_watch"] = True
    return universe

def apply_signal_flags(universe):
    # Load once and extract "tickers" for signal lookup
    post_open = load_json(os.path.join(CACHE_DIR, f"post_open_signals_{TODAY}.json"))
    post_open_signals = post_open.get("tickers", {})

    for symbol, info in universe.items():
        signals = info.setdefault("signals", {})
        price = info.get("last_price")
        volume = info.get("vol_latest")
        change = info.get("pct_change")
        open_price = info.get("open_price")
        prev_close = info.get("prev_close")
        high = info.get("range_930_940_high")
        low = info.get("range_930_940_low")

        info.setdefault("tierHits", {"T1": [], "T2": [], "T3": []})
        info.setdefault("reasons", [])
        score = info.get("score", 0)

        # --- Tier 1 signals ---
        if open_price is not None and prev_close is not None:
            if open_price > prev_close * 1.01:
                signals["gap_up"] = True
                info["tierHits"]["T1"].append("gap_up")
                info["reasons"].append("T1: gap_up")
                score += 3
            elif open_price < prev_close * 0.99:
                signals["gap_down"] = True
                info["tierHits"]["T1"].append("gap_down")
                info["reasons"].append("T1: gap_down")
                score += 3

        if price is not None and high is not None and price > high:
            signals["break_above_range"] = True
            info["tierHits"]["T1"].append("break_above_range")
            info["reasons"].append("T1: break_above_range")
            score += 3

        if price is not None and low is not None and price < low:
            signals["break_below_range"] = True
            info["tierHits"]["T1"].append("break_below_range")
            info["reasons"].append("T1: break_below_range")
            score += 3

        if info.get("rel_vol", 0) > 1.5:
            signals["high_rel_vol"] = True
            info["tierHits"]["T1"].append("high_rel_vol")
            info["reasons"].append("T1: high_rel_vol")
            score += 3

        # --- Raw supporting signals ---
        if volume is not None and volume >= 1_000_000:
            signals["high_volume"] = True
        if price is not None and high is not None and 0 < (high - price) <= 0.25:
            signals["near_range_high"] = True
        if price is not None and low is not None and 0 < (price - low) <= 0.25:
            signals["near_range_low"] = True
        if price is not None and info.get("high_10d") and price >= info["high_10d"] * 0.98:
            signals["near_multi_day_high"] = True
        if price is not None and info.get("low_10d") and price <= info["low_10d"] * 1.02:
            signals["near_multi_day_low"] = True
        if (
            volume is not None and volume >= 800_000 and
            info.get("rel_vol", 0) > 1.0 and
            high is not None and low is not None and
            price is not None and
            low * 0.99 <= price <= high * 1.01 and
            not signals.get("break_above_range") and
            not signals.get("break_below_range") and
            (high - low) / low < 0.02
        ):
            signals["high_volume_no_breakout"] = True

        # --- Tier 2 & 3 from post_open_signals ---
        post = post_open_signals.get(symbol, {})

        if post.get("squeeze_watch"):
            signals["squeeze_watch"] = True
            info["tierHits"]["T2"].append("squeeze_watch")
            info["reasons"].append("T2: squeeze_watch")
            score += 2

        if abs(post.get("early_percent_move", 0)) >= 2.5:
            signals["early_move"] = post["early_percent_move"]
            info["tierHits"]["T2"].append("early_move")
            info["reasons"].append("T2: early_move")
            score += 2

        # Apply sector rotation signals to Tier 2
        if signals.get("strong_sector"):
            info["tierHits"]["T2"].append("strong_sector")
            info["reasons"].append("T2: strong_sector")
            score += 2
        if signals.get("weak_sector"):
            info["tierHits"]["T2"].append("weak_sector")
            info["reasons"].append("T2: weak_sector")
            score += 2

        if post.get("top_volume_gainer"):
            signals["top_volume_gainer"] = True
            info["tierHits"]["T3"].append("top_volume_gainer")
            info["reasons"].append("T3: top_volume_gainer")
            score += 1

        if post.get("near_multi_day_high"):
            signals["near_multi_day_high"] = True
            info["tierHits"]["T3"].append("near_multi_day_high")
            info["reasons"].append("T3: near_multi_day_high")
            score += 1

        if post.get("near_multi_day_low"):
            signals["near_multi_day_low"] = True
            info["tierHits"]["T3"].append("near_multi_day_low")
            info["reasons"].append("T3: near_multi_day_low")
            score += 1

        # Tier 3 raw signals
        if signals.get("near_range_high"):
            info["tierHits"]["T3"].append("near_range_high")
            info["reasons"].append("T3: near_range_high")
            score += 1
        if signals.get("high_volume"):
            info["tierHits"]["T3"].append("high_volume")
            info["reasons"].append("T3: high_volume")
            score += 1
        if signals.get("high_volume_no_breakout"):
            info["tierHits"]["T3"].append("high_volume_no_breakout")
            info["reasons"].append("T3: high_volume_no_breakout")
            score += 1

        # Final score
        info["score"] = score

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
    universe = {}

    if os.path.exists(ENRICHED_PATH):
        print(f"📥 Loading previously enriched file: {ENRICHED_PATH}")
        universe = load_json(ENRICHED_PATH)
    elif os.path.exists(UNIVERSE_PATH):
        print(f"📥 No prior enriched file found. Using base universe: {UNIVERSE_PATH}")
        universe = load_json(UNIVERSE_PATH)
    else:
        print("❌ No universe file available to load.")
        return

    print("🚀 Starting enrichment...")
    if not universe:
        print("❌ No tickers found in base universe. Aborting enrichment.")
        return

    print(f"📦 Loaded {len(universe)} tickers")

    if tv_signals:
        universe = enrich_with_tv_signals(universe, tv_signals)
    else:
        print("⚠️ Skipping TV signals – not available yet.")

    if sector_prices:
        universe = enrich_with_sector(universe, sector_prices)
        universe = apply_sector_rotation_signals(universe, sector_prices)
    else:
        print("⚠️ Skipping sector signals – not available yet.")

    if candles:
        universe = enrich_with_candles(universe, candles)
    else:
        print("⚠️ Skipping 9:30–9:40 range enrichment – no candle data yet.")

    if multi_day_data:
        universe = enrich_with_multi_day_levels(universe, multi_day_data)
    else:
        print("⚠️ Skipping multi-day high/low enrichment – data missing.")

    if short_interest:
        universe = enrich_with_short_interest(universe, short_interest)
    else:
        print("⚠️ Skipping short interest enrichment – data missing.")

    # Always apply signal flags and final processing
    universe = apply_signal_flags(universe)
    universe = flag_top_volume_gainers(universe)
    universe = inject_risk_flags(universe)

    # Timestamp
    eastern = timezone('America/New_York')
    now_eastern = datetime.now(eastern)
    for symbol, info in universe.items():
        info.pop("yfinance_updated", None)
        info["enriched_timestamp"] = now_eastern.isoformat()

    t2_hits = sum(1 for x in universe.values() if x["tierHits"]["T2"])
    t3_hits = sum(1 for x in universe.values() if x["tierHits"]["T3"])
    print(f"✅ Tier 2 hits: {t2_hits}, Tier 3 hits: {t3_hits}")

    with open(OUTPUT_PATH, "w") as f:
        json.dump(universe, f, indent=2)

    print(f"✅ Enriched universe saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
