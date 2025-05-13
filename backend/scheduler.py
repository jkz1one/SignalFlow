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
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
SCRIPTS = {
    "Cache Manager": os.path.join("backend", "cache_manager.py"),
    "Universe Builder": os.path.join("backend", "signals", "universe_builder.py"),
    "Short Interest": os.path.join("backend", "signals", "fetch_short_interest.py"),
    "Post Open Signals": os.path.join("backend", "signals", "post_open_signals.py"),
    "945 Signals": os.path.join("backend", "signals", "945_signals.py"),
    "Enrich Watchdog": os.path.join("backend", "signals", "enrich_watchdog.py"),
}

# --- Utility: Market Day Check ---
def is_market_day(date=None):
    """
    Determine if the given date (or today) is a NYSE market day.
    Displays a brief loading bar for visual feedback.
    """
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
        duration = (end - start).total_seconds()
        logging.info(f"✅ {name} completed at {end.isoformat()} (duration: {duration:.2f}s)")
    except subprocess.CalledProcessError as e:
        end = datetime.now()
        duration = (end - start).total_seconds()
        logging.error(f"❌ {name} failed with code {e.returncode} at {end.isoformat()} (duration: {duration:.2f}s)")
    except Exception as e:
        end = datetime.now()
        duration = (end - start).total_seconds()
        logging.error(f"❌ {name} crashed: {e} at {end.isoformat()} (duration: {duration:.2f}s)")

# --- Market Day Wrapper ---
def market_day_wrapper(name):
    if is_market_day():
        run_script(SCRIPTS[name], name)
    else:
        logging.info(f"📅 Skipping {name}: Not a market day.")

# --- Backfill Helper ---
def should_backfill(target_time_str, file_prefix):
    tz = timezone("US/Eastern")
    now = datetime.now(tz)
    target = datetime.strptime(target_time_str, "%H:%M").replace(
        year=now.year, month=now.month, day=now.day, tzinfo=tz
    )
    today_str = now.strftime("%Y-%m-%d")
    expected = os.path.join(CACHE_DIR, f"{file_prefix}_{today_str}.json")
    return now > target and not os.path.exists(expected)

# --- Watchdog ---
def launch_enrich_watchdog():
    """
    Start the enrichment watchdog to auto-trigger enrich_universe after data arrivals.
    """
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
        logging.info("📅 Today is not a market day — skipping all backfills.")
        return

    today_str = now.strftime("%Y-%m-%d")

    # Universe Builder @ 05:00
    uni_cutoff = datetime.combine(now.date(), dt_time(5, 0), tzinfo=tz)
    if now > uni_cutoff:
        uni_path = os.path.join(CACHE_DIR, f"universe_{today_str}.json")
        if not os.path.exists(uni_path):
            run_script(SCRIPTS["Universe Builder"], "Universe Builder")

    # Short Interest @ 09:00
    si_cutoff = datetime.combine(now.date(), dt_time(6, 0), tzinfo=tz)
    if now > si_cutoff:
        si_path = os.path.join(CACHE_DIR, "short_interest.json")
        if not os.path.exists(si_path):
            run_script(SCRIPTS["Short Interest"], "Short Interest")

    # Post-Open Signals @ 09:35:50
    pos_cutoff = datetime.combine(now.date(), dt_time(9, 35, 50), tzinfo=tz)
    if now > pos_cutoff:
        pos_path = os.path.join(CACHE_DIR, f"post_open_signals_{today_str}.json")
        if not os.path.exists(pos_path):
            run_script(SCRIPTS["Post Open Signals"], "Post Open Signals")

    # 945 Signals @ 09:45:50
    s945_cutoff = datetime.combine(now.date(), dt_time(9, 45, 50), tzinfo=tz)
    if now > s945_cutoff:
        s945_path = os.path.join(CACHE_DIR, f"945_signals_{today_str}.json")
        if not os.path.exists(s945_path):
            run_script(SCRIPTS["945 Signals"], "945 Signals")

# --- Schedule Jobs ---
def schedule_jobs():
    logging.info("⏲️ Scheduling daily jobs now")
    scheduler.add_job(lambda: market_day_wrapper("Cache Manager"), trigger="cron", hour=4, minute=0)
    scheduler.add_job(lambda: market_day_wrapper("Universe Builder"), trigger="cron", hour=5, minute=0)
    scheduler.add_job(lambda: market_day_wrapper("Short Interest"), trigger="cron", hour=6, minute=0, second=10)
    scheduler.add_job(lambda: market_day_wrapper("Post Open Signals"), trigger="cron", hour=9, minute=35, second=50)
    scheduler.add_job(lambda: market_day_wrapper("945 Signals"), trigger="cron", hour=9, minute=45, second=50)
    scheduler.start()
    logging.info("✅ APScheduler started.")

# --- Entrypoint ---
if __name__ == "__main__":
    logging.info("📅 Scheduler initializing...")
    # Allow any prior processes or scheduler to initialize
    time.sleep(5)
    # 1) Run Cache Manager backfill immediately
    run_script(SCRIPTS["Cache Manager"], "Cache Manager")
    # 2) Launch the enrichment watchdog to catch new cache files
    launch_enrich_watchdog()
    # 3) Run remaining backfills (universe, short interest, post-open, 945)
    check_and_run_backfills()
    # 4) Start scheduled cron jobs for daily runs
    schedule_jobs()

    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Scheduler shutdown... ")
        scheduler.shutdown(wait=True)
