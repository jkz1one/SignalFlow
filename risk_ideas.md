# ⚠️ Additional Risk Filter Ideas – Stock Screener v3.7

Expand your risk filtering system with these advanced checks used by pro screeners and institutional workflows:

---

## 🔁 Liquidity & Spread Filters

- **Average Spread %** – Spread relative to price exceeds X% threshold
- **Low Float Risk** – Float < 5M shares
- **Low Market Cap Risk** – Market cap < $300M
- **Low Institutional Ownership** – Indicates potential for instability or manipulation

---

## 📈 Price Action / Behavior Filters

- **No Real Pre-Market Activity** – No trades before 9:25 AM
- **No 1-Minute Volume Spikes** – Avoids tickers manipulated via fake pump activity
- **Frequent Halt History** – Ticker triggered volatility halts recently
- **Illiquid Gaps** – Price gapped up/down without volume confirmation

---

## 🧠 Technical Structure Filters

- **No Clear Trend** – Flat 20/50/200 MAs over last 10 days
- **Inside Candle Choppiness** – Prior day was an inside bar with low range
- **Micro Cap Chop Zone** – Small-cap trading inside tight 1–2% range with no breakout

---

## 📰 News & Catalyst Risk Filters

- **No Fundamental Catalyst** – No earnings, FDA, merger, or relevant event
- **Low News Sentiment** – Pull sentiment score from scraped headlines
- **Fake PR Risk** – Ticker has prior history of misleading press releases

---

## ⚙️ Execution Risk Filters

- **Low Quote Refresh Rate** – Stale quotes, poor Level 2 liquidity
- **No Options Chain** – Lack of options may signal retail-only interest
- **No Dark Pool Interest** – Little or no institutional routing observed

---

## 🧪 Behavioral & Manual Filters

- **Frequent “Rug” Candidate** – Manually flagged for unreliability
- **On Regulatory Watchlist** – Appears on SEC, FINRA, SSR, or other flagged lists

---

> Consider integrating these filters as scoring penalties or hard blocks depending on your screener tier and timeframe. Some may be flagged via scraper logic, others via enrichment metadata.
