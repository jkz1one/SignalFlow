##cache_manager.py

import os
import json
import time
from datetime import datetime, timedelta
import re
import glob
import pandas_market_calendars as mcal

# --- Config ---
CACHE_DIR = "backend/cache"
IMPORTANT_FILES = [
    "945_signals",
    "short_interest.json",
    "post_open_signals",
    "universe_enriched"
]


# --- Market Calendar ---
def get_last_market_day():
    nyse = mcal.get_calendar("XNYS")
    today = datetime.now().date()
    schedule = nyse.schedule(start_date=today - timedelta(days=7), end_date=today)
    return schedule.index[-1].date()

TODAY = get_last_market_day()

# --- Utility ---
def is_today(file_path):
    basename = os.path.basename(file_path)
    match = re.search(r"_(\d{4}-\d{2}-\d{2})\.json$", basename)
    if match:
        file_date_str = match.group(1)
        try:
            file_date = datetime.strptime(file_date_str, "%Y-%m-%d").date()
            return file_date == TODAY
        except ValueError:
            pass
    try:
        modified_time = os.path.getmtime(file_path)
        file_date = datetime.fromtimestamp(modified_time).date()
        return file_date == TODAY
    except Exception:
        return False

# --- Cleanup Functions ---
def cleanup_old_files():
    print("\U0001F9F9 Starting Cache Cleanup...")

    deleted_count = 0
    skipped_count = 0
    today_str = TODAY.strftime("%Y-%m-%d")

    for base_name in IMPORTANT_FILES:
        candidates = [
            os.path.join(CACHE_DIR, fname)
            for fname in os.listdir(CACHE_DIR)
            if fname.startswith(base_name)
        ]

        if base_name in ("universe_enriched", "universe_scored"):
            for path in candidates:
                if today_str not in os.path.basename(path):
                    try:
                        os.remove(path)
                        deleted_count += 1
                        print(f"\U0001F5D1️ Deleted old cache file: {os.path.basename(path)}")
                    except Exception as e:
                        print(f"⚠️ Error deleting {path}: {e}")
            continue

        found_today = any(is_today(p) for p in candidates)
        if found_today:
            for path in candidates:
                if not is_today(path):
                    try:
                        os.remove(path)
                        deleted_count += 1
                        print(f"\U0001F5D1️ Deleted old cache file: {os.path.basename(path)}")
                    except Exception as e:
                        print(f"⚠️ Error deleting {path}: {e}")
        else:
            skipped_count += 1
            print(f"⚠️ No fresh {base_name} file today. Skipping delete.")

    print(f"✅ Cache cleanup complete: {deleted_count} files deleted, {skipped_count} skipped.\n")
    return deleted_count, skipped_count

def cleanup_old_universe_files():
    print("\n\U0001F9F9 Cleaning Up Old Universe Files (Keep Only Today)...")

    today_str = TODAY.strftime("%Y-%m-%d")
    universe_files = glob.glob(os.path.join(CACHE_DIR, "universe_*.json"))
    universe_files = [f for f in universe_files if today_str not in f and "universe_cache.json" not in f]

    deleted = 0
    for path in universe_files:
        try:
            os.remove(path)
            print(f"\U0001F5D1️ Deleted: {os.path.basename(path)}")
            deleted += 1
        except Exception as e:
            print(f"⚠️ Failed to delete {path}: {e}")

    print(f"✅ Cleanup complete — {deleted} old universe files deleted.\n")
    return deleted

