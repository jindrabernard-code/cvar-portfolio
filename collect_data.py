"""
collect_data.py  —  CVaR-Constrained Portfolio Optimization (CEE Equities)
====================================================================================
Downloads all data needed for the Markowitz vs CVaR portfolio-optimization project
on Czech / Central-Eastern-European equities.

Data collected
--------------
1. Equity prices          → data/equities/{TICKER}.csv   (daily adj. close, 2015-2024)
2. Index levels           → data/indices/{INDEX}.csv     (daily close, 2015-2024)
3. FX rates               → data/fx/{pair}.csv           (daily, ECB SDW API)
4. Czech risk-free rate   → data/rates/pribor_3m.csv     (daily, ČNB)
5. EUR risk-free rate     → data/rates/ester.csv         (daily, ECB SDW API)

Usage
-----
    python collect_data.py

Dependencies: pip install yfinance requests pandas python-dotenv
"""

import sys, os, time, logging, requests
from pathlib import Path
from datetime import datetime

import pandas as pd

# ─── Logging ──────────────────────────────────────────────────────────────────
_stream = logging.StreamHandler(sys.stdout)
_stream.stream = open(sys.stdout.fileno(), mode="w", encoding="utf-8", closefd=False, buffering=1)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[_stream, logging.FileHandler("collect_data.log", encoding="utf-8")],
)
log = logging.getLogger(__name__)

# ─── Config ───────────────────────────────────────────────────────────────────
START = "2015-01-01"
END   = "2024-12-31"

DATA_DIR = Path(__file__).parent / "data"

# ─── CEE Equity Universe ──────────────────────────────────────────────────────
# Prague Stock Exchange (PSE / Burza cenných papírů Praha)
CZ_EQUITIES = {
    "CEZ.PR":   "ČEZ a.s. — Czech electricity incumbent",
    "KOMB.PR":  "Komerční banka — Czech retail bank (Société Générale group)",
    "O2CR.PR":  "O2 Czech Republic — Czech telecom",
    "MONET.PR": "Moneta Money Bank — Czech retail bank (IPO May 2016)",
    "TABAK.PR": "Philip Morris ČR — Czech tobacco (PMI subsidiary)",
    "VIG.PR":   "Vienna Insurance Group — Austrian insurer, Prague-listed",
    "COLT.PR":  "Colt CZ Group — Czech firearms manufacturer",
}

# Warsaw Stock Exchange (GPW) — WIG20 constituents
PL_EQUITIES = {
    "PKN.WA":  "PKN Orlen — Polish oil refiner/petrol stations",
    "PKO.WA":  "PKO Bank Polski — largest Polish bank",
    "PZU.WA":  "PZU S.A. — Polish insurance group",
    "KGH.WA":  "KGHM Polska Miedź — copper & silver mining",
    "LPP.WA":  "LPP S.A. — Polish fashion retail (Reserved, Mohito, Cropp)",
    "CDR.WA":  "CD Projekt — Polish game developer (Witcher, Cyberpunk 2077)",
    "PEO.WA":  "Bank Pekao — Polish universal bank",
    "ALE.WA":  "Allegro.eu — Polish e-commerce (IPO Oct 2020)",
}

# Budapest Stock Exchange (BÉT / BSE) — BUX
HU_EQUITIES = {
    "OTP.BD":     "OTP Bank — largest Hungarian bank, major CEE presence",
    "MOL.BD":     "MOL Group — Hungarian oil & gas (refining + E&P)",
    "RICHTER.BD": "Gedeon Richter Plc — Hungarian pharma",
}

# Vienna Stock Exchange (Wiener Börse) — ATX
AT_EQUITIES = {
    "EBS.VI":  "Erste Group Bank — Austrian bank dominant in CEE retail",
    "OMV.VI":  "OMV AG — Austrian integrated oil & gas",
    "VER.VI":  "Verbund AG — Austrian hydropower/electricity",
    "RBI.VI":  "Raiffeisen Bank International — Austrian bank, strong CZ/PL/HU",
}

ALL_EQUITIES = {**CZ_EQUITIES, **PL_EQUITIES, **HU_EQUITIES, **AT_EQUITIES}

# Benchmark indices
INDICES = {
    "^PX":       "Prague Stock Exchange PX index",
    "^WIG20":    "Warsaw WIG20 index",
    "^BUX":      "Budapest BUX index",
    "^ATX":      "Vienna ATX index",
    "^STOXX50E": "Euro Stoxx 50 (pan-European benchmark)",
    "^GDAXI":    "DAX 40 (German benchmark — CZ prices highly correlated)",
    "^GSPC":     "S&P 500 (global risk-off benchmark)",
}

# ECB SDW FX series (D = daily, SP00 = spot, A = average)
ECB_BASE = "https://data-api.ecb.europa.eu/service/data"
FX_SERIES = {
    "CZK_EUR": "EXR/D.CZK.EUR.SP00.A",
    "PLN_EUR": "EXR/D.PLN.EUR.SP00.A",
    "HUF_EUR": "EXR/D.HUF.EUR.SP00.A",
    "USD_EUR": "EXR/D.USD.EUR.SP00.A",
}

