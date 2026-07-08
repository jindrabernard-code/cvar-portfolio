"""
download_indices.py — PX and WIG20 daily index histories (official sources)
===========================================================================
PX     : Prague Stock Exchange public API   (www.pse.cz/api/indexes, paginated)
WIG20  : GPW Benchmark chart API            (gpwbenchmark.pl/chart-json.php)

Both are the official index administrators, so these are primary-source data.

Usage:  python download_indices.py
Output: data/indices/PX.csv   (date, PX     — daily closing values)
        data/indices/WIG20.csv(date, WIG20  — daily closing values)
"""

import json
import sys
import time
from pathlib import Path

import pandas as pd
import requests

OUT_DIR = Path(__file__).parent / "data" / "indices"
START, END = "2015-01-01", "2024-12-31"

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/126.0.0.0 Safari/537.36"),
    "Accept": "application/json, text/plain, */*",
}


def download_px() -> bool:
    """Paginate the PSE indexes API (10 rows per page, newest first)."""
    print("PX: downloading from Prague Stock Exchange API ...")
    rows = []
    page = 1
    session = requests.Session()
    while True:
        for attempt in range(8):
            r = session.get(
                "https://www.pse.cz/api/indexes",
                params={"page": page, "indexName": "PX",
                        "dateFrom": START, "dateTo": END},
                headers=HEADERS, timeout=30)
            if r.status_code == 429:
                wait = 15 * (attempt + 1)
                print(f"  page {page}: rate-limited, waiting {wait}s ...")
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
            print(f"  page {page}  ({len(rows):,} rows so far, "
                  f"oldest: {values[-1]['stockExchangeDay']})")
        page += 1
        time.sleep(0.4)           # be polite to the API

    if not rows:
        print("  PX: no data returned.")
        return False

    df = pd.DataFrame(rows)
    out = (df[["stockExchangeDay", "closingValue"]]
           .rename(columns={"stockExchangeDay": "date", "closingValue": "PX"})
           .assign(date=lambda d: pd.to_datetime(d["date"]))
           .drop_duplicates("date")
           .set_index("date")
           .sort_index())
    out.to_csv(OUT_DIR / "PX.csv")
    print(f"  PX: saved {len(out):,} rows  {out.index.min().date()} -> "
          f"{out.index.max().date()}")
    return True


def download_wig20() -> bool:
    """Full daily archive from GPW Benchmark (official WIG index administrator)."""
    print("WIG20: downloading from GPW Benchmark ...")
    req = json.dumps([{"isin": "PL9999999987", "mode": "ARCH",
                       "from": None, "to": None}])
    r = requests.get(
        "https://gpwbenchmark.pl/chart-json.php",
        params={"req": req, "t": int(time.time() * 1000)},
        headers={**HEADERS,
                 "Referer": "https://gpwbenchmark.pl/karta-indeksu?isin=PL9999999987"},
        timeout=60)
    r.raise_for_status()
    payload = json.loads(r.text.strip())
    data = payload[0].get("data", [])
    if not data:
        print("  WIG20: empty response.")
        return False

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["t"], unit="s").dt.normalize()
    out = (df[["date", "c"]]
           .rename(columns={"c": "WIG20"})
           .drop_duplicates("date")
           .set_index("date")
           .sort_index()
           .loc[START:END])
    out.to_csv(OUT_DIR / "WIG20.csv")
    print(f"  WIG20: saved {len(out):,} rows  {out.index.min().date()} -> "
          f"{out.index.max().date()}")
    return True


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ok_px = download_px()
    ok_wig = download_wig20()
    return 0 if (ok_px and ok_wig) else 1


if __name__ == "__main__":
    sys.exit(main())
