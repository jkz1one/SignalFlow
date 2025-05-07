## enrich_watchdog.py
import os
import time
import subprocess
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- Config ---
WATCH_DIR = os.path.join("backend", "cache")
TRIGGER_SCRIPT = os.path.join("backend", "enrich_universe.py")
TRIGGER_FILES = [
    "post_open_signals_",
    "945_signals_",
    "short_interest.json",
    "multi_day_levels.json"
]
COOLDOWN_SECONDS = 60  # Avoid re-triggering too frequently

def initial_check_and_trigger():
    found = False
    for trigger_key in TRIGGER_FILES:
        for fname in os.listdir(WATCH_DIR):
            if fname.startswith(trigger_key):
                found = True
                break
    if found:
        print(f"⚡ Detected ready file on startup: '{fname}' — running enrichment once.")
        run_enrichment()

last_triggered = {}

class CacheUpdateHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return

        filename = os.path.basename(event.src_path)
        for trigger_key in TRIGGER_FILES:
            if trigger_key in filename:
                now = time.time()
                last_time = last_triggered.get(trigger_key, 0)

                if now - last_time > COOLDOWN_SECONDS:
                    print(f"🕵️ File updated: {filename} — triggering enrichment...")
                    run_enrichment()
                    last_triggered[trigger_key] = now
                else:
                    print(f"⏱️ Skipped duplicate trigger for: {filename}")

# ... [rest of the script unchanged]

def run_enrichment():
    timestamp = datetime.now().strftime("%H:%M:%S")
    try:
        subprocess.run(["python", TRIGGER_SCRIPT], check=True)
        print(f"✅ Enrichment completed at {timestamp}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Enrichment failed at {timestamp}: {e}")

if __name__ == "__main__":
    initial_check_and_trigger()
    observer = Observer()
    event_handler = CacheUpdateHandler()
    observer.schedule(event_handler, path=WATCH_DIR, recursive=False)
    observer.start()
    print("👀 Watchdog is now watching for file updates...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("🛑 Watchdog stopped.")
    observer.join()
