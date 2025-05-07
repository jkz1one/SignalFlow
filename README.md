# 📊 Stock Screener 3.7 – Momentum & Risk-Aware Watchlist Builder

A real-time stock scanning tool that builds a tiered watchlist using volume, price action, sector rotation, and risk filters. Built with FastAPI + Next.js.

## Currently optimized for identifying momentum setups at market open.

![example](https://github.com/user-attachments/assets/97ff525c-fe60-4af3-8952-d913e9e46a75)

**⚠️ This version is under construction for automation and may be unstable.**

> Use the `stable` branch if you need reliability.

---

## 🔧 How It Works – Automation Flow

### ⚙️ Daily Pipeline (Scheduler Driven)

* `scheduler.py`: Core job manager with APScheduler.

  * Launches `universe_builder.py` at 9:00 AM
  * Triggers all enrichment scrapers: `post_open_signals.py`, `945_signals.py`, `fetch_short_interest.py`
  * Kicks off `enrich_universe.py` (also runs on file update via `enrich_watchdog.py`)
  * Enrichment is modular and incremental
  * Future: Trigger scoring and watchlist build automatically after enrichment

### 🐺 `enrich_watchdog.py`

* Monitors cache directory for signal file updates
* Triggers `enrich_universe.py` when:

  * `post_open_signals_*.json`
  * `945_signals_*.json`
  * `short_interest.json`
  * `multi_day_levels.json` update
* Detects stale state on startup and optionally runs enrichment

### 📦 Cache Cleanup

* `cache_manager.py`: Clears stale/unneeded files each morning (future 4:00 AM run goal)
* Health check audit prints missing/expired cache file report

---

## ✅ Project Goals – v3.7

### Known Issues
* - Enrich runs multiple times during post_open_signals because it is saving every so many tickers. The updated post open signals.json causes enrich universe to run. This is causing the universe file to have multiple tags/reasons under Tier Hits.
* - Enrich isn't calculating sector 

### Completed

* ✅ Tier 1, 2, and 3 signal logic implemented
* ✅ Risk filters (liquidity, spread)
* ✅ Enrichment: TV price/vol, candles, short interest, multi-day highs
* ✅ Cache cleaner + audit tools
* ✅ Watchlist scoring + tagging + filtering
* ✅ `run_pipeline.py` orchestrates full system
* ✅ Fixed Cache Manager
* ✅ `post_open_signals.py` rewritten to prevent YF rate limits
* ✅ `enrich_universe.py` now fails gracefully, supports incremental enrichments
* ✅ Scheduler + Watchdog now coordinate
* ✅  Fixed BRK.B ticker parsing

### In Progress

* ⏳ Tier 1 Momentum Confluence (waiting for TradingView premarket levels)
* ⏳ Frontend timestamp display + Sector Tab
* ⏳ Universe Builder v2 (dynamic filtering by market cap, liquidity)
* ⏳ Auto-run screenbuilder after enrichment

### Next Steps

* [ ] Implement 4:00 AM daily reset via `cache_manager.py`
    (smart reset incase pipeline is ran after 4A M)
* [ ] Automatically run `screenbuilder.py` and `watchlist_builder.py` after enrichment
* [ ] Consider adding manual run commands while scheduler active
* [ ] Add Admin Panel to trigger backend jobs manually
* [ ] Add customizable thresholds (e.g., rel vol min) via config
* [ ] Fix frontend risk toggle logic
* [ ] Add Discord/Email alerts for job failures
* [ ] Strip unused dependencies and clean legacy scripts

---

## ▶️ How to Run

```bash
# Step 0 — Install dependencies (Python 3.10+ recommended)
pip install -r backend/requirements.txt

# Step 1 — Run the Virtual Environment 
source backend/screener-venv/bin/activate

# Step 2 — Run the scheduler (auto job runner)
# This will schedule all jobs and auto-trigger enrichment
python3 backend/scheduler.py

# Step 2.5 — Manual run (to be automated)
python3 backend/screenbuilder.py
python3 backend/watchlist_builder.py

# Step 3 — Start backend API (FastAPI)
uvicorn backend.main:app --reload --port 8000

# Step 4 — Start frontend (Next.js)
npm run dev
```

---

## 📡 API Endpoints (Backend/FastAPI)

| Endpoint                | Description                         |
| ----------------------- | ----------------------------------- |
| `/api/autowatchlist`    | Returns final filtered watchlist    |
| `/api/universe`         | Returns scored universe w/ signals  |
| `/api/raw`              | Returns raw enriched universe       |
| `/api/sector`           | Returns sector ETF signal data      |
| `/api/cache-timestamps` | Returns freshness metadata per file |

---

## 🧪 Long-Term Features (Exploration)

* Admin page toggles for variables
* Multiple time-based screeners (e.g., EOD, After Hours)
* Unified screener with logic toggles
* Options flow: GEX, Vanna, Charm, 0DTE triggers
* Screener rule editor UI (custom setups)
* Watchlist alerts + export/email
* Replay/backtest signal flow
* Sentiment overlays (SPY/VIX/VVIX)
* Institutional block scan
* Docker deploy + Cloud job host

---

> Modular, scalable, momentum-aware, and built for speed — this system is meant to evolve. Data integrity not guaranteed. Validate before trading.
