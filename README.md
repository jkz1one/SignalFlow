# 📊 Stock Screener 3.7 – Momentum & Risk-Aware Watchlist Builder

A real-time stock scanning tool that builds a tiered watchlist using volume, price action, sector rotation, and risk filters. Built with FastAPI + Next.js.

> **Currently optimized** for identifying momentum setups at **market open**. 🚀
>
> Use the `stable` branch if you need reliability.

---

![image](https://github.com/user-attachments/assets/e0152b0d-9d26-4f12-9ea6-ee0a9b4813bb)
![image](https://github.com/user-attachments/assets/9965319a-835a-4a52-bd35-66dcae720f49)
![image](https://github.com/user-attachments/assets/1db93560-2cef-4984-b4a4-2a924424c153)

---

## 🔧 How It Works

### 🖥️ Frontend

* Live at `/tracker` via Next.js

### Includes:

* **Auto-Watchlist of scored stocks**

  * Tier hits (T1, T2, T3)
  * Risk tags (e.g., Low Liquidity, Wide Spread)
  * Custom labels like “Strong Setup” or “Squeeze Watch”
  * Click-to-expand view with screener breakdown
  * **Filters and Controls:**

    * Tier toggle (T1/T2/T3)
    * Show/hide risk-blocked tickers
    * Tag filters (e.g., “Early Watch”, “Top Gainer”)
    * Sort by score or symbol

* **Live Tracker tab**

  * Select any ticker (default: SPY)
  * Displays:

    * Momentum status
    * System trend (30m/1h EMA overlay)
    * Premarket and previous day levels
    * Real-time candle chart

* **Sector Rotation tab**

  * Live updates with top/bottom sector sort
  * Lists leading contributors per sector

---

### ⚙️ Backend Active Modules
| Module                     | Function                                                              |
| -------------------------- | --------------------------------------------------------------------- |
| `scheduler.py`             | APScheduler job manager for scheduled runs                            |
| `cache_manager.py`         | Cleans and resets stale cache files at start of day                   |
| `enrich_watchdog.py`       | Monitors post-open signal files and triggers enrichment automatically |
| `enrich_universe.py`       | Applies Tier 1–3 screeners, risk filters, and sector mapping          |
| `screenbuilder.py`         | Assigns scores and tags based on confluence of triggered signals      |
| `watchlist_builder.py`     | Final pass: filters scored tickers into daily watchlist (score/risk)  |
| `post_open_signals.py`     | Unified fetcher for TV signals, early % move, multi-day highs/lows    |
| `fetch_tv_data.py`         | Scrapes TradingView candles (5m–1D) and caches by symbol+interval     |
| `sector_signals.py`        | Extracts sector % change and leading contributors (SPDR ETFs)         |
| `calc_tracker_signals.py`  | Calculates tracker metrics: system labels (EMA10/50), trend, levels   |
| `build_tracker_candles.py` | Groups raw TV candles, patches timestamps, computes interval EMAs     |

---

## 🔁 Daily Automation Flow

### 🕒 Timed by Scheduler
1. **4:00 AM** - `cache_manager.py`
2. **5:00 AM** – `universe_builder.py` 
3. **9:35 AM** – `post_open_signals.py` 
4. **9:45 AM**  - `945_signals.py`
5. **Auto** – `enrich_watchdog.py` detects new signals → triggers `enrich_universe.py`  
6. **Auto** – Enrichment triggers `screenbuilder.py` and `watchlist_builder.py`

> All steps are modular and incremental — no full rebuilds required after reset.

---

## ▶️ How to Run

> This script sets up the full Screener dev environment using tmux to run all backend and frontend services in parallel.

### **🔧** System Requirements

* Python 3.x
* Node.js + npm
* `tmux` (used for dev runner script)
* `chromedriver` (if scraping via Selenium)
* `curl`, `jq` (if used in shell scripts)

---

### 📂 Setup & tmux Usage

### ✅ Install Requirements

```bash
# System dependencies
brew install tmux
brew install jq
brew install --cask chromedriver

# Python packages
pip install -r backend/requirements.txt

# Frontend packages (run from project root if package.json is there)
npm install
```

### 🚀 Run, Navigate, and Control `tmux`

```bash
# 🚀 Start full dev environment
./run.sh

# Navigate tmux windows
Ctrl + b, then n      # next window
Ctrl + b, then p      # previous window
Ctrl + b, then 0-4    # switch to specific window
Ctrl + b, then w      # list all windows

# Detach (leave processes running)
Ctrl + b, then d

# Reattach later
tmux attach -t screener-dev

# Shut down all processes
tmux kill-session -t screener-dev
```

### 🔎 What `run.sh` Handles

```bash
# Step 1 - Activate Virtual Environment
source backend/screener-venv/bin/activate 

# Step 2 - Run Scheduler
python3 backend/scheduler.py

# Step 3 - Run Sector WS
python3 backend/signals/sector_signals.py

# Step 4 - Start backend API (FastAPI)
uvicorn backend.main:app --reload --port 8000

# Step 5 - Start frontend (Next.js)
npm run dev
```

---

## 📁 Project Structure

```

backend/

├── cache/                   # Daily signal + universe files
├── signals/                 # Signal scrapers and enrichment triggers
│   ├── 945_signals.py            # Scrapes 9:30–9:40 range breakout data
│   ├── enrich_watchdog.py        # Watches signal files, triggers enrichment
│   ├── fetch_global_context.py   # Fetches data for global context bar
│   ├── post_open_signals.py      # Combines rel vol, % move, sector strength
│   ├── sector_signals.py         # Websocket script for sector rotation tab
│   └── universe_builder.py       # Builds base universe from anchor levels
├── cache_manager.py         # Clears stale cache at 4AM or on demand
├── enrich_universe.py       # Combines signals, applies tiers and risk filters
├── scheduler.py             # Schedules all timed jobs and monitors run state
├── screenbuilder.py         # Scores tickers based on tier confluence
└── watchlist_builder.py     # Filters scored tickers into final ranked output

```

---

## 📡 API Endpoints

| Route                                                        | Purpose                                                               |
| ------------------------------------------------------------ | --------------------------------------------------------------------- |
| `/api/autowatchlist`                                         | Final filtered watchlist with score and tier logic                    |
| `/api/cache-timestamps`                                      | File freshness tracker for debugging or UI display                    |
| `/api/global_context`                                        | Global context bar data (SPY, BTC, DXY, etc.)                         |
| `/api/enriched`                                              | Enriched universe before scoring                                      |
| `/api/scored`                                                | Fully scored universe with tier signal flags                          |
| `/api/sector`                                                | Live sector ETF data and % change breakdown                           |
| `/api/tracker/{symbol}`                                      | On-demand run: fetch TV candles → calculate system/momentum levels    |
| `/api/tracker-candles?symbol={SYMBOL}[&interval={INTERVAL}]` | On-demand  TV candle data. Defaults to `5m` if `interval` omitted |
| `/api/raw`                                                   | Raw pulled ticker universe (from static CSV sources)                  |


---

## 🚨 Key Fixes & Changes (v3.7+)

* ✅ Added Stock Tracker 
* ✅ Squeeze watch set to be dynamic
* ✅ `post_open_signals.py` updates with batch mode and SI fetch
* ✅ Added Global Context Bar 
* ✅ `scheduler.py` bug fixes and better logging
* ✅ Sort toggle added to sector rotation tab
* ✅ `fetch_short_interest.py` depreciated
* ✅ Gap threshold set to be dynamic
* ✅ Implented improved gap up logic
* ✅ Optimized `post_open_signals.py`
* ✅ Sector Rotation Tab live updates

### Key Fixes & Changes (v3.72)

* ✅ Updated frontend with new working Sector Rotation tab
* ✅ Updated and Fixed API Endpoints
* ✅ Automation and scheduled jobs now with `scheduler.py`
* ✅ Auto-triggers screen + watchlist build after enrichment
* ✅ 4:00 AM smart reset via `cache_manager.py`
* ✅ `enrich_universe.py` now runs incrementally and fails gracefully
* ✅ `post_open_signals.py` no longer spams multiple writes
* ✅ Sector and short interest integrated cleanly
* ✅ Enrichment double-flag reasons fixed
* ✅ Fixed BRK.B and other ticker edge cases
* ✅ Final watchlist now generated reliably via automation
* ✅ Tier 1, 2, and 3 signal logic implemented

---

## 🚧 Roadmap & Goals

### Next Steps and In Progress

* [ ] Make `sector_signals.py` activated by sector page via main
* [ ] Add marquee to context bar
* [ ] Clarify T1 break above/below range on frontend for what timeframe.

### On Deck

* [ ] Fix Near Multi Day High/Low 
* [ ] Break down enrichment into smaller scripts
* [ ] Build DevOps runner to run all scripts at once
* [ ] Update enrich universe to deal with new post open signals
* [ ] Add more info to sector page (maybe with dropdown?) 
* [ ] Frontend timestamp display (data freshness)

### Upcoming
* [ ] Backend risk filters fix
* [ ] Frontend risk toggle fix
* [ ] Make stocks that score 3 and below hide with risk filter
* [ ] Customizable thresholds via config API (SI, Rel Vol %, etc.) 
* [ ] Customizable anchor tickers
* [ ] Start admin page build
* [ ] Admin page toggles for variables
* [ ] Integreate momentum tracker into middle tab
* [ ] Use lazy-loaded WS and add search feature to middle tab
* [ ] Docker deploy


### 🧪 Long-Term Goals

* [ ] Discord/Email alerts (failures/screener screenshots)
* [ ] Multi-screener (Opening, Swing, Overnight)
* [ ] Unified screener with all logic toggles.
* [ ] GEX / 0DTE / Options Flow overlays
* [ ] Watchlist alerts + email/export
* [ ] Replay/backtest mode 
* [ ] Live Movers / Real-Time Heatmap tab

---

## ⚠️ Known Issues

* Multi-Day high/low not exclusive
* Premarket levels pending (needed for Momentum Confluence logic)
* Risk filters pending (right now, most risk  iltering happens in universe build)

---

> Built for speed. Modular by design. Validate before trading.  
> *“Momentum belongs to the prepared.”* 🔍
