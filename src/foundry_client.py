from openai import AzureOpenAI
from src.config import (
    FOUNDRY_ENDPOINT,
    FOUNDRY_API_KEY,
    FOUNDRY_API_VERSION,
)


def get_client():
    return AzureOpenAI(
        azure_endpoint=FOUNDRY_ENDPOINT,
        api_key=FOUNDRY_API_KEY,
        api_version=FOUNDRY_API_VERSION,
    )
