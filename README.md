# 📊 Stock Screener 3.7 – Momentum & Risk-Aware Watchlist Builder

A real-time stock scanning tool that builds a tiered watchlist using volume, price action, sector rotation, and risk filters. Built with FastAPI + Next.js.

Currently optimized for identifying momentum setups at market open.
---
![example](https://github.com/user-attachments/assets/97ff525c-fe60-4af3-8952-d913e9e46a75)

## 🔧 How It Works

### 📦 Daily Refresh
Run this each morning before market open (9:40 AM EST is optimal run time):

- `daily_refresh.py`: Pulls and caches data from multiple scrapers.
  - Build Universe → `universe_cache.json`
  - Scrape TV Signals → `tv_signals.json`
  - Scrape Sector ETFs → `sector_etf_prices.json`
  - Scrape Multi-Day High/Lows → `multi_day_levels.json`
  - Scrape Short Interest → `short_interest.json`
  - Build enriched output → `universe_enriched_*.json`

- Built-in smart cache cleanup:
  - Deletes old or stale files (based on last valid market day)
  - Includes `audit_cache_files()` for health diagnostics

---

### ⚙️ Backend Pipeline

- `run_pipeline.py` runs everything:
  - Enrichment → Scoring → Watchlist
  - Smart cache checks before build
  - Cache cleanup + audit post-run

- Key files:
  - `enrich_universe.py`: Adds price/volume signals, sector data, range breakouts, short interest, risk tags
  - `screenbuilder.py`: Scores all tickers using Tier 1–3 rules
  - `watchlist_builder.py`: Filters and builds final watchlist JSON
  - `universe_builder.py`: Creates base universe from anchor lists and major indexes
  - `cache_manager.py`: Deletes old files, audits cache health
  - `signals/`: All scraper + enrichment logic lives here

---

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

## ▶️ How to Run

```bash
# Step 0 — Install dependencies (one-time setup)
pip install -r backend/requirements.txt

# Step 1 — Run daily refresh (once per day)
python3 backend/daily_refresh.py

# Step 2 — Run full scoring pipeline
python3 run_pipeline.py

# Step 3 — Start backend API (FastAPI)
uvicorn backend.main:app --reload --port 8000

# Step 4 — Start frontend (Next.js)
npm run dev
```

---

## 📡 API Endpoints

| Endpoint                  | Description                        |
|--------------------------|------------------------------------|
| `/api/autowatchlist`     | Returns final filtered watchlist   |
| `/api/universe`          | Returns scored universe with signals |
| `/api/raw`               | Returns raw enriched universe      |
| `/api/sector`            | Returns sector ETF signal data     |
| `/api/cache-timestamps`  | Returns freshness metadata per file|

---

## ✅ Project Goals – v3.7

### Completed
- ✅ Tier 1, 2, and 3 signal logic implemented
- ✅ Risk filters (liquidity, spread)
- ✅ Enrichment: TV price/vol, candles, short interest, multi-day highs
- ✅ Cache cleaner + audit tools
- ✅ Watchlist scoring + tagging + filtering
- ✅ `run_pipeline.py` orchestrates full system

### In Progress
- ⏳ Tier 1 Momentum Confluence (waiting for TradingView premarket levels)
- ⏳ Scheduler for full daily automation
- ⏳ Frontend timestamp display + Sector Tab

### Next Steps
- [ ] Fix Cache Manager.
- [ ] Finish Universe Builder v2.
- [ ] Fix frontend risk toggle logic
- [ ] Add Admin Panel to trigger backend jobs
- [ ] Add customizable thresholds (e.g., rel vol min)
- [ ] Add sector rotation view + GEX system (future)

---

## 🧪 Long-Term Features (Exploration)
- Admin page toggles for variables.
- Multiple time based screens. (EOD/AH)
- Unified screener with logic toggles.
- Options flow: GEX, Vanna, Charm, 0DTE triggers
- Screener rule editor UI (custom setups)
- Watchlist alerts + email/export
- Replay/backtest signal flow
- Sentiment overlays (SPX/SPY, VIX/VIXY)
- Institutional block scan
- Dockerized deploy

---

> This system is a modular and efficient watchlist engine built to scale. Data-driven, momentum-aware, and risk-filtered by default. But it is incomplete, double check all data points.
