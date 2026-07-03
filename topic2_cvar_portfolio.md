# Thesis Topic 2: CVaR-Constrained Portfolio Optimization for Czech/CEE Equities

## 1. Topic Summary

The thesis compares classical **Markowitz mean-variance optimization** with **Conditional Value-at-Risk (CVaR) optimization** (Rockafellar–Uryasev formulation) on a Czech/Central-European equity universe, with emphasis on tail-risk behavior during stress episodes (COVID crash 2020, energy-crisis selloff 2022). The ambitious layer is (a) **copula-based scenario generation** capturing fat tails and crash-correlation, and (b) a **multi-period rebalancing backtest** with transaction costs on a relatively illiquid market.

**Central research questions:**
1. Does scenario-based CVaR optimization deliver materially better out-of-sample tail risk (max drawdown, realized CVaR) than mean-variance on CEE equities?
2. How much of the improvement comes from the objective (CVaR vs. variance) versus the scenario model (copula vs. Gaussian)?
3. Do the results survive transaction costs and realistic rebalancing frequency on the Prague Stock Exchange?

## 2. Why This Topic Is Worth Doing (Benefits)

- **Genuine gap:** "Markowitz vs. CVaR" is common, but rigorous studies on the *Czech/CEE* universe with *copula scenario generation* and *dynamic out-of-sample testing* are rare; most existing student work is static and Gaussian.
- **Decomposition insight:** separating the effect of the risk measure from the effect of the distributional model is a clean, publishable-quality contribution.
- **Practical value:** directly relevant to Czech asset managers, pension companies (penzijní společnosti), and family offices allocating to CEE equities; CVaR is also the regulatory language of Solvency II / Basel-style tail measures.
- **Career signal:** demonstrates portfolio construction, risk management, and computational finance skills valued by banks and asset managers (ČSOB/KBC, Česká spořitelna/Erste, Generali, Amundi CEE desks).

## 3. Suitability as a Master's Thesis

**Verdict: Highly suitable, lowest execution risk of the three topics.** The core CVaR LP is straightforward to implement; daily price data is trivially available; the sophistication comes from scenario modeling and honest out-of-sample evaluation rather than from heavy solver machinery.

- **Scope control:** static in-sample comparison = safe minimum; rolling out-of-sample backtest = solid thesis; copula scenarios + multi-period model = distinguished thesis.
- **Main risks:** (a) small liquid universe on PSE alone — mitigate by extending to WIG20 (Warsaw), BUX (Budapest), ATX (Vienna); (b) data-snooping/overfitting accusations — mitigate with strict train/test separation and reporting of all parameter choices.

## 4. Data Sources (feasibility confirmed)

| Data | Source | Access | Notes |
|---|---|---|---|
| PX index constituents, daily prices | Prague Stock Exchange (pse.cz), kurzy.cz | Free | ~10–15 liquid names; core CZ universe |
| CEE equities (WIG20, BUX, ATX) | Stooq.pl, Yahoo Finance | Free | Stooq is excellent for CEE daily data incl. dividends-adjusted series |
| Index data (PX, WIG20, BUX, ATX, EURO STOXX) | Stooq / exchange websites | Free | Benchmarks |
| FX rates (CZK/EUR/PLN/HUF) | ČNB (cnb.cz), ECB SDW | Free | Needed to express returns in one currency |
| Risk-free rate | ČNB ARAD (PRIBOR, T-bill/repo rates) | Free | For Sharpe/Sortino ratios |
| Macro conditioning variables (optional) | ČNB ARAD, Eurostat | Free | For regime/factor-conditioned scenarios |
| Pension fund performance (optional side section) | APS ČR, individual penzijní společnosti reports | Free but coarse | Quarterly/aggregate only — keep as illustration, not core |

**Practical notes:** adjust for dividends and corporate actions (use adjusted close); handle the small number of PSE names honestly — a 25–40 stock CEE universe is the right size for meaningful optimization. Daily frequency is fully sufficient; no paid data needed.

## 5. Potential Thesis Structure

1. **Introduction** — motivation (tail risk in small/illiquid CEE markets), research questions, contribution.
2. **Theoretical background**
   - 2.1 Mean-variance framework and its known weaknesses (estimation error, symmetric risk measure)
   - 2.2 VaR vs. CVaR; coherence of risk measures (Artzner et al.)
   - 2.3 Rockafellar–Uryasev LP formulation of CVaR minimization