# --- Audit Function ---
def audit_cache_files():
    print("🔍 Starting Cache Audit...")

    issues_found = False

    def check_json(path, expected_keys, label):
        nonlocal issues_found
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
            missing = [k for k in expected_keys if k not in data]
            if missing:
                print(f"⚠️ Missing keys in {label}: {missing}")
                issues_found = True
        else:
            print(f"⚠️ {label} missing!")
            issues_found = True

    # Unified post_open_signals
    post_path = os.path.join(CACHE_DIR, f"post_open_signals_{TODAY.strftime('%Y-%m-%d')}.json")
    if os.path.exists(post_path):
        with open(post_path, "r") as f:
            data = json.load(f)
        if "tickers" not in data or "sectors" not in data:
            print(f"⚠️ Missing top-level keys in post_open_signals")
            issues_found = True
        elif len(data["tickers"]) < 10:
            print(f"⚠️ Unusually small ticker set in post_open_signals ({len(data['tickers'])})")
            issues_found = True
    else:
        print("⚠️ post_open_signals file is missing!")
        issues_found = True

    # Candles
    candles_path = os.path.join(CACHE_DIR, f"945_signals_{TODAY.strftime('%Y-%m-%d')}.json")
    if os.path.exists(candles_path):
        with open(candles_path, "r") as f:
            candle_data = json.load(f)        
        if "candles" not in candle_data or not candle_data["candles"]:
            print("⚠️ 945_signals is missing 'candles' or it's empty")
            issues_found = True
        else:
            empty_candles = [s for s, c in candle_data["candles"].items() if not c]
            if empty_candles:
                print(f"⚠️ {len(empty_candles)} tickers have no candle data in 945_signals")
                issues_found = True
    else:
        print("⚠️ 945_signals missing!")
        issues_found = True

    # Short Interest
    short_path = os.path.join(CACHE_DIR, "short_interest.json")
    if os.path.exists(short_path):
        with open(short_path, "r") as f:
            short_data = json.load(f)
        if len(short_data) < 50:
            print(f"⚠️ Only {len(short_data)} short interest tickers found — expected more")
            issues_found = True
    else:
        print("⚠️ short_interest.json missing!")
        issues_found = True

    if not issues_found:
        print("✅ Cache Audit Passed — All major caches healthy.\n")
    else:
        print("⚠️ Cache Audit found some problems. Check warnings above.\n")

    return not issues_found

# --- Validation Function ---
def validate_caches(strict=True, include_scored=False):
    """
    Validate all required cache files exist and are fresh.
    Optionally validate scored universe only after screenbuilder is run.
    """
    issues = []
    today_str = TODAY.strftime("%Y-%m-%d")

    files_to_check = IMPORTANT_FILES.copy()
    if include_scored and "universe_scored" not in files_to_check:
        files_to_check.append("universe_scored")

    for fname in files_to_check:
        if fname == "universe_enriched":
            pattern = os.path.join(CACHE_DIR, f"universe_enriched_{today_str}.json")
        elif fname == "universe_scored":
            pattern = os.path.join(CACHE_DIR, f"universe_scored_{today_str}.json")
        elif fname.startswith("post_open_signals"):
            pattern = os.path.join(CACHE_DIR, f"{fname}_{today_str}.json")
        else:
            pattern = os.path.join(CACHE_DIR, fname)

        if fname.startswith("universe_"):
            matches = glob.glob(pattern)
            if not matches:
                issues.append(f"{os.path.basename(pattern)} is missing.")
                continue
            for match in matches:
                if os.path.getsize(match) == 0:
                    issues.append(f"{os.path.basename(match)} is empty.")
        else:
            if not os.path.exists(pattern):
                issues.append(f"{fname} is missing.")
            elif os.path.getsize(pattern) == 0:
                issues.append(f"{fname} is empty.")

    if issues:
        print("❌ Cache validation failed:")
        for issue in issues:
            print(" -", issue)
        if strict:
            raise SystemExit("🛑 Strict mode enabled — aborting pipeline.")
        else:
            print("⚠️ Non-strict mode — continuing despite warnings.")
            return False
    else:
        print("✅ All required caches validated.")
        return True
    
# --- Main ---
def run_all():
    deleted_files, skipped_files = cleanup_old_files()
    deleted_universe = cleanup_old_universe_files()
    audit_passed = audit_cache_files()

    return {
        "deleted": deleted_files,
        "skipped": skipped_files,
        "universe_deleted": deleted_universe,
        "audit_passed": audit_passed
    }

if __name__ == "__main__":
    run_all()
