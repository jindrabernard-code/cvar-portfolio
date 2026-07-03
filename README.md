# CVaR Portfolio Optimization — CEE Equities Data Collection

**Master's Thesis — Topic 2**  
*CVaR-Based Portfolio Optimization for Central and Eastern European Equity Markets*

## Contents

| File / Folder | Description |
|---|---|
| `collect_data.py` | Data collection script (Yahoo Finance, ECB SDW, FRED) |
| `build_panel.py` | Merges all sources into a single daily panel CSV |
| `requirements.txt` | Python dependencies |
| `data/equities/` | Adjusted close prices for 20 CEE stocks (2015–2024) |
| `data/indices/` | Benchmark indices: ATX, BUX, STOXX50E, DAX, S&P500 |
| `data/fx/` | FX rates: CZK/EUR, PLN/EUR, HUF/EUR, USD/EUR (ECB SDW) |
| `data/rates/` | Risk-free rates: PRIBOR proxy, €STR, CZ 10Y gov bond |
| `data/topic2_panel.csv` | **Merged daily panel — 3,653 rows × 52 columns** |
| `data/DATA_LEGEND.md` | Full documentation of all variables, units, sources |

## Quick Start

```bash
pip install -r requirements.txt
python collect_data.py      # downloads all data (~2 min)
python build_panel.py       # builds the merged panel with EUR log-returns
```

## Panel Variables (52 columns)

- **Local prices:** `{TICKER}_local` — adjusted close in local currency (20 stocks)
- **EUR log-returns:** `{TICKER}_ret_eur` — daily log-return converted to EUR
- **FX rates:** CZK/EUR, PLN/EUR, HUF/EUR, USD/EUR (ECB daily fixing)
- **Indices:** ATX (Vienna), BUX (Budapest), STOXX50E, DAX, S&P500
- **Risk-free rates:** PRIBOR 3M proxy, €STR, CZ 10Y government bond yield

## Notes on Missing Data

- `O2CR.PR`, `COLT.PR` — not available via Yahoo Finance; download from [pse.cz](https://www.pse.cz)
- `PX` index — download from [pse.cz/udaje-o-trhu/indexy/px](https://www.pse.cz/udaje-o-trhu/indexy/px/historicke-hodnoty)
- `WIG20` — download from [gpw.pl](https://gpw.pl/wskazniki-historyczne?isin=PL9999999987)

See `data/indices/INDEX_DOWNLOAD_INSTRUCTIONS.md` for full details.
