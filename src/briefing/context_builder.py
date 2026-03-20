import threading
import time

from src.config import CONTEXT_CACHE_TTL_SECONDS, HEAVY_CONTEXT_CACHE_TTL_SECONDS
from src.databricks_client import run_query
from src.queries.regime import load_latest_regime
from src.queries.market import load_market_breadth, load_market_coverage, load_market_stress
from src.queries.fx import load_fx_coverage, load_fx_history_summary, load_fx_watchlist
from src.queries.macro import load_macro_coverage, load_macro_trends


_CACHE_LOCK = threading.Lock()
_CONTEXT_CACHE: dict[str, dict] = {}


def _load_latest_dates_signature() -> tuple[str, str, str]:
    query = """
    SELECT
        (SELECT CAST(MAX(as_of_date) AS STRING) FROM fin_signals_dev.gold.cross_signal_summary) AS regime_as_of_date,
        (SELECT CAST(MAX(snapshot_date) AS STRING) FROM fin_signals_dev.gold.daily_market_snapshot) AS market_snapshot_date,
        (SELECT CAST(MAX(rate_date) AS STRING) FROM fin_signals_dev.gold.fx_trend_signals) AS fx_rate_date
    """
    rows = run_query(query)
    if not rows:
        return ("", "", "")
    row = rows[0]
    return (
        row.get("regime_as_of_date") or "",
        row.get("market_snapshot_date") or "",
        row.get("fx_rate_date") or "",
    )


def _build_context_text(include_heavy: bool) -> str:
    regime = load_latest_regime()
    regime_flag = regime[0]["risk_regime"] if regime else "unknown"
    market_breadth = load_market_breadth()
    market = load_market_stress()
    fx = load_fx_watchlist()
    macro = load_macro_trends()

    heavy_sections = ""
    if include_heavy:
        market_coverage = load_market_coverage()
        fx_coverage = load_fx_coverage()
        fx_history = load_fx_history_summary()
        macro_coverage = load_macro_coverage()
        heavy_sections = f"""
MARKET COVERAGE:
{market_coverage}

FX COVERAGE:
{fx_coverage}

FX HISTORY SUMMARY:
{fx_history}

MACRO COVERAGE:
{macro_coverage}
"""

    return f"""
REGIME (Computed): 
{regime_flag}

CROSS SIGNAL REGIME:
{regime}
{heavy_sections}

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

MACRO TRENDS:
{macro}
""".strip()


def clear_context_cache() -> None:
    with _CACHE_LOCK:
        _CONTEXT_CACHE.clear()


def build_context(include_heavy: bool = True, force_refresh: bool = False) -> str:
    cache_key = "heavy" if include_heavy else "fast"
    ttl_seconds = (
        HEAVY_CONTEXT_CACHE_TTL_SECONDS if include_heavy else CONTEXT_CACHE_TTL_SECONDS
    )
    latest_signature = _load_latest_dates_signature()
    now = time.time()

    with _CACHE_LOCK:
        cached = _CONTEXT_CACHE.get(cache_key)
        if (
            cached
            and not force_refresh
            and cached["expires_at"] > now
            and cached["signature"] == latest_signature
        ):
            return cached["context"]

    context = _build_context_text(include_heavy=include_heavy)

    with _CACHE_LOCK:
        _CONTEXT_CACHE[cache_key] = {
            "context": context,
            "expires_at": now + ttl_seconds,
            "signature": latest_signature,
        }

    return context
