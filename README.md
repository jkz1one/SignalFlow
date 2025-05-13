# 📊 Stock Screener 3.7 – Momentum & Risk-Aware Watchlist Builder

A real-time stock scanning tool that builds a tiered watchlist using volume, price action, sector rotation, and risk filters. Built with FastAPI + Next.js.

> **🚀 Currently optimized for identifying momentum setups at market open.**
> Use the `stable` branch if you need reliability.

---

![example](https://github.com/user-attachments/assets/97ff525c-fe60-4af3-8952-d913e9e46a75)

---

## ⚙️ Automation-First Design

### ✅ Active Modules (Live)

| Module                 | Function                                                 |
| ---------------------- | -------------------------------------------------------- |
| `scheduler.py`         | Job manager (APScheduler) for timed runs                 |
| `enrich_watchdog.py`   | Monitors signal files and auto-triggers enrichment flow  |
| `enrich_universe.py`   | Adds Tier 1–3 signals, risk filters, sector mapping      |
| `screenbuilder.py`     | Scores and tags all tickers by signal strength           |
| `watchlist_builder.py` | Filters to final daily watchlist based on score/risk     |
| `post_open_signals.py` | Combines early % move, TradingView data, sector strength |
| `cache_manager.py`     | Cleans and resets stale files at start of day (soon 4AM) |

---

## 🔁 Daily Automation Flow

### 🕒 Timed by Scheduler

1. **9:00 AM** – `universe_builder.py` runs
2. **9:35 AM** – `post_open_signals.py`, `945_signals.py`, `fetch_short_interest.py` execute
3. **\~9:36 AM onward** – `enrich_watchdog.py` detects new signals → triggers `enrich_universe.py`
4. **Auto** – Enrichment triggers `screenbuilder.py` and `watchlist_builder.py`

> All steps are modular and incremental — no full rebuilds required after reset.

---

## 🚨 Key Fixes & Changes (v3.7+)

* ✅ Auto-triggers screen + watchlist build after enrichment
* ✅ `enrich_universe.py` now runs incrementally and fails gracefully
* ✅ `post_open_signals.py` no longer spams multiple writes
* ✅ Sector and short interest integrated cleanly
* ✅ Fixed BRK.B and other ticker edge cases
* ✅ Final watchlist now generated reliably via automation

---

## 📁 Project Structure

```
backend/
├── cache/                     # Daily signal + universe files
├── scheduler.py               # Master job runner
├── enrich_watchdog.py         # Watches for updated signals
├── enrich_universe.py         # Applies all Tier logic + risk flags
├── screenbuilder.py           # Scores stocks using tier hits
├── watchlist_builder.py       # Filters final watchlist
├── post_open_signals.py       # TradingView + sector + early move
├── cache_manager.py           # Smart morning reset
└── universe_builder.py        # Builds base ticker universe
```

---

## 🚧 Roadmap & Goals

### In Progress

* ⏳ 4:00 AM smart reset via `cache_manager.py`
* ⏳ Frontend timestamp display (data freshness)
* ⏳ Universe Builder v2 (dynamic market cap/volume filters)
* ⏳ Frontend risk toggle fix
* ⏳ Admin Panel to manually run jobs

### Upcoming

* [ ] Customizable thresholds (e.g., rel vol %, volume floors)
* [ ] Discord/Email alerts for job failures
* [ ] Docker deploy and cloud cron runner
* [ ] Multi-screener logic (Opening, Swing, Overnight)
* [ ] GEX / 0DTE / Options Flow overlays
* [ ] Replay / Backtest mode

---

## ▶️ How to Run (Dev)

```bash
# 0. Install dependencies
pip install -r backend/requirements.txt

# 1. Activate virtual env
source backend/screener-venv/bin/activate

# 2. Launch scheduler
python3 backend/scheduler.py

# 3. Start FastAPI server
uvicorn backend.main:app --reload --port 8000

# 4. Start frontend
npm run dev
```

---

## 📡 API Endpoints

| Route                   | Purpose                             |
| ----------------------- | ----------------------------------- |
| `/api/autowatchlist`    | Final filtered watchlist            |
| `/api/universe`         | Universe with scores + tier signals |
| `/api/raw`              | Raw enriched data (pre-score)       |
| `/api/sector`           | Sector ETF change + leaders         |
| `/api/cache-timestamps` | File freshness for debug and UI     |

---

## ⚠️ Known Issues

* Enrichment may still occasionally double-flag reasons if signal saves overlap
* TradingView premarket levels pending (needed for Momentum Confluence logic)

---

## 🧪 Experimental Features

* Admin page for manual job control
* Screener config UI (thresholds, logic toggles)
* Sentiment overlays: VIX/VVIX/SPY trends
* Institutional block trade scanning

---

> Built for speed. Modular by design. Validate before trading.
> *“Momentum belongs to the prepared.”* 🔍
