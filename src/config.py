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
