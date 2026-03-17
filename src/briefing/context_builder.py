from src.queries.regime import load_latest_regime
from src.queries.market import load_market_stress
from src.queries.fx import load_fx_watchlist
from src.queries.macro import load_macro_trends


def build_context() -> str:
    regime = load_latest_regime()
    regime_flag = regime[0]["risk_regime"] if regime else "unknown"
    market = load_market_stress()
    fx = load_fx_watchlist()
    macro = load_macro_trends()

    return f"""
REGIME (Computed): 
{regime_flag}

CROSS SIGNAL REGIME:
{regime}

MARKET STRESS (Top 10):
{market}

FX WATCHLIST:
{fx}

MACRO TRENDS:
{macro}
""".strip()
