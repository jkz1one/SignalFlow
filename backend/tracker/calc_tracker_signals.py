import os
import json
import pandas as pd
from datetime import datetime, timedelta, time
import pytz
import pandas_market_calendars as mcal

# --- Config ---
CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'cache')
OUTPUT_TEMPLATE = os.path.join(CACHE_DIR, 'tracker_signals_{symbol}.json')
EASTERN = pytz.timezone("US/Eastern")

# --- EMA + Trend Logic ---
def calculate_ema(series, span):
    return series.ewm(span=span, adjust=False).mean()

def determine_trend(ema10, ema50):
    if abs(ema10 - ema50) <= 0.02:
        return "Chop"
    return "Bullish" if ema10 > ema50 else "Bearish"

# --- Load Candle Data ---
def load_data(symbol):
    prefix = f"tv_candles_{symbol.upper()}_"
    files = [f for f in os.listdir(CACHE_DIR) if f.startswith(prefix) and f.endswith(".json")]
    if not files:
        raise FileNotFoundError(f"No TV data found for {symbol} in {CACHE_DIR}")
    files.sort(reverse=True)
    path = os.path.join(CACHE_DIR, files[0])
    with open(path) as f:
        return json.load(f)

# --- Parse Raw JSON to DataFrame ---
def parse_df(raw, interval):
    df = pd.DataFrame(raw[interval])
    timestamp_key = next((col for col in ['datetime', 'time', 'timestamp'] if col in df.columns), None)
    if not timestamp_key:
        raise KeyError("No valid timestamp column found in data")
    df['timestamp'] = pd.to_datetime(df[timestamp_key]).dt.tz_localize(EASTERN)  # PATCHED: assumes timestamps are in Eastern
    df.set_index('timestamp', inplace=True)
    return df.sort_index()

# --- Get Last N Valid Market Days ---
def get_recent_market_days(n=3):
    nyse = mcal.get_calendar("XNYS")
    today = datetime.now(EASTERN).date()
    schedule = nyse.schedule(start_date=today - timedelta(days=10), end_date=today)
    market_days = sorted(schedule.index.date)
    return market_days[-n:]

# --- System Trend (EMA logic) ---
def get_system_trend(df):
    ema10 = calculate_ema(df['close'], 10).iloc[-1]
    ema50 = calculate_ema(df['close'], 50).iloc[-1]
    return determine_trend(ema10, ema50)

# --- Momentum (Confluence Logic) ---
def get_momentum(current_price, prev_hi, prev_lo, pre_hi, pre_lo):
    if prev_hi and pre_hi and current_price > prev_hi and current_price > pre_hi:
        return "Bullish"
    if prev_lo and pre_lo and current_price < prev_lo and current_price < pre_lo:
        return "Bearish"
    return "Chop"

# --- Main Signal Calculation ---
def calc_tracker_signals(symbol):
    raw = load_data(symbol)
    df_5m = parse_df(raw, '5m')
    df_30m = parse_df(raw, '30m')
    df_1h = parse_df(raw, '1h')

    recent_days = get_recent_market_days(n=3)
    if len(recent_days) < 2:
        raise ValueError("❌ Not enough valid market days to compute signals.")

    premarket_day = recent_days[-1]
    prev_day_range_day = recent_days[-2]

    pre_df = df_5m[
        (df_5m.index.date == premarket_day) &
        (df_5m.index.time >= time(4, 0)) &
        (df_5m.index.time <= time(9, 30))
    ]

    prev_df = df_5m[
        (df_5m.index.date == prev_day_range_day) &
        (df_5m.index.time >= time(9, 30)) &
        (df_5m.index.time <= time(16, 0))
    ]

    pre_hi = pre_df['high'].max() if not pre_df.empty else None
    pre_lo = pre_df['low'].min() if not pre_df.empty else None

    prev_hi = prev_df['high'].max() if not prev_df.empty else None
    prev_lo = prev_df['low'].min() if not prev_df.empty else None
    
    if not prev_df.empty:
        close_df = prev_df.between_time("15:55", "15:55")
        prev_close = close_df["close"].iloc[0] if not close_df.empty else prev_df["close"].iloc[-1]
    else:
        prev_close = None

    current_price = df_5m.iloc[-1]['close']

    signals = {
        "symbol": symbol.upper(),
        "timestamp": datetime.now(EASTERN).isoformat(),
        "system_30m": get_system_trend(df_30m),
        "system_1h": get_system_trend(df_1h),
        "momentum": get_momentum(
            current_price=current_price,
            prev_hi=prev_hi,
            prev_lo=prev_lo,
            pre_hi=pre_hi,
            pre_lo=pre_lo
        ),
        "current_price": round(current_price, 2),  # ✅ NEW FIELD
        "premarket_high": round(pre_hi, 2) if pre_hi else None,
        "premarket_low": round(pre_lo, 2) if pre_lo else None,
        "prev_day_high": round(prev_hi, 2) if prev_hi else None,
        "prev_day_low": round(prev_lo, 2) if prev_lo else None,
        "prev_day_close": round(prev_close, 2) if prev_close else None,
    }

    out_path = OUTPUT_TEMPLATE.format(symbol=symbol.upper())
    with open(out_path, "w") as f:
        json.dump(signals, f, indent=2)
    print(f"✅ Saved tracker_signals_{symbol}.json")

# --- CLI Entry Point ---
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("symbol", type=str, help="Ticker symbol, e.g. SPY")
    args = parser.parse_args()
    calc_tracker_signals(args.symbol)
