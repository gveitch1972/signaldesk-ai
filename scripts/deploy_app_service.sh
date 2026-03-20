#!/usr/bin/env bash
set -euo pipefail

if ! command -v az >/dev/null 2>&1; then
  echo "Azure CLI (az) is required. Install: https://learn.microsoft.com/cli/azure/install-azure-cli" >&2
  exit 1
fi

required_vars=(
  RESOURCE_GROUP
  LOCATION
  APP_SERVICE_PLAN
  WEBAPP_NAME
  DB_HOST
  DB_HTTP_PATH
  DB_TOKEN
  FOUNDRY_ENDPOINT
  FOUNDRY_API_KEY
)

for var in "${required_vars[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    echo "Missing required env var: ${var}" >&2
    exit 1
  fi
done

FOUNDRY_MODEL_DEPLOYMENT="${FOUNDRY_MODEL_DEPLOYMENT:-gpt-4.1-mini}"
FOUNDRY_API_VERSION="${FOUNDRY_API_VERSION:-2025-01-01-preview}"
PYTHON_RUNTIME="${PYTHON_RUNTIME:-PYTHON|3.11}"
APP_SERVICE_SKU="${APP_SERVICE_SKU:-B1}"
PACKAGE_PATH="${PACKAGE_PATH:-/tmp/signaldesk-ai.zip}"

az group create --name "$RESOURCE_GROUP" --location "$LOCATION" >/dev/null

if ! az appservice plan show --resource-group "$RESOURCE_GROUP" --name "$APP_SERVICE_PLAN" >/dev/null 2>&1; then
  az appservice plan create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_SERVICE_PLAN" \
    --is-linux \
    --sku "$APP_SERVICE_SKU" >/dev/null
fi

if ! az webapp show --resource-group "$RESOURCE_GROUP" --name "$WEBAPP_NAME" >/dev/null 2>&1; then
  az webapp create \
    --resource-group "$RESOURCE_GROUP" \
    --plan "$APP_SERVICE_PLAN" \
    --name "$WEBAPP_NAME" \
    --runtime "$PYTHON_RUNTIME" >/dev/null
fi

az webapp config set \
  --resource-group "$RESOURCE_GROUP" \
  --name "$WEBAPP_NAME" \
  --startup-file "bash startup.sh" >/dev/null

az webapp config appsettings set \
  --resource-group "$RESOURCE_GROUP" \
  --name "$WEBAPP_NAME" \
  --settings \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    DB_HOST="$DB_HOST" \
    DB_HTTP_PATH="$DB_HTTP_PATH" \
    DB_TOKEN="$DB_TOKEN" \
    FOUNDRY_ENDPOINT="$FOUNDRY_ENDPOINT" \
    FOUNDRY_API_KEY="$FOUNDRY_API_KEY" \
    FOUNDRY_MODEL_DEPLOYMENT="$FOUNDRY_MODEL_DEPLOYMENT" \
    FOUNDRY_API_VERSION="$FOUNDRY_API_VERSION" >/dev/null

zip -r "$PACKAGE_PATH" . \
  -x ".git/*" \
  -x ".venv/*" \
  -x "__pycache__/*" \
  -x "*.pyc" \
  -x "*.pyo" \
  -x "*.DS_Store" >/dev/null

az webapp deploy \
  --resource-group "$RESOURCE_GROUP" \
  --name "$WEBAPP_NAME" \
  --src-path "$PACKAGE_PATH" \
  --type zip >/dev/null

APP_URL="https://${WEBAPP_NAME}.azurewebsites.net"
echo "Deployment complete: ${APP_URL}"
echo "Tail logs: az webapp log tail --resource-group ${RESOURCE_GROUP} --name ${WEBAPP_NAME}"
