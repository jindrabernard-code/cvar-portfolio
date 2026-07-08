# Data Legend — Topic 2: CVaR-Constrained Portfolio Optimization for Czech/CEE Equities

Generated: 2026-07-03 | Period covered: 2015-01-01 – 2024-12-31

---

## Overview

All data was collected automatically via `collect_data.py` from free, publicly accessible sources.
No paid data subscriptions required.

---

## 1. Equity Prices — `data/equities/`

**Purpose:** Daily adjusted closing prices for individual stocks in the CEE universe.  
**Format:** CSV, index = `date` (YYYY-MM-DD), single column `adj_close` (local currency, split- and dividend-adjusted).  
**Source:** Yahoo Finance via `yfinance` library (free, no registration).  
**Frequency:** Daily (business days); some tickers follow local exchange holidays.  
**Currency note:** Prices are in local currency (CZK for .PR, PLN for .WA, HUF for .BD, EUR for .VI).
Apply FX rates from `data/fx/` to express all returns in a common currency.

### Czech Republic — Prague Stock Exchange (PSE / Burza)

| File | Company | Sector | Rows | Notes |
|---|---|---|---|---|
| `CEZ.PR.csv` | ČEZ a.s. | Utilities / Electricity | 2,504 | Dominant Czech power company; nuclear + coal + renewables |
| `KOMB.PR.csv` | Komerční banka | Banking | 2,504 | Czech retail/corporate bank; majority-owned by Société Générale |
| `MONET.PR.csv` | Moneta Money Bank | Banking | 1,993 | Czech retail bank; IPO May 2016 — data from 2016-05 only |
| `TABAK.PR.csv` | Philip Morris ČR | Consumer Staples | 2,504 | Czech subsidiary of Philip Morris International (PMI) |
| `VIG.PR.csv` | Vienna Insurance Group | Insurance | 2,504 | Austrian insurer; Prague dual-listed |
| `O2CR.PR.csv` | O2 Czech Republic | Telecom | 1,790 | PSE API (`download_pse_equities.py`); **raw close, not dividend-adjusted**; delisted Feb 2022 — data 2015-01 – 2022-02 |
| `COLT.PR.csv` | Colt CZ Group | Industrials | 1,151 | PSE API (`download_pse_equities.py`); **raw close, not dividend-adjusted**; listed Jun 2020 — data 2020-06 – 2024-12 |

### Poland — Warsaw Stock Exchange (GPW)

| File | Company | Sector | Rows | Notes |
|---|---|---|---|---|
| `PKN.WA.csv` | PKN Orlen | Energy (Oil & Gas) | 2,549 | Polish oil refiner & petrol station operator |
| `PKO.WA.csv` | PKO Bank Polski | Banking | 2,549 | Largest Polish bank by assets |
| `PZU.WA.csv` | PZU S.A. | Insurance | 2,549 | Largest Polish insurer; also manages pension assets |
| `KGH.WA.csv` | KGHM Polska Miedź | Materials (Mining) | 2,549 | Major copper & silver producer; high commodity-price sensitivity |
| `LPP.WA.csv` | LPP S.A. | Consumer Discretionary | 2,549 | Polish fast-fashion retailer (Reserved, Mohito, Cropp brands) |
| `CDR.WA.csv` | CD Projekt | Technology / Gaming | 2,549 | Game developer; massive volatility around Cyberpunk 2077 (2020) |
| `PEO.WA.csv` | Bank Pekao | Banking | 2,549 | Polish universal bank; major shareholders: PZU, BGK |
| `ALE.WA.csv` | Allegro.eu | Technology / E-commerce | 1,056 | Polish e-commerce giant; IPO October 2020 — partial data only |

### Hungary — Budapest Stock Exchange (BÉT)

| File | Company | Sector | Rows | Notes |
|---|---|---|---|---|
| `OTP.BD.csv` | OTP Bank | Banking | 2,537 | Dominant Hungarian bank; significant CEE regional presence |
| `MOL.BD.csv` | MOL Group | Energy (Oil & Gas) | 2,537 | Hungarian integrated O&G; refining + retail + E&P |
| `RICHTER.BD.csv` | Gedeon Richter Plc | Healthcare (Pharma) | 2,537 | Hungarian pharmaceutical; main export markets: CIS + EU |

### Austria — Vienna Stock Exchange (Wiener Börse)

| File | Company | Sector | Rows | Notes |
|---|---|---|---|---|
| `EBS.VI.csv` | Erste Group Bank | Banking | 2,512 | Austrian bank; dominant retail/commercial bank in CZ, SK, HR, RO |
| `OMV.VI.csv` | OMV AG | Energy (Oil & Gas) | 2,512 | Austrian integrated O&G; significant refining in CZ (Litvínov via Unipetrol) |
| `VER.VI.csv` | Verbund AG | Utilities / Electricity | 2,512 | Austrian hydropower company; major renewable electricity exporter |
| `RBI.VI.csv` | Raiffeisen Bank International | Banking | 2,512 | Austrian bank; strong presence in CZ, PL, HU, RU (partial 2022 exposure) |

### Corporate Actions & Adjustments
- All prices are **adjusted close** (split-adjusted and dividend-adjusted) as provided by Yahoo Finance.
- For the CVaR optimization, use **log returns**: `r_t = ln(P_t / P_{t-1})`.
- Handle missing trading days (holidays differ by exchange) using `dropna()` or `ffill()` before computing returns.

---

## 2. Benchmark Indices — `data/indices/`

**Purpose:** Market-level benchmarks for performance comparison.  
**Format:** CSV, index = `date`, column `close`.  
**Source:** Yahoo Finance via `yfinance` (free).

