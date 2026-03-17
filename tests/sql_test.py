from dotenv import load_dotenv

from databricks import sql
import os

load_dotenv()

conn = sql.connect(
    server_hostname=os.getenv("DB_HOST"),
    http_path=os.getenv("DB_HTTP_PATH"),
    access_token=os.getenv("DB_TOKEN"),
)

cursor = conn.cursor()
cursor.execute("SELECT 1")

print(cursor.fetchall())
