# 📊 Stock Screener 3.7 – Momentum & Risk-Aware Watchlist Builder

A real-time stock scanning tool that builds a tiered watchlist using volume, price action, sector rotation, and risk filters. Built with FastAPI + Next.js.

Currently optimized for identifying momentum setups at market open.
---
![example](https://github.com/user-attachments/assets/97ff525c-fe60-4af3-8952-d913e9e46a75)

# 🚧 THIS VERSION IS UNDER CONSTRUCTION FOR AUTOMATION. IT IS BROKEN 🚧
## Use the stable branch instead

## 🛠️ Main Branch Fixes To Do List

- [ ] **Ensure screener resets cleanly at 4:00 AM:**  
  – Prevent any ticker data from populating before the scheduler runs.  
  – Avoid pre-4:00 AM enrichment or early data pollution.  
  – Use `cache_manager.py` to clear stale or previous-day files.

- [ ] **Make `enrich_universe.py` incremental and resilient:**  
  – Allow partial enrichment as new data becomes available.  
  – Gracefully handle missing or delayed files (e.g., `post_open_signals.json`).  
  – Skip or defer enrichment if run before 9:36 AM.

- [ ] **Make `screenbuilder.py` incremental and scheduler-aware:**  
  – Allow scoring only when relevant signals are present.  
  – Ensure it runs automatically after enrichment via scheduler or watchdog.  
  – Avoid running if required data is missing.

- [ ] **Finalize and validate the full automation flow:**  
  – Ensure all scripts run in correct sequence.  
  – Implement timing safeguards and file dependency checks.  
  – Build scheduler or watchdog logic to manage the full pipeline reliably.

---

## ✅ Project Goals – v3.7

### Completed
- ✅ Tier 1, 2, and 3 signal logic implemented
- ✅ Risk filters (liquidity, spread)
- ✅ Enrichment: TV price/vol, candles, short interest, multi-day highs
- ✅ Cache cleaner + audit tools
- ✅ Watchlist scoring + tagging + filtering
- ✅ `run_pipeline.py` orchestrates full system
- ✅ Fixed Cache Manager.

### In Progress
- ⏳ Tier 1 Momentum Confluence (waiting for TradingView premarket levels)
- ⏳ Scheduler for full daily automation
- ⏳ Frontend timestamp display + Sector Tab

### Next Steps
- [ ] Finish Universe Builder v2.
- [ ] Fix frontend risk toggle logic
- [ ] Add Admin Panel to trigger backend jobs
- [ ] Add customizable thresholds (e.g., rel vol min)
- [ ] Add sector rotation view + GEX system (future)
- [ ] Fix error for stocks with periods/dashes (e.g.,BRK.B)
- [ ] Automate Data Pulls
- [ ] Add Discord and/or Email Alerts 

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