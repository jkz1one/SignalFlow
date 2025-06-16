# Screener 3.7 – Final Roadmap (Pre-Deployment)

---

## STOCK TRACKER

1. Fix chart timestamps — show actual hour + minute  
2. Add symbol suggest dropdown with fuzzy search  
3. Add recent tickers dropdown  
4. Add toggleable overlays: volume bars, moving averages, RSI, volume profile  
5. Add backend middleware to handle chart fetches/calculations  
6. Speed up chart data updates (polling or optimized middleware)  
7. Add toggleable lines for premarket high/low, prev day high/low, opening range  
8. Allow manual annotations (trendline drawing)  
9. Create fullscreen chart page (separate route)  

**✅  Completed:**
10. Cache last used chart time frame for next load  ✓

---

## SCREENER / AUTO-WATCHLIST

1. Fix frontend risk filters: support raw + adjusted scores  
2. Make screener parameters dynamic and frontend-configurable  
3. Modularize screener logic to support multiple screener types (Opening, Lunchtime, Swing, etc.)  
4. Add admin config panel for screener logic + threshold overrides  
5. Add sparkline previews (1-day or 5m inline chart)  
6. Add grid vs list toggle layout for watchlist  
7. Auto-refresh frontend when `/api/autowatchlist` updates  
8. Log top 3–5 watchlist stocks per day  
9. Track post-signal performance  
10. Audit screener logic effectiveness  
11. Finalize or remove momentum logic  

**✅  Completed:**
12. Show actual breakout range values on frontend  ✓
13. Add hover tooltips to tier hits  ✓
14. Click-through from expanded ticker to Stock Tracker  ✓

---

## UI / SYSTEM

1. Persist last active tab on app reload  
2. Improve Global Context Bar:  
   a. Better toggle hint area  
   b. Smooth marquee loop with clean reset, no layout jump  

---

## DEPLOYMENT / ADMIN TOOLS

1. Add cache debug panel (dev-only)  
2. Add API status checker route (shows freshness of key cache files)  
3. Add error fallback UI (for fetch/enrichment failures)  
4. Minimize API payloads (remove unused keys from `/api/tracker`, `/api/scored`, etc.)  
5. Strengthen logging + expose logs in admin panel (live or cached)  
6. Add on-demand Discord bot:  
   a. Query watchlist / tracker  
   b. Trigger refresh from Discord  