3. **Scenario generation**
   - 3.1 Gaussian baseline (historical mean/covariance)
   - 3.2 Historical/bootstrap scenarios
   - 3.3 Marginal models (e.g., ARMA-GARCH with skewed-t innovations) + **t-copula / vine copula** dependence
   - 3.4 Diagnostics: tail dependence coefficients, crash-correlation evidence in CEE data
4. **Data** — universe construction, descriptive statistics, stylized facts (fat tails, skewness, correlation asymmetry).
5. **Empirical design**
   - 5.1 Static comparison (in-sample efficient frontiers: mean-variance vs. mean-CVaR)
   - 5.2 Rolling out-of-sample backtest with re-optimization, transaction costs, turnover constraints
   - 5.3 (Optional) multi-period stochastic program with rebalancing recourse
6. **Results** — out-of-sample Sharpe, Sortino, max drawdown, realized 95/99% CVaR, turnover; subperiod analysis (2020, 2022); the objective-vs-scenario-model decomposition.
7. **Robustness** — different α levels, estimation windows, universes (CZ-only vs. CEE), equal-weight and minimum-variance benchmarks.
8. **Discussion and conclusion** — practical implications for CEE asset allocation, limitations.

## 6. Relevant Literature (starting set)

**Foundations**
- Markowitz, H. (1952), "Portfolio Selection", *Journal of Finance*.
- Rockafellar, R.T. & Uryasev, S. (2000), "Optimization of Conditional Value-at-Risk", *Journal of Risk*; and (2002) "Conditional value-at-risk for general loss distributions", *Journal of Banking & Finance*.
- Artzner, P., Delbaen, F., Eber, J.-M. & Heath, D. (1999), "Coherent Measures of Risk", *Mathematical Finance*.

**Scenario modeling / copulas**
- McNeil, A., Frey, R. & Embrechts, P. — *Quantitative Risk Management* (Princeton UP) — the key reference for copulas, tail dependence, and GARCH marginals.
- Patton, A. (2012), "A review of copula models for economic time series", *Journal of Multivariate Analysis*.
- Kaut, M. & Wallace, S.W. (2007), "Evaluation of scenario-generation methods for stochastic programming", *Pacific Journal of Optimization*.

**Portfolio optimization under uncertainty / estimation error**
- DeMiguel, V., Garlappi, L. & Uppal, R. (2009), "Optimal versus Naive Diversification: How Inefficient is the 1/N Portfolio Strategy?", *Review of Financial Studies* — the benchmark skeptic paper you must engage with.
- Krokhmal, P., Palmquist, J. & Uryasev, S. (2002), "Portfolio optimization with conditional value-at-risk objective and constraints", *Journal of Risk*.
- Kolm, P., Tütüncü, R. & Fabozzi, F. (2014), "60 Years of portfolio optimization", *European Journal of Operational Research*.

**CEE-specific**
- Search terms: "CEE equity markets tail dependence", "Visegrad stock markets copula", "Prague Stock Exchange portfolio optimization" — there is a small but citable literature (e.g., work in *Czech Journal of Economics and Finance / Finance a úvěr* and *Prague Economic Papers*), and citing local journals plays well with Czech committees.

## 7. What You Should Study Beforehand

**Mathematics / optimization:**
- Linear programming; convex optimization basics.
- Risk measures: VaR, CVaR, coherence axioms; the Rockafellar–Uryasev linearization mechanics.
- (Optional extension) multi-stage stochastic programming with transaction-cost recourse.

**Econometrics / statistics:**
- Univariate volatility models (GARCH family, skewed-t innovations).
- Copula theory: Sklar's theorem, Gaussian vs. t-copula, tail dependence; vine copulas if ambitious.
- Backtesting methodology: rolling windows, out-of-sample discipline, multiple-testing awareness.

**Finance:**
- Modern portfolio theory and its critiques (estimation error, DeMiguel et al.).
- Market microstructure basics for the transaction-cost model (bid-ask spreads on PSE, turnover costs).

**Software:**
- Python: pandas, `arch` (GARCH), `copulas`/`pyvinecopulib`, cvxpy or Pyomo for the LP; or R: `rugarch`, `VineCopula`, `PortfolioAnalytics`.
- Free solvers (HiGHS, ECOS) are fully sufficient — CVaR LPs with a few thousand scenarios solve in seconds.
