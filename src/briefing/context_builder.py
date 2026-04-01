import threading
import time
import logging

from src.config import CONTEXT_CACHE_TTL_SECONDS, HEAVY_CONTEXT_CACHE_TTL_SECONDS
from src.databricks_jobs_client import run_context_job


_CACHE_LOCK = threading.Lock()
_CONTEXT_CACHE: dict[str, dict] = {}
_PAYLOAD_CACHE: dict[bool, dict] = {}
_EMPTY_SIGNATURE = ("", "", "", "")
logger = logging.getLogger(__name__)


def get_latest_dates(raise_on_error: bool = False) -> dict[str, str]:
    try:
        payload = _get_context_payload(include_heavy=False, force_refresh=False)
    except Exception:
        logger.exception("Failed to fetch latest data dates from Databricks context payload.")
        if raise_on_error:
            raise
        return {
            "regime_as_of_date": "",
            "market_snapshot_date": "",
            "fx_rate_date": "",
            "movers_as_of_date": "",
        }

    latest_dates = payload.get("latest_dates")
    if not isinstance(latest_dates, dict):
        return {
            "regime_as_of_date": "",
            "market_snapshot_date": "",
            "fx_rate_date": "",
            "movers_as_of_date": "",
        }
    return {
        "regime_as_of_date": str(latest_dates.get("regime_as_of_date") or ""),
        "market_snapshot_date": str(latest_dates.get("market_snapshot_date") or ""),
        "fx_rate_date": str(latest_dates.get("fx_rate_date") or ""),
        "movers_as_of_date": str(latest_dates.get("movers_as_of_date") or ""),
    }


def _get_section(payload: dict, key: str, fallback):
    value = payload.get(key)
    return value if value else fallback


def _get_heavy_section(payload: dict, key: str, fallback):
    heavy = payload.get("heavy")
    if isinstance(heavy, dict) and heavy.get(key):
        return heavy.get(key)
    return fallback


def _signature_from_payload(payload: dict) -> tuple[str, str, str, str]:
    latest_dates = payload.get("latest_dates")
    if not isinstance(latest_dates, dict):
        return _EMPTY_SIGNATURE
    return (
        str(latest_dates.get("regime_as_of_date") or ""),
        str(latest_dates.get("market_snapshot_date") or ""),
        str(latest_dates.get("fx_rate_date") or ""),
        str(latest_dates.get("movers_as_of_date") or ""),
    )


def _get_context_payload(include_heavy: bool, force_refresh: bool) -> dict:
    with _CACHE_LOCK:
        if not force_refresh and include_heavy in _PAYLOAD_CACHE:
            return _PAYLOAD_CACHE[include_heavy]

    payload = run_context_job(include_heavy=include_heavy)
    if not isinstance(payload, dict):
        raise RuntimeError("Databricks context job returned non-object payload.")

    with _CACHE_LOCK:
        _PAYLOAD_CACHE[include_heavy] = payload

    return payload


def get_context_payload(
    include_heavy: bool = False,
    force_refresh: bool = False,
    raise_on_error: bool = False,
) -> dict:
    try:
        payload = _get_context_payload(include_heavy=include_heavy, force_refresh=force_refresh)
        return payload if isinstance(payload, dict) else {}
    except Exception:
        logger.exception(
            "Failed to fetch context payload from Databricks context job (include_heavy=%s).",
            include_heavy,
        )
        if raise_on_error:
            raise
        return {}


def _build_context_text(include_heavy: bool) -> str:
    payload = _get_context_payload(include_heavy=include_heavy, force_refresh=False)

    regime = _get_section(payload, "regime", [{"note": "Regime data unavailable."}])
    regime_flag = regime[0].get("risk_regime", "unknown") if regime else "unknown"

    market_breadth = _get_section(payload, "market_breadth", [{"note": "Market breadth unavailable."}])
    market_stress = _get_section(payload, "market_stress", [{"note": "Market stress unavailable."}])
    fx_watchlist = _get_section(payload, "fx_watchlist", [{"note": "FX watchlist unavailable."}])
    macro_trends = _get_section(payload, "macro_trends", [{"note": "Macro trends unavailable."}])
    top_movers = _get_section(
        payload, "top_movers", [{"note": "Top movers explainability unavailable."}]
    )

    heavy_sections = ""
    if include_heavy:
        market_coverage = _get_heavy_section(
            payload, "market_coverage", [{"note": "Market coverage unavailable."}]
        )
        fx_coverage = _get_heavy_section(payload, "fx_coverage", [{"note": "FX coverage unavailable."}])
        fx_history = _get_heavy_section(
            payload, "fx_history_summary", [{"note": "FX history summary unavailable."}]
        )
        macro_coverage = _get_heavy_section(
            payload, "macro_coverage", [{"note": "Macro coverage unavailable."}]
        )

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

    latest_dates = _get_section(payload, "latest_dates", {})

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
        _PAYLOAD_CACHE.clear()


def build_context(include_heavy: bool = True, force_refresh: bool = False) -> str:
    cache_key = "heavy" if include_heavy else "fast"
    ttl_seconds = (
        HEAVY_CONTEXT_CACHE_TTL_SECONDS if include_heavy else CONTEXT_CACHE_TTL_SECONDS
    )
    payload = _get_context_payload(include_heavy=include_heavy, force_refresh=force_refresh)
    latest_signature = _signature_from_payload(payload)
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
