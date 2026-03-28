from src.databricks_client import run_query


def load_top_movers_why(limit: int = 10):
    query = f"""
    SELECT
        as_of_date,
        symbol,
        latest_price,
        day_change_pct,
        return_30d_pct,
        stress_flag,
        fx_context,
        macro_context,
        why_summary
    FROM fin_signals_dev.gold.top_movers_why
    WHERE as_of_date = (
        SELECT MAX(as_of_date)
        FROM fin_signals_dev.gold.top_movers_why
    )
    ORDER BY return_30d_pct ASC, symbol ASC
    LIMIT {int(limit)}
    """
    try:
        return run_query(query)
    except Exception:
        # Graceful fallback when the new table is not yet available.
        return []
