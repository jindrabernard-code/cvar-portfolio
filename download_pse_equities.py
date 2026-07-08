"""
download_pse_equities.py — Missing Prague equities from the PSE public API
==========================================================================
Downloads daily closing prices for the two tickers unavailable on Yahoo:

  COLT.PR  — COLT CZ Group SE     (ISIN CZ0009008942, listed Oct 2020)
  O2CR.PR  — O2 Czech Republic    (ISIN CZ0009093209, delisted mid-2021)

NOTE: the PSE API provides raw closing prices, NOT dividend-adjusted prices
(unlike the yfinance "adj_close" used for the other tickers). Returns computed
from these series therefore exclude the dividend component. The files keep the
same column name (adj_close) so build_panel.py picks them up unchanged.

Usage:  python download_pse_equities.py
Output: data/equities/COLT.PR.csv, data/equities/O2CR.PR.csv
"""

import sys
import time
from pathlib import Path

import pandas as pd
import requests

OUT_DIR = Path(__file__).parent / "data" / "equities"
START, END = "2015-01-01", "2024-12-31"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

TICKERS = {
    "COLT.PR": "CZ0009008942",
    "O2CR.PR": "CZ0009093209",
}


def fetch_isin(isin: str) -> pd.DataFrame:
    rows = []
    page = 1
    session = requests.Session()
    while True:
        for attempt in range(8):
            r = session.get(
                "https://www.pse.cz/api/instruments",
                params={"page": page, "isin": isin,
                        "dateFrom": START, "dateTo": END},
                headers=HEADERS, timeout=30)
            if r.status_code == 429:
                wait = 15 * (attempt + 1)
                print(f"    page {page}: rate-limited, waiting {wait}s ...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            break
        else:
            raise RuntimeError(f"PSE API kept returning 429 at page {page}")
        values = r.json().get("data", {}).get("values", [])
        if not values:
            break
        rows.extend(values)
        if page % 25 == 0:
            print(f"    page {page}  ({len(rows):,} rows, "
                  f"oldest: {values[-1]['stockExchangeDay']})")
        page += 1
        time.sleep(0.4)
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    out = (df[["stockExchangeDay", "closingCourse"]]
           .rename(columns={"stockExchangeDay": "date",
                            "closingCourse": "adj_close"})
           .assign(date=lambda d: pd.to_datetime(d["date"]))
           .dropna()
           .drop_duplicates("date")
           .set_index("date")
           .sort_index())
    return out


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    failures = 0
    for ticker, isin in TICKERS.items():
        print(f"{ticker} ({isin}): downloading from PSE API ...")
        try:
            df = fetch_isin(isin)
        except Exception as exc:
            print(f"  FAILED: {exc}")
            failures += 1
            continue
        if df.empty:
            print(f"  {ticker}: no data returned.")
            failures += 1
            continue
        df.to_csv(OUT_DIR / f"{ticker}.csv")
        print(f"  Saved {len(df):,} rows  {df.index.min().date()} -> "
              f"{df.index.max().date()}")
    return failures


if __name__ == "__main__":
    sys.exit(main())
