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
| `run_tracker.py`           | Central runner: executes TV fetch, calculates signals, builds candles |
| `tracker_candles.py`       | API endpoint handler for chart candles (supports cache\_only mode)    |

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

### ⚙️ Live Polling (Frontend)

* GlobalContextBar — refreshes macro ticker data every 60s

* StockTracker — refreshes system labels + levels (via API) every 60s

* Chart — fetches fresh candles from backend every 60s

* SectorRotation — re-polls SPDR ETF % change and leaders every 60s

> All live views use lightweight fetches and frontend-side timers to stay updated.

---

## 📁 Project Structure

```
backend/

├── cache/                         # Daily signal + universe files
│   └── tracker_candles_*.json         # Cached TV candle files by symbol/interval
│   └── tracker_signals_*.json         # Momentum + system logic per ticker
│   └── global_context.json            # SPY/VIX/etc. macro overlay
│   └── sector_etf_prices.json         # Sector rotation intraday strength
│   └── post_open_signals.json         # Merged rel vol / % move / sector strength
│   └── universe_enriched.json         # Final enriched ticker data
│   └── autowatchlist_cache.json       # Final scored + filtered list
│   └── cache_timestamps.json          # File freshness timestamps
│
├── signals/                     # Signal scrapers and enrichment triggers
│   ├── 945_signals.py               # Scrapes 9:30–9:40 breakout info
│   ├── enrich_watchdog.py           # Watches signal files, triggers enrichment
│   ├── fetch_global_context.py      # Fetches SPY, BTC, DXY, yields, etc.
│   ├── post_open_signals.py         # Rel vol, % move, sector strength merge
│   ├── sector_signals.py            # WebSocket-based sector strength signals
│   └── universe_builder.py          # Builds base universe from anchor tickers
│
├── tracker/                     # Stock Tracker module
│   ├── fetch_tv_data.py             # Fetch raw TradingView candles for symbol/interval
│   ├── build_tracker_candles.py     # Groups and formats candles by interval
│   ├── calc_tracker_signals.py      # Calculates system/momentum states from candles
│   └── run_tracker.py               # Orchestrates fetch → calc pipeline on demand
│
├── routes/                      # FastAPI route handlers (backend API)
│   ├── autowatchlist_router.py      # /api/autowatchlist
│   ├── cache_timestamps_router.py   # /api/cache-timestamps
│   ├── enriched_router.py           # /api/enriched
│   ├── global_context_router.py     # /api/global_context
│   ├── raw_router.py                # /api/raw
│   ├── scored_router.py             # /api/scored
│   ├── sector_router.py             # /api/sector
│   ├── tracker_router.py            # /api/tracker/{symbol}
│   └── tracker_candles_router.py    # /api/tracker-candles
│
├── cache_manager.py             # Clears stale cache at 4AM or on demand
├── enrich_universe.py           # Combines signals, applies tiers and risk filters
├── main.py                      # FastAPI entrypoint – mounts all API routers
├── scheduler.py                 # Schedules jobs, checks for data completeness
├── screenbuilder.py             # Scores enriched tickers by confluence
└── watchlist_builder.py         # Filters to final daily ranked watchlist
```

---

## 📡 API Endpoints

| Route | Purpose |
| --- | --- |
| `/api/autowatchlist` | Returns the final watchlist (scored, filtered, tier-tagged tickers) |
| `/api/cache-timestamps` | Returns timestamps for all cached data files (for debugging or frontend freshness display) |
| `/api/global_context` | Macro context bar data (SPY, BTC, DXY, Gold, etc.) |
| `/api/enriched` | Universe after data enrichment but before scoring |
| `/api/scored` | Fully enriched and scored universe (with Tier 1–3 flags) |
| `/api/sector` | Sector ETF data and intraday % change breakdown |
| `/api/tracker/{symbol}` | Runs tracker pipeline: fetch TV data → calculate system + momentum → outputs `tracker_signals_{symbol}.json` |
| `/api/tracker-candles?symbol={SYMBOL}&interval={INTERVAL}&cache={true\|false}` | Returns TradingView candle data (5m, 10m, 30m, etc).<br>**Defaults:** `interval=5m`, `cache=true`. Set `cache=false` to force fresh fetch. |
| `/api/raw` | Raw universe before enrichment (from static CSV sources) |

---

## 🚨 Key Fixes & Changes (v3.7+)

* ✅ Added fully functional Stock Tracker tab  
  * Symbol search, multi-timeframe chart, real-time level data
* ✅ Integrated Lightweight Charts (v4.1.1) with autoscaling + ↻ reset
* ✅ Built `/api/tracker-candles` with `cache=true|false` toggle
* ✅ Modularized tracker backend: `fetch_tv_data`, `build_tracker_candles`, `calc_tracker_signals`
* ✅ Implemented cache fallback logic for candles + system labels
* ✅ Cleaned chart UI: scroll past edges, autoscale reset, removed right-edge shadow
* ✅ Hooked up system + momentum states from backend to frontend
* ✅ Stabilized tracker fetch flow via `run_tracker.py` + FastAPI route
* ✅ Finalized backend structure: `routes/`, `tracker/`, `signals/`, `cache/`

### v3.73 and previous

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

* [ ] Consider dedicated middleware script for stock tracker
* [ ] Consider update for cache-timestamps for new api endpoints
* [ ] Fix tracker fetch errors (fallbacks, error messages)
* [ ] Make `sector_signals.py` activated by sector page via main
* [ ] Add marquee to context bar
* [ ] Clarify T1 break above/below range on frontend for what timeframe

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
* [ ] Integrate momentum tracker into middle tab
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
