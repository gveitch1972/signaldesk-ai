from src.databricks_client import run_query


def load_fx_watchlist():
    query = """
    SELECT
        currency_pair,
        rate_date,
        rate,
        daily_change_pct,
        weekly_change_pct,
        return_30d_pct,
        rolling_30d_volatility,
        trend_signal,
        stress_flag
    FROM fin_signals_dev.gold.fx_trend_signals
    WHERE rate_date = (
        SELECT MAX(rate_date)
        FROM fin_signals_dev.gold.fx_trend_signals
    )
    ORDER BY
        stress_flag DESC,
        ABS(return_30d_pct) DESC,
        rolling_30d_volatility DESC
    LIMIT 10
    """
    return run_query(query)
