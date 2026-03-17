from databricks import sql
from src.config import DB_HOST, DB_HTTP_PATH, DB_TOKEN


def get_connection():
    return sql.connect(
        server_hostname=DB_HOST,
        http_path=DB_HTTP_PATH,
        access_token=DB_TOKEN,
    )


def run_query(query: str) -> list[dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    finally:
        conn.close()
