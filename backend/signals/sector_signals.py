# backend/signals/sector_signals.py
import os
import json
import asyncio
import argparse
import yfinance as yf
from datetime import datetime, time as dt_time
from pytz import timezone

# --- Configuration ---
SECTORS = {
    "XLK": "Technology",
    "XLF": "Financials",
    "XLE": "Energy",
    "XLV": "Healthcare",
    "XLI": "Industrials",
    "XLY": "Consumer Discretionary",
    "XLP": "Consumer Staples",
    "XLU": "Utilities",
    "XLRE": "Real Estate",
    "XLB": "Materials",
    "XLC": "Communication Services",
}

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Dynamic output filename with current date
def get_out_path():
    eastern = timezone("US/Eastern")
    today_str = datetime.now(eastern).strftime("%Y-%m-%d")
    return os.path.join(CACHE_DIR, f"sector_{today_str}.json")

# Define market hours guard for US/Eastern
def is_market_open():
    eastern = timezone("US/Eastern")
    now = datetime.now(eastern)
    # Monday=0, Sunday=6
    if now.weekday() >= 5:
        return False
    current_time = now.time()
    return dt_time(9, 30) <= current_time <= dt_time(16, 0)

async def fetch_sector_prices():
    results = {}
    for symbol, sector in SECTORS.items():
        try:
            data = yf.Ticker(symbol).history(period="1d", interval="1m")
            if data.empty:
                continue
            latest = data.iloc[-1]
            open_price = data.iloc[0]["Open"]
            last_price = latest["Close"]
            change = ((last_price - open_price) / open_price) * 100
            results[symbol] = {
                "sector": sector,
                "price": round(last_price, 2),
                "changePercent": round(change, 2),
            }
        except Exception as e:
            results[symbol] = {"error": str(e)}
    # Add snapshot timestamp in UTC
    results["_timestamp"] = datetime.utcnow().isoformat() + "Z"
    out_path = get_out_path()
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"✅ Sector data saved to {out_path} (snapshot at {results['_timestamp']})")

async def run_loop(interval_seconds):
    while True:
        if is_market_open():
            await fetch_sector_prices()
        else:
            print("⏸️ Market closed — skipping sector update")
        await asyncio.sleep(interval_seconds)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and save sector rotation data on a loop.")
    parser.add_argument(
        "--interval",
        type=int,
        default=int(os.getenv('INTERVAL_SECONDS', '30')),
        help="Polling interval in seconds (env: INTERVAL_SECONDS)"
    )
    args = parser.parse_args()
    try:
        asyncio.run(run_loop(args.interval))
    except KeyboardInterrupt:
        print("🛑 Stopped manually")
