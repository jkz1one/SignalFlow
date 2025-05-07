
# ✅ Screener Automation System – Updated Goals (May 2025)

## 1. **Enrichment Watchdog Logic**
- **Current Behavior**: `enrich_watchdog.py` triggers `enrich_universe.py` **only** when new cache inputs (e.g., `post_open_signals.json`, `945_signals.json`) appear or change.
- **What’s Next**:
  - [ ] **Append** `screenbuilder.py` and `watchlist_builder.py` as post-enrichment steps inside `enrich_watchdog.py`.
    - This makes the system “live-update” the screener anytime enrichment is refreshed.
  - [ ] Add a log statement:  
    `"✅ Enrichment complete — running screener + watchlist builders..."`

---

## 2. **Universe Builder Automation vs. Manual Frontend Control**

You now have two possible paths for handling `universe_builder.py`:

### Option A: Automated Daily Run (Backend-Controlled)
- **Pros**: Fully hands-off, always fresh.
- **Cons**: Requires stable CSV source, logic can’t be tuned easily without code changes.

### Option B: Manual via Admin Panel (Frontend-Controlled)
- **Pros**: Lets you configure filters like `min cap`, `volume`, or anchor tickers from the frontend.
- **Cons**: Adds a UI step, requires logic to persist user config.

**Decision:**  
- [ ] Decide if you're pursuing **Option A (automation)** or **Option B (manual UI-based universe control)**  
- If **A**, add to daily scheduler at 4:00 AM  
- If **B**, build admin config schema and store to disk (`universe_config.json`)

---

## 3. **runner.py Refactor**
- Add flexible flags to modularize your runs:
  ```bash
  python runner.py --step scrape
  python runner.py --step enrich
  python runner.py --step build
  python runner.py --step full
  ```
- [ ] Parse flags using `argparse`
- [ ] Internally call the correct sequence for each flag

---

## 4. **Daily Automation Schedule (Suggested Triggers)**

| Time (ET) | Task |
|-----------|------|
| 04:00 AM  | `universe_builder.py` *(if auto)* + clear stale cache |
| 09:35 AM  | `post_open_signals.py` |
| 09:45 AM  | `945_signals.py` |
| 09:46 AM+ | `enrich_watchdog.py` auto-triggers full refresh: enrichment → screener → watchlist |

---

## 5. **Fail-Safe & Logging**
- [ ] Log each enrichment run with timestamp + signal freshness report
- [ ] Add sanity check: if < X tickers enriched, warn: `"⚠️ Low output: only N tickers enriched. Possible signal delay or universe issue."`
- [ ] (Future) Trigger Discord/email alert if critical failure