# ─── Helpers ──────────────────────────────────────────────────────────────────
def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def save_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path)
    log.info(f"    Saved {len(df):,} rows  {path.relative_to(DATA_DIR.parent)}")

# ─── 1. Equity prices via yfinance ────────────────────────────────────────────
def collect_equities(out_dir: Path) -> None:
    log.info("━━━ Equity Prices (yfinance) ━━━")
    ensure_dir(out_dir)
    try:
        import yfinance as yf
    except ImportError:
        log.error("yfinance not installed. Run: pip install yfinance")
        return

    ok, skip, fail = 0, 0, 0
    for ticker, desc in ALL_EQUITIES.items():
        out_file = out_dir / f"{ticker.replace('^','')}.csv"
        if out_file.exists():
            log.info(f"  {ticker}: already exists — skipping.")
            skip += 1
            continue
        try:
            df = yf.download(ticker, start=START, end=END,
                             auto_adjust=True, progress=False, timeout=30)
            if df.empty:
                log.warning(f"  {ticker}: no data returned.")
                fail += 1
                continue
            # Keep Close only (adjusted), rename to ticker
            close = df[["Close"]].copy()
            close.columns = ["adj_close"]
            close.index.name = "date"
            close = close.dropna()
            save_csv(close, out_file)
            ok += 1
        except Exception as exc:
            log.warning(f"  {ticker}: {exc}")
            fail += 1
        time.sleep(0.5)

    log.info(f"  Equities: {ok} downloaded, {skip} skipped, {fail} failed.")


# ─── 2. Index levels via yfinance ─────────────────────────────────────────────
def collect_indices(out_dir: Path) -> None:
    log.info("━━━ Index Levels (yfinance) ━━━")
    ensure_dir(out_dir)
    try:
        import yfinance as yf
    except ImportError:
        return

    ok, skip, fail = 0, 0, 0
    for ticker, desc in INDICES.items():
        name = ticker.replace("^", "").replace("=", "")
        out_file = out_dir / f"{name}.csv"
        if out_file.exists():
            log.info(f"  {ticker}: already exists — skipping.")
            skip += 1
            continue
        try:
            df = yf.download(ticker, start=START, end=END,
                             auto_adjust=True, progress=False, timeout=30)
            if df.empty:
                log.warning(f"  {ticker}: no data returned.")
                fail += 1
                continue
            close = df[["Close"]].copy()
            close.columns = ["close"]
            close.index.name = "date"
            close = close.dropna()
            save_csv(close, out_file)
            ok += 1
        except Exception as exc:
            log.warning(f"  {ticker}: {exc}")
            fail += 1
        time.sleep(0.5)

    log.info(f"  Indices: {ok} downloaded, {skip} skipped, {fail} failed.")


# ─── 3. FX rates via ECB Statistical Data Warehouse ──────────────────────────
def collect_fx(out_dir: Path) -> None:
    log.info("━━━ FX Rates (ECB SDW) ━━━")
    ensure_dir(out_dir)

    for pair, series in FX_SERIES.items():
        out_file = out_dir / f"{pair}.csv"
        if out_file.exists():
            log.info(f"  {pair}: already exists — skipping.")
            continue
        try:
            url = (f"{ECB_BASE}/{series}"
                   f"?startPeriod={START}&endPeriod={END}&format=csvdata")
            r = requests.get(url, timeout=30,
                             headers={"Accept": "text/csv"})
            if r.status_code != 200:
                log.warning(f"  {pair}: HTTP {r.status_code}")
                continue
            from io import StringIO
            df = pd.read_csv(StringIO(r.text))
            # ECB CSV has TIME_PERIOD and OBS_VALUE columns
            if "TIME_PERIOD" not in df.columns or "OBS_VALUE" not in df.columns:
                log.warning(f"  {pair}: unexpected columns {list(df.columns)[:5]}")
                continue
            df = df[["TIME_PERIOD", "OBS_VALUE"]].rename(
                columns={"TIME_PERIOD": "date", "OBS_VALUE": pair}
            )
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date").sort_index().dropna()
            df = df.loc[START:END]
            save_csv(df, out_file)
        except Exception as exc:
            log.warning(f"  {pair}: {exc}")
        time.sleep(0.3)

    log.info("  FX collection complete.")


