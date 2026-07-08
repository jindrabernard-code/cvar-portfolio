"""
build_panel.py  —  CVaR Portfolio Optimization (CEE Equities)
=============================================================
Merges all collected data into a single wide-format daily panel CSV.

Output
------
  data/cvar_portfolio_panel.csv
  Index : date (YYYY-MM-DD, business days union)
  Columns:

  EQUITY ADJUSTED CLOSE PRICES (local currency per share)
    {TICKER}_local        e.g. CEZ.PR_local, PKN.WA_local, OTP.BD_local, …

  EQUITY LOG-RETURNS IN EUR (primary for CVaR analysis)
    {TICKER}_ret_eur      Daily log-return expressed in EUR (= local log-ret + FX log-ret)

  FX RATES (units of foreign currency per 1 EUR)
    fx_CZK_EUR, fx_PLN_EUR, fx_HUF_EUR, fx_USD_EUR

  BENCHMARK INDEX LEVELS (local/EUR)
    idx_ATX, idx_BUX, idx_STOXX50E, idx_GDAXI, idx_GSPC

  RISK-FREE RATES (% per annum, forward-filled to daily)
    rf_pribor_3m_pct      FRED Czech immediate rate proxy
    rf_ester_pct          ECB €STR (available from Oct 2019)
    rf_cz_10y_gov_pct     Czech 10Y government bond yield (FRED)

Usage
-----
  python build_panel.py
"""

import sys
import logging
import pandas as pd
import numpy as np
from pathlib import Path

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s  %(levelname)-8s  %(message)s",
                    handlers=[logging.StreamHandler(sys.stdout)])
log = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"
OUT_FILE = DATA_DIR / "cvar_portfolio_panel.csv"

START = "2015-01-01"
END   = "2024-12-31"

# Exchange→FX pair mapping (which FX rate to use per ticker suffix)
TICKER_FX = {
    ".PR": "CZK_EUR",
    ".WA": "PLN_EUR",
    ".BD": "HUF_EUR",
    ".VI": None,        # EUR-denominated already
}

# ─── helpers ──────────────────────────────────────────────────────────────────

def load_csv_date_index(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index, errors="coerce")
    return df.dropna(how="all").sort_index()


def read_single_col(path: Path, name: str) -> pd.Series:
    df = load_csv_date_index(path)
    if df.empty:
        return pd.Series(dtype=float, name=name)
    col = df.iloc[:, 0].rename(name)
    return col.loc[START:END]


# ─── 1. Load FX rates ─────────────────────────────────────────────────────────
def load_fx() -> pd.DataFrame:
    log.info("Loading FX rates (ECB SDW)...")
    fx_dir = DATA_DIR / "fx"
    frames = {}
    for pair in ["CZK_EUR", "PLN_EUR", "HUF_EUR", "USD_EUR"]:
        s = read_single_col(fx_dir / f"{pair}.csv", f"fx_{pair}")
        if not s.empty:
            frames[pair] = s
            log.info(f"  {pair}: {len(s):,} obs")
    if not frames:
        return pd.DataFrame()
    return pd.DataFrame(frames).loc[START:END]


# ─── 2. Load risk-free rates ──────────────────────────────────────────────────
def load_rates() -> pd.DataFrame:
    log.info("Loading risk-free rates...")
    rates_dir = DATA_DIR / "rates"
    pieces = {}

    for fname, col in [
        ("pribor_3m.csv", "rf_pribor_3m_pct"),
        ("ester.csv",     "rf_ester_pct"),
        ("cz_10y_gov_bond.csv", "rf_cz_10y_gov_pct"),
    ]:
        s = read_single_col(rates_dir / fname, col)
        if not s.empty:
            # Forward-fill to daily (monthly/sparse series)
            s = s.resample("D").interpolate(method="time")
            pieces[col] = s
            log.info(f"  {fname}: {len(s):,} obs after resample")

    if not pieces:
        return pd.DataFrame()
    return pd.DataFrame(pieces).loc[START:END]


# ─── 3. Load equity prices ────────────────────────────────────────────────────
def load_equities() -> pd.DataFrame:
    log.info("Loading equity adjusted close prices...")
    eq_dir = DATA_DIR / "equities"
    frames = {}
    for csv_file in sorted(eq_dir.glob("*.csv")):
        ticker = csv_file.stem          # e.g. "CEZ.PR"
        s = read_single_col(csv_file, f"{ticker}_local")
        if not s.empty:
            frames[ticker] = s
            log.info(f"  {ticker}: {len(s):,} trading days")
    if not frames:
        return pd.DataFrame()
    return pd.DataFrame(frames)


