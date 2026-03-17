from src.databricks_client import run_query


def load_market_stress():
    query = """
    SELECT
        symbol,
        snapshot_date,
        latest_price,
        day_change_pct,
        return_30d_pct,
        return_90d_pct,
        rolling_30d_volatility,
        drawdown_from_90d_high_pct,
        stress_flag,
        currency
    FROM fin_signals_dev.gold.daily_market_snapshot
    WHERE snapshot_date = (
        SELECT MAX(snapshot_date)
        FROM fin_signals_dev.gold.daily_market_snapshot
    )
    ORDER BY
        stress_flag DESC,
        drawdown_from_90d_high_pct ASC,
        rolling_30d_volatility DESC
    LIMIT 10
    """
    return run_query(query)


def load_market_winners_losers():
    query = """
    SELECT
        symbol,
        return_30d_pct,
        return_90d_pct,
        rolling_30d_volatility
    FROM fin_signals_dev.gold.daily_market_snapshot
    WHERE snapshot_date = (
        SELECT MAX(snapshot_date)
        FROM fin_signals_dev.gold.daily_market_snapshot
    )
    ORDER BY return_30d_pct ASC
    LIMIT 5
    """
    losers = run_query(query)

    query_winners = """
    SELECT
        symbol,
        return_30d_pct,
        return_90d_pct,
        rolling_30d_volatility
    FROM fin_signals_dev.gold.daily_market_snapshot
    WHERE snapshot_date = (
        SELECT MAX(snapshot_date)
        FROM fin_signals_dev.gold.daily_market_snapshot
    )
    ORDER BY return_30d_pct DESC
    LIMIT 5
    """
    winners = run_query(query_winners)

    return {"losers": losers, "winners": winners}


def load_market_coverage():
    query = """
    SELECT
        MIN(snapshot_date) AS first_snapshot_date,
        MAX(snapshot_date) AS latest_snapshot_date,
        COUNT(*) AS total_rows,
        COUNT(DISTINCT symbol) AS distinct_symbols,
        COUNT(DISTINCT snapshot_date) AS distinct_snapshot_dates,
        COUNT(DISTINCT currency) AS distinct_currencies
    FROM fin_signals_dev.gold.daily_market_snapshot
    """
    return run_query(query)


def load_market_breadth():
    query = """
    WITH latest_snapshot AS (
        SELECT *
        FROM fin_signals_dev.gold.daily_market_snapshot
        WHERE snapshot_date = (
            SELECT MAX(snapshot_date)
            FROM fin_signals_dev.gold.daily_market_snapshot
        )
    )
    SELECT
        snapshot_date,
        COUNT(*) AS symbols_in_snapshot,
        SUM(CASE WHEN day_change_pct > 0 THEN 1 ELSE 0 END) AS advancing_symbols,
        SUM(CASE WHEN day_change_pct < 0 THEN 1 ELSE 0 END) AS declining_symbols,
        SUM(CASE WHEN stress_flag THEN 1 ELSE 0 END) AS stressed_symbols,
        ROUND(AVG(day_change_pct), 4) AS avg_day_change_pct,
        ROUND(AVG(return_30d_pct), 4) AS avg_return_30d_pct,
        ROUND(AVG(return_90d_pct), 4) AS avg_return_90d_pct,
        ROUND(AVG(rolling_30d_volatility), 4) AS avg_rolling_30d_volatility
    FROM latest_snapshot
    GROUP BY snapshot_date
    """
    return run_query(query)