# ─── 4. Risk-free rates ────────────────────────────────────────────────────────
def collect_rates(out_dir: Path) -> None:
    log.info("━━━ Risk-free Rates ━━━")
    ensure_dir(out_dir)

    # 4a. PRIBOR 3M — Czech National Bank
    # CNB publishes yearly TXT files with exchange rates + money-market rates.
    # PRIBOR is available via the ARAD system.
    pribor_file = out_dir / "pribor_3m.csv"
    if not pribor_file.exists():
        log.info("  Downloading Czech short-term interest rate (PRIBOR proxy) from FRED...")
        try:
            # FRED series IRSTCI01CZM156N = Czech Republic Immediate Rates: Call Money/Interbank
            # Rate, Less than 24 Hours (monthly %). Used as PRIBOR proxy.
            url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=IRSTCI01CZM156N"
            from io import StringIO
            r = requests.get(url, timeout=30)
            if r.status_code == 200 and len(r.text) > 100:
                df = pd.read_csv(StringIO(r.text), names=["date", "pribor_3m_pct"],
                                 skiprows=1, parse_dates=["date"])
                df = df.set_index("date").sort_index()
                df["pribor_3m_pct"] = pd.to_numeric(df["pribor_3m_pct"], errors="coerce")
                df = df.dropna().loc[START:END]
                save_csv(df, pribor_file)
                log.info(f"  PRIBOR proxy (FRED): {len(df):,} months  "
                         f"{df.index.min().date()} → {df.index.max().date()}")
                log.info("  Note: monthly FRED series — forward-fill to daily in analysis code.")
            else:
                log.warning(f"  PRIBOR FRED: HTTP {r.status_code}")
        except Exception as exc:
            log.warning(f"  PRIBOR: {exc}")
    else:
        log.info("  PRIBOR 3M: already exists — skipping.")

    # 4b. €STR (Euro Short-Term Rate) — replaces EONIA, ECB SDW
    ester_file = out_dir / "ester.csv"
    if not ester_file.exists():
        log.info("  Downloading €STR from ECB SDW...")
        try:
            # €STR series: EST.B.EU000A2X2A25.WT (compounded rate)
            url = (f"{ECB_BASE}/EST/B.EU000A2X2A25.WT"
                   f"?startPeriod={START}&endPeriod={END}&format=csvdata")
            r = requests.get(url, timeout=30, headers={"Accept": "text/csv"})
            if r.status_code == 200:
                from io import StringIO
                df = pd.read_csv(StringIO(r.text))
                if "TIME_PERIOD" in df.columns and "OBS_VALUE" in df.columns:
                    df = df[["TIME_PERIOD", "OBS_VALUE"]].rename(
                        columns={"TIME_PERIOD": "date", "OBS_VALUE": "ester_pct"}
                    )
                    df["date"] = pd.to_datetime(df["date"])
                    df = df.set_index("date").sort_index().dropna()
                    save_csv(df, ester_file)
                    log.info(f"  €STR: {len(df):,} rows")
                else:
                    log.warning("  €STR: unexpected response format")
            else:
                log.warning(f"  €STR: HTTP {r.status_code}")
        except Exception as exc:
            log.warning(f"  €STR: {exc}")
    else:
        log.info("  €STR: already exists — skipping.")

    # 4c. Czech 3Y Government bond yield (proxy for medium-term risk-free rate)
    # Source: ECB SDW — Czech government bond yield
    czgov_file = out_dir / "cz_gov_bond_3y.csv"
    if not czgov_file.exists():
        log.info("  Downloading CZ 3Y Gov Bond yield from ECB SDW...")
        try:
            # ECB IRS (interest rate statistics) for CZ: not always available.
            # Try FRED-style: use OECD/Eurostat 10Y as fallback.
            url = (f"{ECB_BASE}/IRS/M.CZ.L.L40.CI.0.CZK.N.Z"
                   f"?startPeriod=2015-01&endPeriod=2024-12&format=csvdata")
            r = requests.get(url, timeout=30, headers={"Accept": "text/csv"})
            if r.status_code == 200 and len(r.text) > 200:
                from io import StringIO
                df = pd.read_csv(StringIO(r.text))
                if "TIME_PERIOD" in df.columns and "OBS_VALUE" in df.columns:
                    df = df[["TIME_PERIOD", "OBS_VALUE"]].rename(
                        columns={"TIME_PERIOD": "date", "OBS_VALUE": "cz_gov_3y_pct"}
                    )
                    df["date"] = pd.to_datetime(df["date"])
                    df = df.set_index("date").sort_index().dropna()
                    save_csv(df, czgov_file)
                    log.info(f"  CZ 3Y Gov Bond: {len(df):,} rows")
            else:
                log.warning(f"  CZ 3Y Gov Bond: HTTP {r.status_code} or empty")
        except Exception as exc:
            log.warning(f"  CZ 3Y Gov Bond: {exc}")
    else:
        log.info("  CZ 3Y Gov Bond: already exists — skipping.")

    log.info("  Rates collection complete.")


# ─── MAIN ──────────────────────────────────────────────────────────────────────
def main() -> None:
    sep = "═" * 60
    log.info(sep)
    log.info("CVaR Portfolio — CEE Data Collection")
    log.info(f"Period  : {START}  →  {END}")
    log.info(f"Output  : {DATA_DIR.resolve()}")
    log.info(f"Stocks  : {len(ALL_EQUITIES)} equities  |  {len(INDICES)} indices")
    log.info(sep)

    collect_equities(DATA_DIR / "equities")
    collect_indices(DATA_DIR / "indices")
    collect_fx(DATA_DIR / "fx")
    collect_rates(DATA_DIR / "rates")

    log.info(sep)
    log.info("Collection complete.")
    log.info(sep)


if __name__ == "__main__":
    main()
