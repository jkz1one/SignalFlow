## scheduler.py
import os
import time
import subprocess
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
import logging
from logging.handlers import RotatingFileHandler

# --- Logging Setup with Rotation ---
LOG_PATH = os.path.join(os.path.dirname(__file__), "logs", "scheduler.log")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

handler = RotatingFileHandler(LOG_PATH, maxBytes=5_000_000, backupCount=3)
formatter = logging.Formatter('%(asctime)s — %(levelname)s — %(message)s')
handler.setFormatter(formatter)

logging.basicConfig(handlers=[handler], level=logging.INFO)

# --- Global Scheduler ---
scheduler = BackgroundScheduler(timezone="US/Eastern")

# --- Config ---
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
SCRIPTS = {
    "Universe Builder": "backend/signals/universe_builder.py",
    "Short Interest": "backend/signals/fetch_short_interest.py",
    "Post Open Signals": "backend/signals/post_open_signals.py",
    "945 Signals": "backend/signals/945_signals.py",
    "Enrich Universe": "backend/signals/enrich_universe.py"
}

# --- Run Script Wrapper ---
def run_script(path, name):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n⏱️ [{timestamp}] Running: {name}")
    logging.info(f"⏱️ Running: {name}")
    try:
        subprocess.run(["python", path], check=True)
        print(f"✅ {name} completed.")
        logging.info(f"✅ {name} completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ {name} failed with return code {e.returncode}")
        logging.error(f"❌ {name} failed with return code {e.returncode}")
    except Exception as e:
        print(f"❌ {name} crashed: {e}")
        logging.error(f"❌ {name} crashed: {e}")

# --- Backfill Helper ---
def should_backfill(target_time_str, file_prefix):
    eastern = timezone("US/Eastern")
    now = datetime.now(eastern)
    target_time = datetime.strptime(target_time_str, "%H:%M").replace(
        year=now.year, month=now.month, day=now.day, tzinfo=eastern
    )
    today_str = now.strftime("%Y-%m-%d")
    expected_path = os.path.join(CACHE_DIR, f"{file_prefix}_{today_str}.json")
    return now > target_time and not os.path.exists(expected_path)

# --- Run Backfills If Missed ---
def check_and_run_backfills():
    print("🔁 Checking for missed jobs...")
    logging.info("🔁 Checking for missed jobs...")
    if should_backfill("09:00", "short_interest"):
        run_script(SCRIPTS["Short Interest"], "Short Interest")
    if should_backfill("09:35", "post_open_signals"):
        run_script(SCRIPTS["Post Open Signals"], "Post Open Signals")
    if should_backfill("09:45", "945_signals"):
        run_script(SCRIPTS["945 Signals"], "945 Signals")

# --- Watchdog ---
def launch_enrich_watchdog():
    print("🐺 Starting Enrich WatchDog...")
    logging.info("🐺 Starting Enrich WatchDog...")
    subprocess.Popen(["python", "backend/signals/enrich_watchdog.py"])

# --- Schedule Jobs ---
def schedule_jobs():
    scheduler.add_job(lambda: run_script(SCRIPTS["Universe Builder"], "Universe Builder"),
                      trigger="cron", hour=9, minute=0)
    scheduler.add_job(lambda: run_script(SCRIPTS["Short Interest"], "Short Interest"),
                      trigger="cron", hour=9, minute=0, second=10)
    scheduler.add_job(lambda: run_script(SCRIPTS["Post Open Signals"], "Post Open Signals"),
                      trigger="cron", hour=9, minute=35, second=50)
    scheduler.add_job(lambda: run_script(SCRIPTS["945 Signals"], "945 Signals"),
                      trigger="cron", hour=9, minute=45, second=50)
    scheduler.add_job(lambda: run_script(SCRIPTS["Enrich Universe"], "Enrich Universe"),
                      trigger="cron", hour=9, minute=46, second=30)
    scheduler.start()
    logging.info("✅ APScheduler started.")



# --- Entrypoint ---
if __name__ == "__main__":
    print("📅 Scheduler initializing...")
    logging.info("📅 Scheduler initializing...")

    launch_enrich_watchdog()
    check_and_run_backfills()
    schedule_jobs()


    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Scheduler stopped.")
        scheduler.shutdown(wait=True)
        logging.info("🛑 Scheduler shutdown complete.")

