import os
import sys
import time
import subprocess
import argparse
from datetime import datetime, timedelta, time as dt_time
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
import pandas_market_calendars as mcal
import logging
from logging.handlers import RotatingFileHandler
from tqdm import tqdm

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
BASE_DIR = os.path.dirname(__file__)
CACHE_DIR = os.path.join(BASE_DIR, "cache")

#--- Status Lock ---
LOCK_PATH = os.path.join(CACHE_DIR, "scrape.lock")

def _write_lock(process: str):
    os.makedirs(CACHE_DIR, exist_ok=True)
    try:
        with open(LOCK_PATH, "w") as f:
            f.write(process)
    except Exception:
        pass

def _clear_lock():
    try:
        if os.path.exists(LOCK_PATH):
            os.remove(LOCK_PATH)
    except Exception:
        pass

SCRIPTS = {
    "Cache Manager": os.path.join(BASE_DIR, "cache_manager.py"),
    "Universe Builder": os.path.join(BASE_DIR, "signals", "universe_builder.py"),
    "Post Open Signals": os.path.join(BASE_DIR, "signals", "post_open_signals.py"),
    "945 Signals": os.path.join(BASE_DIR, "signals", "945_signals.py"),
    "Enrich Watchdog": os.path.join(BASE_DIR, "signals", "enrich_watchdog.py"),
}

# --- Utility: Market Day Check ---
def is_market_day(date=None):
    with tqdm(total=1, desc="Checking market day", bar_format="{l_bar}{bar} {elapsed_s}s") as pbar:
        nyse = mcal.get_calendar("XNYS")
        tz = timezone("US/Eastern")
        today = date or datetime.now(tz).date()
        schedule = nyse.schedule(start_date=today - timedelta(days=7), end_date=today)
        pbar.update(1)
    is_open = today in schedule.index.date
    logging.info(f"✅ {today} is a market day." if is_open else f"📅 {today} is not a market day.")
    return is_open

# --- Run Script Wrapper with Timing ---
def run_script(path, name):
    start = datetime.now()
    logging.info(f"⏱️ Starting {name} at {start.isoformat()}")
    _write_lock(name)
    try:
        subprocess.run([sys.executable, path], check=True)
        end = datetime.now()
        duration = (end - start).total_seconds()
        logging.info(f"✅ {name} completed at {end.isoformat()} (duration: {duration:.2f}s)")
    except subprocess.CalledProcessError as e:
        end = datetime.now()
        logging.error(f"❌ {name} failed (code {e.returncode}) at {end.isoformat()}")
    except Exception as e:
        end = datetime.now()
        logging.error(f"❌ {name} crashed: {e} at {end.isoformat()}")
    finally:
        _clear_lock()
        
# --- Market Day Wrapper ---
def market_day_wrapper(name):
    if is_market_day():
        run_script(SCRIPTS[name], name)
    else:
        logging.info(f"📅 Skipping {name}: Not a market day.")

# --- Watchdog ---
def launch_enrich_watchdog():
    logging.info("🐺 Starting Enrich WatchDog...")
    try:
        subprocess.Popen([sys.executable, SCRIPTS["Enrich Watchdog"]])
        logging.info("🐺 Enrich WatchDog launched successfully.")
    except Exception as e:
        logging.error(f"🐺 Enrich WatchDog failed to start: {e}")

# --- Run Backfills If Missed ---
def check_and_run_backfills():
    logging.info("🔁 Checking for missed jobs...")
    tz = timezone("US/Eastern")
    now = datetime.now(tz)
    if not is_market_day():
        logging.info("📅 Today is not a market day — skipping backfills.")
        return

    today = now.date()
    today_str = today.strftime("%Y-%m-%d")
    market_close = tz.localize(datetime.combine(today, dt_time(16, 0)))

    # Universe Builder
    now = datetime.now(tz)
    uni_cutoff = tz.localize(datetime.combine(today, dt_time(5, 0)))
    if now >= uni_cutoff:
        uni_path = os.path.join(CACHE_DIR, f"universe_{today_str}.json")
        if not os.path.exists(uni_path):
            logging.info("🔁 Backfilling Universe Builder now...")
            run_script(SCRIPTS["Universe Builder"], "Universe Builder")
        else:
            logging.info("✅ Universe file exists, skipping backfill.")

    # Post Open Signals
    now = datetime.now(tz)
    pos_cutoff = tz.localize(datetime.combine(today, dt_time(9, 35, 50)))
    pos_path = os.path.join(CACHE_DIR, f"post_open_signals_{today_str}.json")
    logging.info(f"🕓 Post-Open cutoff at {pos_cutoff.time()}, now: {now.time()}")
    if pos_cutoff <= now <= market_close:
        if not os.path.exists(pos_path):
            logging.info("🔁 Backfilling Post-Open Signals now...")
            run_script(SCRIPTS["Post Open Signals"], "Post Open Signals")
        else:
            logging.info("✅ Post-Open file exists, skipping backfill.")
    else:
        logging.info("⏳ Outside Post-Open window; skipping backfill.")

    # 945 Signals
    now = datetime.now(tz)
    s945_cutoff = tz.localize(datetime.combine(today, dt_time(9, 45, 50)))
    s945_path = os.path.join(CACHE_DIR, f"945_signals_{today_str}.json")
    logging.info(f"🕓 945 cutoff at {s945_cutoff.time()}, now: {now.time()}")
    if s945_cutoff <= now <= market_close:
        if not os.path.exists(s945_path):
            logging.info("🔁 Backfilling 945 Signals now...")
            run_script(SCRIPTS["945 Signals"], "945 Signals")
        else:
            logging.info("✅ 945 file exists, skipping backfill.")
    else:
        logging.info("⏳ Outside 945 window; skipping backfill.")

# --- Force Run ---
def force_run_all():
    logging.info("🏃‍♂️ Forcing execution of all scripts now...")
    for name in ["Cache Manager", "Universe Builder", "Post Open Signals", "945 Signals"]:
        logging.info(f"🔧 Forcing {name}...")
        run_script(SCRIPTS[name], name)

# --- Schedule Jobs ---
def schedule_jobs():
    logging.info("⏲️ Scheduling daily jobs now")
    scheduler.add_job(lambda: market_day_wrapper("Cache Manager"), trigger="cron", hour=4, minute=0)
    scheduler.add_job(lambda: market_day_wrapper("Universe Builder"), trigger="cron", hour=5, minute=0)
    scheduler.add_job(lambda: market_day_wrapper("Post Open Signals"), trigger="cron", hour=9, minute=35, second=50)
    scheduler.add_job(lambda: market_day_wrapper("945 Signals"), trigger="cron", hour=9, minute=45, second=50)
    scheduler.start()
    logging.info("✅ APScheduler started.")

# --- Entrypoint ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scheduler for Screener jobs.")
    parser.add_argument("--force", action="store_true", help="Force run all jobs immediately and exit.")
    args = parser.parse_args()

    if args.force:
        force_run_all()
        sys.exit(0)

    logging.info("📅 Scheduler initializing...")
    time.sleep(5)
    logging.info("🔁 Starting Cache Manager backfill...")
    run_script(SCRIPTS["Cache Manager"], "Cache Manager")
    logging.info("🔁 Cache Manager complete.")
    logging.info("🐺 Launching Enrich WatchDog...")
    launch_enrich_watchdog()
    logging.info("🔁 Running backfills for missed jobs...")
    check_and_run_backfills()
    logging.info("🔁 Backfills complete.")
    logging.info("⏲️ Starting scheduled jobs...")
    schedule_jobs()
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Scheduler shutdown...")
        scheduler.shutdown(wait=True)
