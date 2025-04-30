# backend/daily_refresh.py

import subprocess
import sys
import os
from tqdm import tqdm
from datetime import datetime
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.cache_manager import cleanup_old_files, audit_cache_files, cleanup_old_universe_files

# --- Daily Refresh Tasks ---
tasks = [
    ("Build Universe", "backend/signals/universe_builder.py"),
    ("Scrape TV Signals", "backend/signals/scrape_tv_signals.py"),
    ("Scrape Sector ETF Prices", "backend/signals/scrape_sector_prices.py"),
    ("Scrape 5m Candles", "backend/signals/scraper_candles_5m.py"),
    ("Fetch Multi-Day High/Low", "backend/signals/fetch_multi.py"),
    ("Fetch Short Interest", "backend/signals/fetch_short_interest.py"),
]

print("\n🚀 Starting Daily Refresh...\n")

for desc, script_path in tqdm(tasks, desc="Running Daily Refresh", unit="task"):
    print(f"\n🔹 {desc}...")
    try:
        subprocess.run([sys.executable, script_path], check=True)
        print(f"✅ {desc} complete.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {script_path}: {e}")
        print(f"⚠️ {desc} failed. Continuing...")

# After all tasks...
cleanup_old_files()
cleanup_old_universe_files(days_to_keep=1)
audit_cache_files()

print("\n🎯 Daily Refresh Complete!")
