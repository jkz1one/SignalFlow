# ✅ Stock Screener v3.7

> **Status:** Stable daily-use build  
> **Next Phase:** Universe Builder + Scheduled Automation  
> **Further Phases:** Sector Tab + Admin Panel + Frontend Timestamp + Screener Builder  
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
- 5-minute candle scraper (930–940 range)  
- Short interest loader from FINRA/Nasdaq  
- Multi-day high/low scraper  
- `enriched_timestamp` injected into universe  
- Removed deprecated `yfinance_updated` field  
- Universe enrichment and scoring validated  
- AutoWatchlist builder + frontend rendering  

### Backend Architecture
- `run_pipeline.py` orchestrates refresh → score → build  
- `daily_refresh.py` wraps all scrapers with cleanup and audit  
- `cache_manager.py` handles cleanup (uses last valid market day logic)  
- Modular `signals/` folder with all enrichment logic  
- Universe Builder added (`universe_builder.py`)  
- `watchlist_builder.py` builds filtered, scored JSON output  

---

## 🔄 IN PROGRESS / PARTIAL

- [~] Tier 1: Momentum Confluence (awaiting accurate premarket highs/lows from TradingView)  
- [~] Daily refresh runs manually, but automation flow is staged  
- [~] Universe Builder still uses static anchor lists; partial L1–L3 logic in place  

---

## 🛠️ UPCOMING (v3.7)

### Backend Enhancements
- [ ] Fix UI logic for hiding risk-blocked tickers (AutoWatchlist risk toggle)  
- [ ] Universe Builder v2 with full dynamic CSV → L1–L3 assignment  
- [ ] Risk filter: "No Reliable Price" logic  
- [ ] Add logging for Universe, Scoring, and Watchlist phases  
- [ ] Add per-file timestamps in audit output  

### Automation
- [ ] Add scheduler (APScheduler or cron) to run `daily_refresh.py` and `run_pipeline.py` automatically  
- [ ] Add `runner.py` modular launcher  
- [ ] All scrapers should skip if cache file is up to date (timestamp-based skip)  

### Scraper System
- [ ] Convert all scrapers to callable functions (vs raw scripts)  
- [ ] Add stealth scraping improvements for TradingView  
- [ ] Option to retry or failover on scrape errors  

### Frontend Goals
- [ ] Add Sector Rotation tab view  
- [ ] Add Admin Panel to manually trigger backend refresh  
- [ ] Add cache freshness timestamps per file (badge/UI footer)  
- [ ] Allow user config overrides (e.g., relative volume threshold)  
- [ ] UI toggle for "Top 3 Only" / "Show Blocked"  

---

## 🧪 Long-Term & Advanced

- [ ] Options data analysis (GEX, Vanna, Charm, 0DTE)  
- [ ] Sentiment overlays (SPX vs SPY, QQQ vs NQ, VIX vs VIXY)  
- [ ] Screener builder / rule editor  
- [ ] Alerts + email/export for top picks  
- [ ] Replay backtesting of signal triggers  
- [ ] Same-day, next-day, weekly contract scanner  
- [ ] Institutional flow tracker (block trades, large orders)  
- [ ] Docker container deployment for reproducibility  