# ─── 4. Load index levels ─────────────────────────────────────────────────────
def load_indices() -> pd.DataFrame:
    log.info("Loading benchmark indices...")
    idx_dir = DATA_DIR / "indices"
    frames = {}
    for csv_file in sorted(idx_dir.glob("*.csv")):
        name = csv_file.stem
        s = read_single_col(csv_file, f"idx_{name}")
        if not s.empty:
            frames[name] = s
    return pd.DataFrame(frames).loc[START:END]


# ─── 5. Build panel ───────────────────────────────────────────────────────────
def build_panel() -> None:
    sep = "═" * 60
    log.info(sep)
    log.info("CVaR Portfolio — Building Daily Panel Dataset")
    log.info(sep)

    fx      = load_fx()
    rates   = load_rates()
    equities = load_equities()
    indices  = load_indices()

    # ── Compute EUR log-returns for each equity ──────────────────────────────
    log.info("Computing EUR log-returns...")
    ret_frames = {}

    for col in equities.columns:
        ticker = col.replace("_local", "")
        # Identify FX pair by suffix
        fx_pair = None
        for suffix, pair in TICKER_FX.items():
            if ticker.endswith(suffix):
                fx_pair = pair
                break

        price = equities[col].dropna()
        if len(price) < 5:
            continue

        local_ret = np.log(price / price.shift(1)).dropna()

        fx_col = f"fx_{fx_pair}" if fx_pair else None
        if fx_col and fx_col in fx.columns and not fx[fx_col].dropna().empty:
            fx_rate = fx[fx_col].reindex(local_ret.index, method="ffill").dropna()
            fx_ret  = np.log(fx_rate / fx_rate.shift(1)).dropna()
            # EUR log-return = local log-return − Δln(foreign/EUR)
            # Because: P_EUR = P_local / (FX_local/EUR) → ret_EUR = ret_local - ret_FX
            common_idx = local_ret.index.intersection(fx_ret.index)
            eur_ret = local_ret.reindex(common_idx) - fx_ret.reindex(common_idx)
        else:
            # Already EUR-denominated (e.g. .VI stocks)
            eur_ret = local_ret

        ret_frames[f"{ticker}_ret_eur"] = eur_ret.rename(f"{ticker}_ret_eur")

    if ret_frames:
        eur_returns = pd.DataFrame(ret_frames).loc[START:END]
        log.info(f"  EUR returns: {len(eur_returns):,} rows × {len(eur_returns.columns)} tickers")
    else:
        eur_returns = pd.DataFrame()

    # ── Rename local prices to include prefix ─────────────────────────────────
    equities_local = equities.rename(columns=lambda c: c)  # already named {TICKER}_local
    equities_local = equities_local.loc[START:END]

    # ── Merge all ─────────────────────────────────────────────────────────────
    pieces = [p for p in [equities_local, eur_returns, fx, indices, rates] if not p.empty]
    if not pieces:
        log.error("Nothing to merge.")
        return

    panel = pieces[0]
    for df in pieces[1:]:
        panel = panel.join(df, how="outer")

    panel = panel.sort_index().loc[START:END]
    panel = panel.dropna(how="all")

    log.info(sep)
    log.info(f"Panel: {len(panel):,} rows × {len(panel.columns)} columns")
    log.info(f"Date range: {panel.index.min().date()} → {panel.index.max().date()}")

    # Brief coverage summary
    coverage = panel.notna().mean().sort_values(ascending=False)
    log.info(f"Coverage (top 10):\n{coverage.head(10).to_string()}")
    log.info(f"Coverage (bottom 10):\n{coverage.tail(10).to_string()}")

    missing_pct = panel.isnull().mean()
    log.info(f"\nColumns with > 20% missing: {list(missing_pct[missing_pct > 0.2].index)}")

    panel.to_csv(OUT_FILE)
    log.info(f"Saved → {OUT_FILE}  ({OUT_FILE.stat().st_size / 1024:.0f} KB)")
    log.info(sep)


if __name__ == "__main__":
    build_panel()
