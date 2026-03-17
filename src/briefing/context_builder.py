from src.queries.regime import load_latest_regime
from src.queries.market import load_market_breadth, load_market_coverage, load_market_stress
from src.queries.fx import load_fx_coverage, load_fx_history_summary, load_fx_watchlist
from src.queries.macro import load_macro_coverage, load_macro_trends


def build_context() -> str:
    regime = load_latest_regime()
    regime_flag = regime[0]["risk_regime"] if regime else "unknown"
    market_coverage = load_market_coverage()
    market_breadth = load_market_breadth()
    market = load_market_stress()
    fx_coverage = load_fx_coverage()
    fx_history = load_fx_history_summary()
    fx = load_fx_watchlist()
    macro_coverage = load_macro_coverage()
    macro = load_macro_trends()

    return f"""
REGIME (Computed): 
{regime_flag}

CROSS SIGNAL REGIME:
{regime}

MARKET COVERAGE:
{market_coverage}

MARKET BREADTH:
{market_breadth}

MARKET STRESS (Top 10):
{market}

FX COVERAGE:
{fx_coverage}

FX HISTORY SUMMARY:
{fx_history}

FX WATCHLIST:
{fx}

MACRO COVERAGE:
{macro_coverage}

MACRO TRENDS:
{macro}
""".strip()
