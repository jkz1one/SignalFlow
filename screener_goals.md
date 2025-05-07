# ✅ Stock Screener v3.7

> **Status:** Broken/Under Construction  
> **Next Phase:** Universe Builder + Scheduled Automation  
> **Further Phases:** Sector Tab • Admin Panel • Frontend Timestamp • Screener Builder  
>  
> **Tag:** `v3.7-beta`

---

## ✅ COMPLETED

### Tier Logic  
- Tier 1: Gap Up / Gap Down  
- Tier 1: Break Above/Below 9:30–9:40 Range  
- Tier 1: High Relative Volume  
- Tier 2: Early % Move  
- Tier 2: Squeeze Watch  
- Tier 2: Sector Rotation  
- Tier 3: High Volume  
- Tier 3: Top 5 Volume Gainers  
- Tier 3: Near Multi-Day High / Low  
- Tier 3: High Volume, No Breakout  

### Risk Filters  
- Low Liquidity  
- Wide Spread  

### Data & Enrichment  
- TradingView signal scraper merged with yfinance  
- Sector ETF scraper (`sector_etf_prices.json`)  
- 5-minute candle scraper (9:30–9:40 range)  
- Short interest loader from FINRA/Nasdaq  
- Multi-day high/low scraper  
- `enriched_timestamp` added to universe  
- Removed deprecated `yfinance_updated` field  
- Universe enrichment + scoring fully validated  
- AutoWatchlist builder + clean frontend rendering  
- Fixed BRK.B ticker parsing

### Backend Architecture  
- `run_pipeline.py` orchestrates enrich → score → build  
- `daily_refresh.py` wraps all scrapers with cache audit  
- `cache_manager.py` handles cleanup + validation (strict mode optional)  
- Modular `signals/` folder for enrichment layers  
- Universe Builder (`universe_builder.py`) added  
- Watchlist system built with `watchlist_builder.py`

---

## 🔄 IN PROGRESS / PARTIAL

- [~] Tier 1: Momentum Confluence (awaiting reliable premarket highs/lows)  
- [~] Universe Builder still uses static anchors; v2 under development  
- [~] Daily refresh pipeline is still manual; scheduler integration staged  

---

## 🛠️ UPCOMING (v3.7)

### Backend Enhancements  
- [ ] Fix UI logic for hiding risk-blocked tickers (AutoWatchlist risk toggle)  
- [ ] Universe Builder v2: modular anchor logic with optional tagging  
- [ ] Add risk filter: “No Reliable Price”  
- [ ] Add logging for enrichment, scoring, and watchlist stages  
- [ ] Add cache freshness timestamps per file (embedded + visual)  
- [ ] Strip unused dependencies and files  

### Automation  
- [ ] Add scheduler (APScheduler or cron) to automate `daily_refresh.py` + `run_pipeline.py`  
- [ ] Add `runner.py` to manage modular refreshes (scrape-only, score-only, etc.)  
- [ ] Implement timestamp-based skip logic for scrapers if data is fresh  
- [ ] Auto-run `screenbuilder.py` and `watchlist_builder.py` after enrichment  
- [ ] Implement 4:00 AM daily reset via `cache_manager.py`  

### Scraper System  
- [ ] Convert all scrapers to callable Python modules (instead of CLI scripts)  
- [ ] Add stealth/resilience improvements for TradingView scrapes  
- [ ] Add retry + failover options on scraper failures  
- [ ] Fix BRK.B and other special ticker parsing issues  
- [ ] Use updated yfinance 0.2.58+ for more resilient `.info` and `.history()`  

### Frontend Goals  
- [ ] Add dedicated Sector Rotation tab  
- [ ] Add Admin Panel to manually trigger backend refresh  
- [ ] Display per-file cache freshness (e.g., badges, tooltips, footer)  
- [ ] Add user config override system (e.g., rel vol %, volume thresholds)  
- [ ] Add toggle for “Top 3 Only” / “Show Risk-Blocked” tickers  
- [ ] Add frontend timestamp display for enriched file + inputs  

---

## 🚧 Further Improvements (beyond v3.7)

### Modular Screener System  
- [ ] Adopt a **time-based screener framework** (Opening, Swing, Overnight)  
- [ ] Build and maintain separate logic pipelines for each screener type  
- [ ] Add **Admin Panel** for internal overrides + screener-level control  
- [ ] Create unified **Screener Build Page** where users can edit rules, toggle screener types, and adjust logic parameters (e.g., rel vol %, volume thresholds, gap %)  
- [ ] Ensure some **core signals remain shared** across screeners for consistency  
- [ ] Introduce **fundamental signal logic** (e.g., valuation, growth) in Swing + Overnight screeners only  
- [ ] Leave room for future screeners (e.g., Lunch Break, Block Trades, Earnings Flow)
- [ ] Consider adding manual run commands while **Sheduler.py** is actively running. Ie run post open scrape, run enrichment, etc. 

---

## 🧪 Long-Term & Advanced

- [ ] Options data integration (GEX, Vanna, Charm, 0DTE)  
- [ ] Sentiment overlays (SPX vs SPY, QQQ vs NQ, VIX vs VIXY)  
- [ ] Alerts + email/export for top-ranked setups  
- [ ] Replay / backtest signal triggers  
- [ ] Same-day, next-day, and weekly contract scanner  
- [ ] Dynamic Universe Builder with auto-tuned anchors  
- [ ] Institutional order tracker (block trades, sweeps, etc.)  
- [ ] Docker deployment for reproducibility + scale  
