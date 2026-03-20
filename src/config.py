import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "")
DB_HTTP_PATH = os.getenv("DB_HTTP_PATH", "")
DB_TOKEN = os.getenv("DB_TOKEN", "")

FOUNDRY_ENDPOINT = os.getenv("FOUNDRY_ENDPOINT", "")
FOUNDRY_API_KEY = os.getenv("FOUNDRY_API_KEY", "")
FOUNDRY_MODEL_DEPLOYMENT = os.getenv("FOUNDRY_MODEL_DEPLOYMENT", "gpt-4.1-mini")
FOUNDRY_API_VERSION = os.getenv("FOUNDRY_API_VERSION", "2025-01-01-preview")


def _as_bool(value: str, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


CONTEXT_CACHE_TTL_SECONDS = int(os.getenv("CONTEXT_CACHE_TTL_SECONDS", "900"))
HEAVY_CONTEXT_CACHE_TTL_SECONDS = int(os.getenv("HEAVY_CONTEXT_CACHE_TTL_SECONDS", "21600"))
ENABLE_HEAVY_CONTEXT_FOR_QA = _as_bool(os.getenv("ENABLE_HEAVY_CONTEXT_FOR_QA"), False)
ENABLE_HEAVY_CONTEXT_FOR_BRIEFING = _as_bool(
    os.getenv("ENABLE_HEAVY_CONTEXT_FOR_BRIEFING"), True
)
