# backend/run_pipeline.py

import subprocess
import os
from datetime import datetime
import time  # <-- add this
from backend.cache_manager import validate_caches, cleanup_old_files

print("🔁 [1/4] Building base universe...")
subprocess.run(["python3", "backend/enrich_universe.py"], check=True)

# ✅ Wait a moment to ensure filesystem sync
time.sleep(1)

print("🔎 Validating cache files...")
validate_caches(strict=True, include_scored=False)  # Strict mode ON for prod

print("🧨 [2/4] Cleaning old cache files...")
result = cleanup_old_files()
print(f"🧹 Deleted: {result[0]} | Skipped: {result[1]}")

print("⚙️ [3/4] Scoring and saving autowatchlist output...")
subprocess.run(["python3", "-m", "backend.screenbuilder"], check=True)
from backend.watchlist_builder import build_autowatchlist

print("📋 [4/4] Building AutoWatchlist from scored universe...")
build_autowatchlist()

print("✅ Pipeline complete. Watchlist and cache updated.")
validate_caches(strict=True, include_scored=True)
print("🧨 Cleaning old cache files...")
result = cleanup_old_files()
print(f"🧹 Deleted: {result[0]} | Skipped: {result[1]}")
print("💯 Done.")