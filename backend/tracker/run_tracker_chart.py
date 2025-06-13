# backend/tracker/run_tracker_chart.py
import subprocess
import sys

def run_pipeline(symbol: str):
    subprocess.run(["python", "backend/tracker/fetch_tv_data.py", "--symbols", symbol], check=True)
    subprocess.run(["python", "backend/tracker/build_tracker_candles.py", symbol], check=True)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_tracker_chart.py SYMBOL")
        sys.exit(1)
    run_pipeline(sys.argv[1].upper())
