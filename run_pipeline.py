# backend/run_pipeline.py

import subprocess
import os
from datetime import datetime
import time  # <-- add this

print("🔁 [1/4] Building base universe...")
subprocess.run(["python3", "backend/enrich_universe.py"], check=True)

# ✅ Wait a moment to ensure filesystem sync
time.sleep(1)

print("🧨 [2/4] Cleaning cache...")
subprocess.run(["python3", "backend/cache_manager.py"], check=True)

print("⚙️ [3/4] Scoring and saving autowatchlist output...")
subprocess.run(["python3", "-m", "backend.screenbuilder"], check=True)
from backend.watchlist_builder import build_autowatchlist

print("📋 [4/4] Building AutoWatchlist from scored universe...")
build_autowatchlist()

print("✅ Pipeline complete. Watchlist and cache updated.")
