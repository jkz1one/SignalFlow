# backend/run_pipeline.py

import subprocess
import os
from datetime import datetime
import time  # <-- add this

print("🔁 [1/4] Building base universe...")
subprocess.run(["python3", "backend/enrich_universe.py"], check=True)

# ✅ Wait a moment to ensure filesystem sync
time.sleep(1)

def check_required_cache():
    today = datetime.now().strftime("%Y-%m-%d")
    CACHE_DIR = "backend/cache"
    required_files = [
        f"tv_signals.json",
        f"sector_etf_prices.json",
        f"candles_5m.json",
        f"multi_day_levels.json",
        f"short_interest.json",
        f"universe_{today}.json"
    ]
    missing = []
    for fname in required_files:
        if not os.path.exists(os.path.join(CACHE_DIR, fname)):
            missing.append(fname)

    if missing:
        print("\n❌ Missing or outdated cache files detected:")
        for m in missing:
            print(f" - {m}")
        raise SystemExit("\n🛑 Aborting pipeline! Refresh data or debug enrich.\n")

print("🔎 Verifying cache/enrich freshness ...")
check_required_cache()

print("🧨 [2/4] Cleaning cache...")
subprocess.run(["python3", "backend/cache_manager.py"], check=True)

print("⚙️ [3/4] Scoring and saving autowatchlist output...")
subprocess.run(["python3", "-m", "backend.screenbuilder"], check=True)
from backend.watchlist_builder import build_autowatchlist

print("📋 [4/4] Building AutoWatchlist from scored universe...")
build_autowatchlist()

print("✅ Pipeline complete. Watchlist and cache updated.")
