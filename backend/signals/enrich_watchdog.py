## enrich_watchdog.py
import os
import time
import subprocess
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- Config ---
WATCH_DIR = os.path.join("backend", "cache")
ENRICH_SCRIPT = os.path.join("backend", "enrich_universe.py")
SCREENBUILDER_SCRIPT = os.path.join("backend", "screenbuilder.py")
WATCHLIST_SCRIPT = os.path.join("backend", "watchlist_builder.py")  # adjust if different
TRIGGER_FILES = [
    "post_open_signals_",
    "945_signals_",
    "short_interest.json",
    "multi_day_levels.json"
]
COOLDOWN_SECONDS = 120  # Avoid re-triggering too frequently

last_triggered = {}


def run_pipeline():
    now = datetime.now().strftime("%H:%M:%S")
    try:
        subprocess.run(["python", ENRICH_SCRIPT], check=True)
        print(f"✅ Enrichment completed at {now}")
        subprocess.run(["python", SCREENBUILDER_SCRIPT], check=True)
        print(f"✅ Screenbuilder completed at {now}")
        subprocess.run(["python", WATCHLIST_SCRIPT], check=True)
        print(f"✅ Watchlist builder completed at {now}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Pipeline failed at {now}: {e}")


def initial_check_and_trigger():
    # If any trigger file already present at startup, fire pipeline once
    for trigger in TRIGGER_FILES:
        for fname in os.listdir(WATCH_DIR):
            if fname.startswith(trigger):
                print(f"⚡ Detected '{fname}' on startup — running full pipeline.")
                run_pipeline()
                return


class CacheUpdateHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        filename = os.path.basename(event.src_path)
        for trigger in TRIGGER_FILES:
            if trigger in filename:
                now = time.time()
                last = last_triggered.get(trigger, 0)
                if now - last > COOLDOWN_SECONDS:
                    print(f"🕵️ Detected update '{filename}' — running full pipeline...")
                    run_pipeline()
                    last_triggered[trigger] = now
                else:
                    print(f"⏱️ Skipping duplicate trigger for '{filename}'")
                break


if __name__ == "__main__":
    initial_check_and_trigger()
    observer = Observer()
    handler = CacheUpdateHandler()
    observer.schedule(handler, path=WATCH_DIR, recursive=False)
    observer.start()
    print("👀 Watchdog is watching for file updates...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("🛑 Watchdog stopped.")
    observer.join()

