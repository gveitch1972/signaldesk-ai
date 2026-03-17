from dotenv import load_dotenv
load_dotenv()

from databricks import sql
import os

conn = sql.connect(
    server_hostname=os.getenv("DB_HOST"),
    http_path=os.getenv("DB_HTTP_PATH"),
    access_token=os.getenv("DB_TOKEN"),
)

cursor = conn.cursor()

query = """
SELECT
    symbol,
    snapshot_date,
    latest_price,
    return_30d_pct,
    rolling_30d_volatility,
    drawdown_from_90d_high_pct,
    stress_flag
FROM fin_signals_dev.gold.daily_market_snapshot
ORDER BY snapshot_date DESC, stress_flag DESC
LIMIT 10
"""

cursor.execute(query)
rows = cursor.fetchall()

for row in rows:
    print(row)
