from src.databricks_client import run_query


def load_macro_trends():
    query = """
    SELECT
        country_code,
        indicator_name,
        observation_date,
        observation_value,
        period_change_pct,
        year_over_year_pct,
        trend_direction
    FROM fin_signals_dev.gold.macro_indicator_trends
    WHERE observation_date = (
        SELECT MAX(observation_date)
        FROM fin_signals_dev.gold.macro_indicator_trends
    )
    ORDER BY
        observation_date DESC,
        country_code,
        indicator_name
    LIMIT 15
    """
    return run_query(query)


def load_macro_coverage():
    query = """
    SELECT
        MIN(observation_date) AS first_observation_date,
        MAX(observation_date) AS latest_observation_date,
        COUNT(*) AS total_rows,
        COUNT(DISTINCT country_code) AS distinct_countries,
        COUNT(DISTINCT indicator_name) AS distinct_indicators,
        COUNT(DISTINCT observation_date) AS distinct_observation_dates
    FROM fin_signals_dev.gold.macro_indicator_trends
    """
    return run_query(query)
