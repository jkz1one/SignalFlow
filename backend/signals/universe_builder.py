from shutil import copyfile
import re
import csv
import json
import os
import requests
from datetime import datetime

# === CONFIG ===
ANCHOR_TICKERS = ["SPY", "QQQ", "AAPL", "MSFT", "TSLA", "NVDA", "GME", "KSS", "AMC", "BYND", "GRRR"]
SECTOR_ETFS = ["XLF", "XLK", "XLE"]
DOW_30_TICKERS = [
    "AAPL", "AMGN", "AXP", "BA", "CAT", "CSCO", "CVX", "DIS", "DOW", "GS",
    "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "KO", "MCD", "MMM", "MRK",
    "MSFT", "NKE", "PG", "TRV", "UNH", "V", "VZ", "WBA", "WMT", "CRM"
]
CACHE_DIR = "backend/cache"
LOG_FILE = "backend/logs/universe_build.log"
TODAY_STR = datetime.now().strftime("%Y-%m-%d")
CACHE_FILE = os.path.join(CACHE_DIR, f"universe_{TODAY_STR}.json")

# === FETCH S&P 500 FROM GITHUB ===
def fetch_sp500_csv(save_path):
    url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"})
        r.raise_for_status()
        with open(save_path, "w") as f:
            f.write(r.text)
        print(f"✅ Fetched S&P 500 CSV to {save_path}")
    except Exception as e:
        print(f"❌ Failed to fetch S&P 500: {e}")


def fetch_nasdaq100_csv(save_path):
    url = "https://yfiua.github.io/index-constituents/constituents-nasdaq100.csv"
    try:
        r = requests.get(url)
        r.raise_for_status()
        with open(save_path, "w") as f:
            f.write(r.text)
        print(f"✅ Fetched Nasdaq 100 CSV to {save_path}")
    except Exception as e:
        print(f"❌ Failed to fetch Nasdaq 100: {e}")


# === LOADERS ===
def load_csv_tickers(filepath):
    tickers = []
    try:
        with open(filepath, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "Symbol" in row:
                    tickers.append(row["Symbol"].strip().upper())
                elif "Ticker" in row:
                    tickers.append(row["Ticker"].strip().upper())
    except FileNotFoundError:
        print(f"⚠️ CSV not found: {filepath}")
    return tickers

# === MAIN ===
def build_universe():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    if not os.path.exists("backend/logs"):
        os.makedirs("backend/logs")

    if os.path.exists(CACHE_FILE):
        print(f"✔ Universe already built today: {CACHE_FILE}")
        return

    fetch_sp500_csv("data/sp500.csv")
    fetch_nasdaq100_csv("data/nasdaq100.csv")

    sp500 = set(load_csv_tickers("data/sp500.csv"))
    nasdaq100 = set(load_csv_tickers("data/nasdaq100.csv"))
    dow30 = set(DOW_30_TICKERS)
    anchors = set(ANCHOR_TICKERS)
    sector_etfs = set(SECTOR_ETFS)

    combined = sp500.union(nasdaq100).union(dow30).union(anchors).union(sector_etfs)
    universe = {}

    for ticker in combined:
        level = None
        sources = []
        if ticker in sp500:
            sources.append("sp500")
        if ticker in nasdaq100:
            sources.append("nasdaq100")
        if ticker in dow30:
            sources.append("dow30")
        if ticker in anchors:
            sources.append("anchor")
        if ticker in sector_etfs:
            sources.append("etf")

        if ticker in anchors:
            level = "L0"
        elif ticker in dow30 or ticker in sector_etfs:
            level = "L1"
        elif ticker in sp500 or ticker in nasdaq100:
            level = "L2"
        else:
            level = "L3"

        universe[ticker] = {
            "sources": sources,
            "level": level
        }

    with open(CACHE_FILE, "w") as f:
        json.dump(universe, f, indent=2)

    with open(LOG_FILE, "a") as log:
        log.write(f"[{datetime.now()}] Built universe: {len(universe)} tickers\n")

    print(f"✅ Universe cached: {CACHE_FILE} | Total: {len(universe)} tickers")

if __name__ == "__main__":
    build_universe()


copyfile(CACHE_FILE, "backend/cache/universe_cache.json")
print("✅ Universe also saved to backend/cache/universe_cache.json")
