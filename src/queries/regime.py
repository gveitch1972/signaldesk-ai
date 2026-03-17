from src.databricks_client import run_query


def load_latest_regime():
    query = """
    SELECT
        as_of_date,
        risk_regime,
        market_stress_symbols,
        market_up_symbols,
        market_down_symbols,
        fx_stress_pairs,
        fx_strengthening_pairs,
        fx_weakening_pairs,
        macro_up_indicators,
        macro_down_indicators,
        market_avg_day_change_pct,
        market_avg_return_30d_pct,
        fx_avg_daily_change_pct,
        fx_avg_return_30d_pct,
        macro_avg_period_change_pct,
        macro_avg_year_over_year_pct
    FROM fin_signals_dev.gold.cross_signal_summary
    ORDER BY as_of_date DESC
    LIMIT 1
    """
    return run_query(query)
