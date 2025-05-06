# Screener 3.7 – Audit Summary
_Last Updated: 2025-04-30_

---

## Overview

This audit summary outlines the current backend and automation structure of the Screener 3.7 project. It includes core pipeline structure, cache behavior, enrichment dependencies, scraper timing concerns, potential inefficiencies, and recommendations.

---

## 1. Core Pipeline Structure

The screener system has two main scripts:

- **`daily_refresh.py`**: Fetches and builds all required data.
- **`run_pipeline.py`**: Validates cache, runs cache manager, scores tickers, builds watchlist.

These can be thought of as **Refresh (data pull)** and **Build (scoring/output)**. For full daily function, both are required.

---

## 2. Automation Timing Model

Some scrapers depend on specific time windows:

| Script                        | Recommended Run Time (ET) | Reason |
|------------------------------|----------------------------|--------|
| `scrape_tv_signals.py`       | **After 9:30 AM**          | Needs open data for price, volume, change% |
| `scraper_candles_5m.py`      | **After 9:40 AM**          | 9:30–9:40 range logic needs full 10 mins |
| `fetch_multi.py`             | **Anytime after 4:00 AM**  | Multi-day levels based on close data |
| `fetch_short_interest.py`    | **Once daily after release** | Semi-monthly updates (from FINRA/Nasdaq) |
| `scrape_sector_prices.py`    | **After 9:30 AM**          | Price and prevClose are needed |

### Enrichment Dependency Model:
- `enrich_universe.py` must run **after** all of the above scrapers.
- Alternatively: `enrich_universe.py` could be **re-run after each update** to build live composite cache.

---

## 3. Cache Management

The project uses `cache_manager.py` to clean old files and audit the cache directory.

### Key Improvements:
- NYSE calendar logic (via `pandas_market_calendars`) used to define “today” on weekends/holidays
- Risk of accidental cache deletion minimized by fallback mod-time checks

---

## 4. Structure Review – Old / Unused Files

### Possibly Deprecated or Unused:
- `yf_enrichment.py`: YFinance enrichment no longer used directly; logic has moved to TV-based pipeline
- `old_universe_builder.py`: Superseded by new `backend/signals/universe_builder.py`
- Manual copies of scored or enriched files with hardcoded names — replace with dynamic naming and cache manager logic

---

## 5. Opportunities for Improvement

### Structural:
- Move enrichment logic into modular, on-demand functions to reduce re-processing
- Consider combining scrape + enrich phases into one reactive system (e.g., run enrich after each scraper)

### Performance:
- Use `.pkl` or compressed formats for large JSONs if slowness arises
- Explore `asyncio` or batching if real-time scraping is eventually desired

### Future Automation:
- Support `cron` or `APScheduler` automation for:
  - Daily refresh (before 9:30 AM)
  - Enrichment re-runs
  - Optional risk audits or output exports

---

## 6. Scope & Goal Additions

**Current System Supports:**
- Tiered scoring
- Risk filters
- 5m candles / sector ETF logic
- Fully styled watchlist frontend
- Universe builder with static anchors

**Possible Goal Additions:**
- Admin panel to manually add/pin tickers to universe
- Auto-trigger `enrich_universe` after each scraper
- UI toggle or log to show cache freshness per file
- Realtime GEX or options flow overlay (future tier)

---

## Summary

The Screener 3.7 backend is structurally sound and modular, with excellent logging, cache logic, and signal enrichment. Some scrapers depend on time, so a hybrid or sequenced automation model is recommended.

The frontend is mostly stable, with potential issues around broken risk toggles. Audit and cleanup routines are well-handled, but minor simplifications (e.g., avoiding redundant cache manager calls) will help polish the final product.
