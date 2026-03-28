import threading
import time

from src.config import CONTEXT_CACHE_TTL_SECONDS, HEAVY_CONTEXT_CACHE_TTL_SECONDS
from src.databricks_client import run_query
from src.queries.regime import load_latest_regime
from src.queries.market import load_market_breadth, load_market_coverage, load_market_stress
from src.queries.fx import load_fx_coverage, load_fx_history_summary, load_fx_watchlist
from src.queries.macro import load_macro_coverage, load_macro_trends
from src.queries.top_movers import load_top_movers_why


_CACHE_LOCK = threading.Lock()
_CONTEXT_CACHE: dict[str, dict] = {}


def _load_latest_dates_signature() -> tuple[str, str, str, str]:
    query = """
    SELECT
        (SELECT CAST(MAX(as_of_date) AS STRING) FROM fin_signals_dev.gold.cross_signal_summary) AS regime_as_of_date,
        (SELECT CAST(MAX(snapshot_date) AS STRING) FROM fin_signals_dev.gold.daily_market_snapshot) AS market_snapshot_date,
        (SELECT CAST(MAX(rate_date) AS STRING) FROM fin_signals_dev.gold.fx_trend_signals) AS fx_rate_date,
        (SELECT CAST(MAX(as_of_date) AS STRING) FROM fin_signals_dev.gold.top_movers_why) AS movers_as_of_date
    """
    try:
        rows = run_query(query)
    except Exception:
        return ("", "", "", "")

    if not rows:
        return ("", "", "", "")

    row = rows[0]
    return (
        row.get("regime_as_of_date") or "",
        row.get("market_snapshot_date") or "",
        row.get("fx_rate_date") or "",
        row.get("movers_as_of_date") or "",
    )


def get_latest_dates() -> dict[str, str]:
    regime_as_of_date, market_snapshot_date, fx_rate_date, movers_as_of_date = _load_latest_dates_signature()
    return {
        "regime_as_of_date": regime_as_of_date,
        "market_snapshot_date": market_snapshot_date,
        "fx_rate_date": fx_rate_date,
        "movers_as_of_date": movers_as_of_date,
    }


def _safe_load(loader, fallback):
    try:
        value = loader()
        if value:
            return value
    except Exception:
        pass
    return fallback


def _build_context_text(include_heavy: bool) -> str:
    regime = _safe_load(load_latest_regime, [{"note": "Regime data unavailable."}])
    regime_flag = regime[0].get("risk_regime", "unknown") if regime else "unknown"

    market_breadth = _safe_load(load_market_breadth, [{"note": "Market breadth unavailable."}])
    market_stress = _safe_load(load_market_stress, [{"note": "Market stress unavailable."}])
    fx_watchlist = _safe_load(load_fx_watchlist, [{"note": "FX watchlist unavailable."}])
    macro_trends = _safe_load(load_macro_trends, [{"note": "Macro trends unavailable."}])
    top_movers = _safe_load(load_top_movers_why, [{"note": "Top movers explainability unavailable."}])

    heavy_sections = ""
    if include_heavy:
        market_coverage = _safe_load(load_market_coverage, [{"note": "Market coverage unavailable."}])
        fx_coverage = _safe_load(load_fx_coverage, [{"note": "FX coverage unavailable."}])
        fx_history = _safe_load(load_fx_history_summary, [{"note": "FX history summary unavailable."}])
        macro_coverage = _safe_load(load_macro_coverage, [{"note": "Macro coverage unavailable."}])

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

    latest_dates = get_latest_dates()

    return f"""
LATEST DATA DATES:
{latest_dates}

REGIME CALL:
{regime_flag}

CROSS-SIGNAL REGIME DETAIL:
{regime}

TOP MOVERS + WHY:
{top_movers}

MARKET BREADTH:
{market_breadth}

MARKET STRESS (TOP):
{market_stress}

FX WATCHLIST:
{fx_watchlist}

MACRO TRENDS:
{macro_trends}
{heavy_sections}
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
