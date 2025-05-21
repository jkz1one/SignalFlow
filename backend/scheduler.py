import os
import sys
import time
import subprocess
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
    try:
        subprocess.run([sys.executable, path], check=True)
        end = datetime.now()
        logging.info(f"✅ {name} completed at {end.isoformat()} (duration: {(end-start).total_seconds():.2f}s)")
    except subprocess.CalledProcessError as e:
        end = datetime.now()
        logging.error(f"❌ {name} failed (code {e.returncode}) at {end.isoformat()}")
    except Exception as e:
        end = datetime.now()
        logging.error(f"❌ {name} crashed: {e} at {end.isoformat()}")

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

# --- Run Backfills If Missed (excluding Cache Manager) ---
def check_and_run_backfills():
    logging.info("🔁 Checking for missed jobs...")
    tz = timezone("US/Eastern")
    now = datetime.now(tz)
    if not is_market_day():
        logging.info("📅 Today is not a market day — skipping backfills.")
        return

    today_str = now.strftime("%Y-%m-%d")

    # Universe Builder @ 05:00
    uni_cutoff = datetime.combine(now.date(), dt_time(5, 0), tzinfo=tz)
    if now > uni_cutoff:
        uni_path = os.path.join(CACHE_DIR, f"universe_{today_str}.json")
        if not os.path.exists(uni_path):
            logging.info("🔁 Backfilling Universe Builder now...")
            run_script(SCRIPTS["Universe Builder"], "Universe Builder")
        else:
            logging.info("✅ Universe file exists, skipping backfill.")

    # Post-Open Signals main: backfill anytime after scheduled run until market close
    pos_cutoff = datetime.combine(now.date(), dt_time(9, 35, 30), tzinfo=tz)
    market_close = datetime.combine(now.date(), dt_time(16, 0), tzinfo=tz)
    pos_path   = os.path.join(CACHE_DIR, f"post_open_signals_{today_str}.json")
    logging.info(f"🕓 Post-Open window: after {pos_cutoff.time()} until market close {market_close.time()}, now: {now.time()}")
    if now >= pos_cutoff and now <= market_close:
        if not os.path.exists(pos_path):
            logging.info("🔁 Backfilling Post-Open Signals during market hours...")
            run_script(SCRIPTS["Post Open Signals"], "Post Open Signals")
        else:
            logging.info("✅ Post-Open file exists, skipping backfill.")
    else:
        logging.info("⏳ Outside Post-Open window for backfill, skipping.")

    # 945 Signals @ 09:45:30: backfill anytime after cutoff until market close
    s945_cutoff = datetime.combine(now.date(), dt_time(9, 45, 30), tzinfo=tz)
    s945_path   = os.path.join(CACHE_DIR, f"945_signals_{today_str}.json")
    logging.info(f"🕓 945 Signals window: after {s945_cutoff.time()} until market close {market_close.time()}, now: {now.time()}")
    if now >= s945_cutoff and now <= market_close:
        if not os.path.exists(s945_path):
            logging.info("🔁 Backfilling 945 Signals during market hours...")
            run_script(SCRIPTS["945 Signals"], "945 Signals")
        else:
            logging.info("✅ 945 file exists, skipping backfill.")
    else:
        logging.info("⏳ Outside 945 Signals window for backfill, skipping.")

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
