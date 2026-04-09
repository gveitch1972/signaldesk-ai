import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "")
DB_HTTP_PATH = os.getenv("DB_HTTP_PATH", "")
DB_TOKEN = os.getenv("DB_TOKEN", "")

# Preferred Databricks Jobs API settings for non-serverless execution.
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST", DB_HOST)
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", DB_TOKEN)
DATABRICKS_JOB_ID = os.getenv("DATABRICKS_JOB_ID", "239064539654873")
DATABRICKS_RUN_TIMEOUT_SECONDS = int(os.getenv("DATABRICKS_RUN_TIMEOUT_SECONDS", "900"))
DATABRICKS_POLL_INTERVAL_SECONDS = int(
    os.getenv("DATABRICKS_POLL_INTERVAL_SECONDS", "5")
)
DATABRICKS_CA_BUNDLE = os.getenv("DATABRICKS_CA_BUNDLE", "")

FOUNDRY_ENDPOINT = os.getenv("FOUNDRY_ENDPOINT", "")
FOUNDRY_API_KEY = os.getenv("FOUNDRY_API_KEY", "")
FOUNDRY_MODEL_DEPLOYMENT = os.getenv("FOUNDRY_MODEL_DEPLOYMENT", "gpt-4.1-mini")
FOUNDRY_API_VERSION = os.getenv("FOUNDRY_API_VERSION", "2025-01-01-preview")


def _as_bool(value: str, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


CONTEXT_CACHE_TTL_SECONDS = int(os.getenv("CONTEXT_CACHE_TTL_SECONDS", "900"))
HEAVY_CONTEXT_CACHE_TTL_SECONDS = int(
    os.getenv("HEAVY_CONTEXT_CACHE_TTL_SECONDS", "21600")
)
ENABLE_HEAVY_CONTEXT_FOR_QA = _as_bool(os.getenv("ENABLE_HEAVY_CONTEXT_FOR_QA"), False)
ENABLE_HEAVY_CONTEXT_FOR_BRIEFING = _as_bool(
    os.getenv("ENABLE_HEAVY_CONTEXT_FOR_BRIEFING"), True
)
ENABLE_UI_DEBUG = _as_bool(os.getenv("ENABLE_UI_DEBUG"), True)
ENABLE_SERVERLESS_COMPUTE = _as_bool(os.getenv("ENABLE_SERVERLESS_COMPUTE"), False)
DATABRICKS_SKIP_SSL_VERIFY = _as_bool(os.getenv("DATABRICKS_SKIP_SSL_VERIFY"), False)