| File | Index | Exchange | Rows | Notes |
|---|---|---|---|---|
| `ATX.csv` | ATX | Vienna (Wiener Börse) | 2,499 | 20 largest Austrian stocks by free-float |
| `BUX.csv` | BUX | Budapest (BÉT) | 1,623 | Hungarian blue-chip index; OTP, MOL, RICHTER dominant |
| `STOXX50E.csv` | Euro Stoxx 50 | Pan-European | 2,514 | 50 largest Eurozone companies; systemic risk benchmark |
| `GDAXI.csv` | DAX 40 | Frankfurt (XETRA) | 2,537 | German blue-chip; CZ equities historically correlated with DE |
| `GSPC.csv` | S&P 500 | New York (NYSE/NASDAQ) | 2,515 | Global risk-off benchmark |
| `PX.csv` | PX | Prague (PSE) | 2,504 | Official PSE API (`download_indices.py`); daily closing values |
| `WIG20.csv` | WIG20 | Warsaw (GPW) | 2,500 | GPW Benchmark chart API (`download_indices.py`); daily closing values |

---

## 3. FX Rates — `data/fx/`

**Purpose:** Convert equity returns to a common currency (EUR or CZK) for portfolio analysis.  
**Format:** CSV, index = `date`, single column = exchange rate.  
**Source:** ECB Statistical Data Warehouse (SDW), series EXR — daily spot fixing (CC BY 4.0).  
**Frequency:** Daily (business days, ECB fixing ~14:15 CET).  
**Rows:** 2,561 per currency pair (2015–2024).

| File | Pair | Column | Convention | Notes |
|---|---|---|---|---|
| `CZK_EUR.csv` | CZK per EUR | `CZK_EUR` | Foreign/EUR, i.e., 25.0 means 1 EUR = 25 CZK | Typical range: 24–28 CZK/EUR |
| `PLN_EUR.csv` | PLN per EUR | `PLN_EUR` | Foreign/EUR | Typical range: 4.0–4.8 PLN/EUR |
| `HUF_EUR.csv` | HUF per EUR | `HUF_EUR` | Foreign/EUR | Typical range: 290–420 HUF/EUR; high volatility 2022 |
| `USD_EUR.csv` | USD per EUR | `USD_EUR` | Foreign/EUR | Useful for USD-denominated global factors |

**Usage in analysis:** To convert a CZK stock return to EUR:  
`r_EUR = r_CZK - Δ(CZK/EUR) / (CZK/EUR)` (approximate, exact version uses log differences).

---

## 4. Risk-Free Rates — `data/rates/`

**Purpose:** Baseline risk-free rate for Sharpe/Sortino ratio computation and the CVaR optimization benchmark.

| File | Description | Source | Frequency | Rows | Range |
|---|---|---|---|---|---|
| `pribor_3m.csv` | Czech Republic short-term interbank rate proxy (FRED `IRSTCI01CZM156N`) | FRED / IMF | Monthly | 120 | 0.0%–7.2% (2015-2024); near-zero 2015-2018, rising 2022-2023 |
| `ester.csv` | Euro Short-Term Rate (€STR), replaces EONIA | ECB SDW `EST/B.EU000A2X2A25.WT` | Daily | 1,347 | -0.6% to +3.9%; available from Oct 2019 |
| `cz_10y_gov_bond.csv` | Czech 10-Year Government Bond Yield | FRED `IRLTLT01CZM156N` | Monthly | 120 | 0.25%–5.52% (peaked 2022-2023 energy crisis) |

**Notes on PRIBOR proxy:**  
The FRED series `IRSTCI01CZM156N` is the Czech Republic's immediate interbank call money rate. It closely tracks PRIBOR O/N (overnight) rather than 3M. The actual PRIBOR 3M can be obtained from ČNB ARAD system at https://www.cnb.cz/en/statistics/financial-market-supervision-statistics/ (search for PRIBOR). For most portfolio analysis purposes this proxy is adequate; forward-fill monthly values to daily.

---

## 5. Summary Statistics

| Category | Count | Coverage | Primary Use |
|---|---|---|---|
| CEE equities | 22 stocks | 2015-2024 (partial: MONET from 2016, ALE from 2020, COLT from 2020-06, O2CR until 2022-02) | Portfolio weights, return distributions |
| Benchmark indices | 7 (ATX, BUX, STOXX50E, DAX, S&P500, PX, WIG20) | 2015-2024 | Performance comparison |
| FX rates | 4 pairs | 2015-2024 (2,561 trading days each) | Currency normalization |
| Risk-free rates | 3 series | 2015-2024 (monthly; €STR from 2019) | Sharpe/Sortino denominator |
| **Total CSV files** | **36** | — | — |

---

## 6. Missing / Manual Data

| Data | Why Missing | Manual Download |
|---|---|---|
| PRIBOR 3M (exact) | ČNB ARAD API returned no data in this run; FRED proxy used instead | https://www.cnb.cz/en/statistics/financial-market-supervision-statistics/financial-markets/money-market-statistics/ |

Previously missing series that are now collected automatically:
- **PX, WIG20** — `download_indices.py` (PSE API + GPW Benchmark API)
- **O2CR.PR, COLT.PR** — `download_pse_equities.py` (PSE API; raw close, not dividend-adjusted)

---

## 7. Data Pipeline

```
collect_data.py
├── collect_equities()  →  Yahoo Finance (yfinance)
├── collect_indices()   →  Yahoo Finance (yfinance)
├── collect_fx()        →  ECB SDW REST API (JSON/CSV)
└── collect_rates()     →  FRED REST API (CSV)

download_indices.py       →  PX (PSE API), WIG20 (GPW Benchmark API)
download_pse_equities.py  →  O2CR.PR, COLT.PR (PSE API)
```

Re-run with `python collect_data.py` — already-existing files are skipped automatically.
