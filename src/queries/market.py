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
