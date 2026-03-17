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


def load_fx_coverage():
    query = """
    SELECT
        MIN(rate_date) AS first_rate_date,
        MAX(rate_date) AS latest_rate_date,
        COUNT(*) AS total_rows,
        COUNT(DISTINCT currency_pair) AS distinct_currency_pairs,
        COUNT(DISTINCT rate_date) AS distinct_rate_dates
    FROM fin_signals_dev.gold.fx_trend_signals
    """
    return run_query(query)


def load_fx_history_summary():
    query = """
    WITH pair_history AS (
        SELECT
            currency_pair,
            MIN(rate_date) AS first_rate_date,
            MAX(rate_date) AS latest_rate_date,
            COUNT(*) AS observations,
            AVG(ABS(daily_change_pct)) AS avg_abs_daily_change_pct,
            AVG(rolling_30d_volatility) AS avg_rolling_30d_volatility,
            MAX(ABS(return_30d_pct)) AS max_abs_return_30d_pct
        FROM fin_signals_dev.gold.fx_trend_signals
        GROUP BY currency_pair
    )
    SELECT
        currency_pair,
        first_rate_date,
        latest_rate_date,
        observations,
        ROUND(avg_abs_daily_change_pct, 4) AS avg_abs_daily_change_pct,
        ROUND(avg_rolling_30d_volatility, 4) AS avg_rolling_30d_volatility,
        ROUND(max_abs_return_30d_pct, 4) AS max_abs_return_30d_pct
    FROM pair_history
    ORDER BY
        observations DESC,
        avg_rolling_30d_volatility DESC,
        currency_pair
    LIMIT 10
    """
    return run_query(query)
