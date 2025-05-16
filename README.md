# 📊 Stock Screener 3.7 – Momentum & Risk-Aware Watchlist Builder

A real-time stock scanning tool that builds a tiered watchlist using volume, price action, sector rotation, and risk filters. Built with FastAPI + Next.js.

> **Currently optimized** for identifying momentum setups at **market open**. 🚀
>
> Use the `stable` branch if you need reliability.

---

![example](https://github.com/user-attachments/assets/97ff525c-fe60-4af3-8952-d913e9e46a75)

---

## 🔧 How It Works

### 🖥️ Frontend

- Live at `/tracker` via Next.js
- Displays:
  - Watchlist of scored stocks
  - Tier hits (T1, T2, T3)
  - Risk tags (e.g., Low Liquidity, Wide Spread)
  - Custom labels like “Strong Setup” or “Squeeze Watch”

- Interactive filters:
  - Tier toggle (T1/T2/T3)
  - Show/hide risk-blocked tickers
  - Tag filters (e.g., “Early Watch”, “Top Gainer”)
  - Sort by score

---

### ⚙️ Backend Active Modules

| Module                 | Function                                                 |
| ---------------------- | -------------------------------------------------------- |
| `scheduler.py`         | Job manager (APScheduler) for timed runs                 |
| `cache_manager.py`     | Cleans and resets stale files at start of day            |
| `enrich_watchdog.py`   | Monitors signal files and auto-triggers enrichment flow  |
| `enrich_universe.py`   | Adds Tier 1–3 signals, risk filters, sector mapping      |
| `screenbuilder.py`     | Scores and tags all tickers by signal strength           |
| `watchlist_builder.py` | Filters to final daily watchlist based on score/risk     |

---

## 🔁 Daily Automation Flow

### 🕒 Timed by Scheduler
0. **4:00 AM** - `cache_manager.py`
1. **5:00 AM** – `universe_builder.py` 
2. **9:35 AM** – `fetch_short_interest.py` 
3. **9:35 AM** – `post_open_signals.py` 
4. **9:45 AM**  - `945_signals.py`
5. **Auto** – `enrich_watchdog.py` detects new signals → triggers `enrich_universe.py`  
6. **Auto** – Enrichment triggers `screenbuilder.py` and `watchlist_builder.py`

> All steps are modular and incremental — no full rebuilds required after reset.

---

## ▶️ How to Run

```bash
# Step 0 — Install dependencies (one-time setup)
pip install -r backend/requirements.txt

# Step 1 — Run Scheduler
python3 backend/scheduler.py

# Step 1 — Run Scheduler
python3 backend/scheduler.py

# Step 3 — Start backend API (FastAPI)
uvicorn backend.main:app --reload --port 8000

# Step 4 — Start frontend (Next.js)
npm run dev
```

---

## 🚨 Key Fixes & Changes (v3.7+)
* ✅ Sector Rotation Tab is Live Updating
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

## 📁 Project Structure

```

backend/

├── cache/                   # Daily signal + universe files
├── signals/                 # Signal scrapers and enrichment triggers
│   ├── 945_signals.py            # Scrapes 9:30–9:40 range breakout data
│   ├── enrich_watchdog.py        # Watches signal files, triggers enrichment
│   ├── fetch_short_interest.py   # Pulls short float data from FINRA/Nasdaq
│   ├── post_open_signals.py      # Combines rel vol, % move, sector strength
│   └── universe_builder.py       # Builds base universe from anchor levels
├── cache_manager.py         # Clears stale cache at 4AM or on demand
├── enrich_universe.py       # Combines signals, applies tiers and risk filters
├── scheduler.py             # Schedules all timed jobs and monitors run state
├── screenbuilder.py         # Scores tickers based on tier confluence
└── watchlist_builder.py     # Filters scored tickers into final ranked output

```

---

## 📡 API Endpoints

| Route                   | Purpose                                  |
| ----------------------- | ---------------------------------------- |
| `/api/autowatchlist`    | Final filtered watchlist                 |
| `/api/scored`           | Scored universe with tier signals        |
| `/api/enriched`         | Enriched universe (pre-scoring)          |
| `/api/raw`              | Raw pulled universe (from CSVs/static)   |
| `/api/sector`           | Live Sector ETF % change and data        |
| `/api/cache-timestamps` | File freshness tracker for debugging/UI  |

---

## 🚧 Roadmap & Goals

### Next Steps and In Progress

* ⏳ Optimize scrapers for speed
* ⏳ Seperate sector rotation scrape and run hourly
* ⏳ More logging for scheduler
* ⏳ Make unified run script for frontend, backend, and scheduler

### Upcoming

* [ ] Frontend timestamp display (data freshness)
* [ ] Backend risk filters fix
* [ ] Frontend risk toggle fix
* [ ] Customizable thresholds via config API (SI, Rel Vol %, etc.) 
* [ ] Admin Panel Build Start
* [ ] Discord/Email alerts (failures/screener screenshots)
* [ ] Docker deploy

## 🧪 Long-Term Goals

- Admin page toggles for variables.
- Replay / Backtest mode
- Multi-screener (Opening, Swing, Overnight)
- Unified screener with all logic toggles.
- GEX / 0DTE / Options Flow overlays
- Watchlist alerts + email/export
- Replay/backtest signal flow
- Sentiment overlays (SPX/SPY, VIX/VIXY)

---

## ⚠️ Known Issues
* 
* Gap up/down logic needs improvement
* Premarket levels pending (needed for Momentum Confluence logic)
* Risk filters pending (right now, most risk filtering happens in universe build)
---

> Built for speed. Modular by design. Validate before trading.  
> *“Momentum belongs to the prepared.”* 🔍