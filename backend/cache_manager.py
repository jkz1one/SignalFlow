import os
import argparse
from datetime import datetime

# --- Config ---
CACHE_DIR = "backend/cache"
LAST_CLEAR_FILE = os.path.join(CACHE_DIR, ".last_clear")


def read_last_clear_date():
    """
    Read the date the cache was last cleared (YYYY-MM-DD) from LAST_CLEAR_FILE.
    Returns a datetime.date or None if not found or unreadable.
    """
    if not os.path.exists(LAST_CLEAR_FILE):
        return None
    try:
        with open(LAST_CLEAR_FILE, "r") as f:
            return datetime.fromisoformat(f.read().strip()).date()
    except Exception as e:
        print(f"⚠️ Could not read last clear date: {e}")
        return None


def write_last_clear_date(date):
    """
    Write the given date (datetime.date) to LAST_CLEAR_FILE in ISO format.
    """
    try:
        with open(LAST_CLEAR_FILE, "w") as f:
            f.write(date.isoformat())
    except Exception as e:
        print(f"⚠️ Could not write last clear date: {e}")


def clear_cache():
    """
    Delete all files and directories under CACHE_DIR.
    """
    deleted = 0
    if not os.path.isdir(CACHE_DIR):
        print(f"⚠️ Cache directory '{CACHE_DIR}' not found.")
        return

    for fname in os.listdir(CACHE_DIR):
        path = os.path.join(CACHE_DIR, fname)
        try:
            if os.path.isfile(path) or os.path.islink(path):
                os.remove(path)
                deleted += 1
            elif os.path.isdir(path):
                for root, dirs, files in os.walk(path, topdown=False):
                    for file in files:
                        os.remove(os.path.join(root, file))
                    for dir in dirs:
                        os.rmdir(os.path.join(root, dir))
                os.rmdir(path)
                deleted += 1
        except Exception as e:
            print(f"⚠️ Failed to delete {path}: {e}")
    print(f"🗑️ Cleared cache directory '{CACHE_DIR}', deleted {deleted} items.")


def main(force):
    today = datetime.now().date()
    last_clear = read_last_clear_date()

    if last_clear == today and not force:
        print(f"🗓️ Cache already cleared today ({today}); use --force to override.")
        return

    print(f"🕒 Cache clear started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    clear_cache()
    write_last_clear_date(today)
    print(f"✅ Cache clear completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Clear the cache directory once per day, unless forced."
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Force cache clear even if already run today"
    )
    args = parser.parse_args()
    main(force=args.force)
