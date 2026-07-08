# CVaR Portfolio Optimization — CEE Equities Data Collection

*CVaR-Based Portfolio Optimization for Central and Eastern European Equity Markets*

## Contents

| File / Folder | Description |
|---|---|
| `collect_data.py` | Data collection script (Yahoo Finance, ECB SDW, FRED) |
| `download_indices.py` | PX + WIG20 from official exchange APIs (PSE, GPW Benchmark) |
| `download_pse_equities.py` | O2CR.PR + COLT.PR from the PSE public API |
| `build_panel.py` | Merges all sources into a single daily panel CSV |
| `requirements.txt` | Python dependencies |
| `data/equities/` | Close prices for 22 CEE stocks (2015–2024) |
| `data/indices/` | Benchmark indices: ATX, BUX, STOXX50E, DAX, S&P500, PX, WIG20 |
| `data/fx/` | FX rates: CZK/EUR, PLN/EUR, HUF/EUR, USD/EUR (ECB SDW) |
| `data/rates/` | Risk-free rates: PRIBOR proxy, €STR, CZ 10Y gov bond |
| `data/cvar_portfolio_panel.csv` | **Merged daily panel — 3,653 rows × 58 columns** |
| `data/DATA_LEGEND.md` | Full documentation of all variables, units, sources |

## Quick Start

```bash
pip install -r requirements.txt
python collect_data.py           # downloads Yahoo/ECB/FRED data (~2 min)
python download_indices.py       # PX + WIG20 (official exchange APIs, ~3 min)
python download_pse_equities.py  # O2CR.PR + COLT.PR (PSE API, ~3 min)
python build_panel.py            # builds the merged panel with EUR log-returns
```

## Panel Variables (58 columns)

- **Local prices:** `{TICKER}_local` — close in local currency (22 stocks)
- **EUR log-returns:** `{TICKER}_ret_eur` — daily log-return converted to EUR
- **FX rates:** CZK/EUR, PLN/EUR, HUF/EUR, USD/EUR (ECB daily fixing)
- **Indices:** ATX (Vienna), BUX (Budapest), STOXX50E, DAX, S&P500, PX (Prague), WIG20 (Warsaw)
- **Risk-free rates:** PRIBOR 3M proxy, €STR, CZ 10Y government bond yield

## Data Notes

- `O2CR.PR` (delisted 2022-02) and `COLT.PR` (listed 2020-06) come from the PSE API
  as **raw closing prices** (not dividend-adjusted, unlike the Yahoo series).
- `PX` comes from the official PSE API; `WIG20` from GPW Benchmark (index administrator).
- Exact PRIBOR 3M still requires manual download from ČNB ARAD (FRED proxy included).
