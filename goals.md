# 📈 Screener 3.7 – Final Roadmap (Pre-Deployment)

This is the deployment-ready roadmap for Screener 3.7, categorized by system section. Each block is collapsible for easier viewing.

---

<details open>
<summary>📊 <strong>Stock Tracker</strong></summary>

1. Improve chart timestamps to show actual hour + minute, not just date.  
2. Symbol suggest in Stock Tracker — dropdown with fuzzy search.  
3. Dropdown for recent tickers on Stock Tracker.  
4. Add toggleable overlays and indicators:
   - Volume bars  
   - Moving averages  
   - RSI  
   - Visual range volume profile  
5. Add dedicated backend middleware to handle chart-related fetches/calculations.  
6. Speed up chart data updates (via frontend polling or smarter middleware).  
7. Add toggleable horizontal lines for:
   - Premarket High / Low  
   - Previous Day High / Low  
   - Opening Range  
8. Allow for drawing trendlines (manual annotations).  
9. Click-through from Screener/Auto-Watchlist to Stock Tracker or chart page.  
10. Create dedicated chart page (large fullscreen view, separate route).  

</details>

---

<details>
<summary>🧠 <strong>Screener / Auto-Watchlist</strong></summary>

1. Fix frontend risk filters:
   - Rework enrich/scoring pipeline to optionally output both raw and risk-adjusted scores.  
2. Clarify tier logic hits on frontend:
   - e.g. show actual breakout range for “Break Above Range”.  
3. Hover tooltips on tier hits — expose exact thresholds or values.  
4. Make screener logic parameters dynamic and frontend-configurable.  
5. Make screener logic modular to support multiple screener types:
   - Opening, Lunchtime, Swing, etc.  
6. Admin config panel for screener — control logic, thresholds, presets.  
7. Add small inline sparkline next to each stock (1-day or 5m preview).  
8. Grid view toggle for Screener/Auto-Watchlist — compact grid vs list layout.  
9. Log top 3–5 watchlist stocks per day and track post-signal performance.  
10. Trigger frontend auto-refresh when `/api/autowatchlist` updates.  
11. Click-through from expanded dropdown to open Stock Tracker or chart.  
12. Audit screener logic for effectiveness.  
13. Try to improve or finalize momentum logic (or deprecate cleanly).  

</details>

---

<details>
<summary>🧩 <strong>Other / UI / System</strong></summary>

1. Make default app page persist — restore last visited tab on reload.  
2. Refine Global Context Bar:
   - Better UI hint/clickable area for row toggle.  
3. Improve marquee behavior on idle:
   - Smooth scrolling, loop reset, no layout jump.  

</details>

---

<details>
<summary>🛠 <strong>Deployment & Admin Tools</strong></summary>

1. Cache File Debug Panel (dev only, future part of admin panel).  
2. API Status Checker Route — returns freshness of all key cache files.  
3. Error fallback UI — graceful frontend messages if fetch or enrichment fails.  
4. Minimize API payloads — trim unused keys in `/api/tracker`, `/api/scored`, etc.  
5. Strengthen logging and expose logs in frontend admin panel (live or cached).  
6. Add on-demand Discord Bot for querying watchlist, tracker data, or triggering refresh from Discord channel.  

</details>
