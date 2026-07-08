# PX Index & WIG20 — Manual Download Instructions

> **RESOLVED (2026-07-08):** Both indices are now downloaded automatically by
> `download_indices.py` — PX via the official PSE API
> (`www.pse.cz/api/indexes`, paginated) and WIG20 via the GPW Benchmark chart
> API (`gpwbenchmark.pl/chart-json.php`, full daily archive). `PX.csv` and
> `WIG20.csv` exist in this folder and are already merged into
> `cvar_portfolio_panel.csv`. The manual instructions below are kept as a fallback.

Both indices are unavailable via Yahoo Finance (confirmed: all tickers return empty).
Download manually from the official exchange websites below.

---

## PX Index (Prague Stock Exchange)

**What to download:** Daily closing values, 2015-01-01 to 2024-12-31

### Source 1 — Prague Stock Exchange (official, recommended)
1. Go to: https://www.pse.cz/udaje-o-trhu/indexy/px/historicke-hodnoty
2. Set date range: 2015-01-01 → 2024-12-31
3. Click "Stáhnout jako CSV" or export button
4. Save as: `PX.csv` in this folder (`data/indices/`)

**Is the key data enough?**
For the CVaR portfolio optimisation, the PX index serves as the **Czech benchmark** for:
- Beta computation (sensitivity of Czech stocks to the local market)
- Sharpe ratio benchmarking
- Portfolio performance attribution

Without it you can still run CVaR optimisation (it only needs the asset returns), but you cannot benchmark against the Czech market. **Download it** — it takes 2 minutes.

**Required column format:**
```
date,PX
2015-01-02,986.4
2015-01-05,981.2
...
```

---

## WIG20 Index (Warsaw Stock Exchange)

**What to download:** Daily closing values, 2015-01-01 to 2024-12-31

### Source 1 — GPW Warsaw Stock Exchange (official)
1. Go to: https://gpw.pl/wskazniki-historyczne?isin=PL9999999987
2. Select range 2015–2024
3. Export as CSV/Excel
4. Save as: `WIG20.csv` in this folder

### Source 2 — Stooq.com (direct CSV link)
Open this URL in your browser (may work depending on network):
https://stooq.com/q/d/l/?s=%5Ewig20&d1=20150101&d2=20241231&i=d
Save the downloaded file as `WIG20.csv`

### Source 3 — Investing.com
1. Go to: https://www.investing.com/indices/wig20-historical-data
2. Set date range 2015–2024
3. Download CSV
4. Rename to `WIG20.csv`

**What data to download from WIG20:**
- **Daily closing price** (index level, not price/share — WIG20 is a point value)
- **Date range:** 2015-01-01 to 2024-12-31
- **Frequency:** Daily (business days)
- You do NOT need volume, open, high, low — just the closing level for return computation

**Required column format:**
```
date,WIG20
2015-01-02,2324.57
2015-01-05,2298.41
...
```

---

## After Download — Integration into Panel

Once downloaded, place both files in `data/indices/`
and re-run `build_panel.py` — it will automatically pick them up and include them
in `cvar_portfolio_panel.csv`.
