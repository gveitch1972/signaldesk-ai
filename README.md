# SignalDesk AI

SignalDesk AI is a Python 3 app that builds market briefings and question-answering flows from Databricks data and Azure OpenAI.

## What It Does

The app now combines:

- cross-signal regime context
- market coverage, breadth, and latest stress signals
- FX coverage, per-pair history summaries, and the latest FX watchlist
- macro coverage and the latest macro trend rows
- top movers explainability from `fin_signals_dev.gold.top_movers_why`

The Streamlit UI supports:

- executive snapshot metrics and data freshness labels
- top movers plus rationale view
- asking free-form questions about the loaded data
- generating an executive briefing
- showing the raw assembled context sent to the model

## Setup

Use Python 3, not the system `python` command if that still points to Python 2.7 on your machine.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e .
```

## Environment

Create a `.env` file with the required Databricks Jobs API and Azure OpenAI settings:

```env
DATABRICKS_HOST=
DATABRICKS_TOKEN=
DATABRICKS_JOB_ID=
DATABRICKS_RUN_TIMEOUT_SECONDS=
DATABRICKS_POLL_INTERVAL_SECONDS=
FOUNDRY_ENDPOINT=
FOUNDRY_API_KEY=
FOUNDRY_MODEL_DEPLOYMENT=
FOUNDRY_API_VERSION=
CONTEXT_CACHE_TTL_SECONDS=
HEAVY_CONTEXT_CACHE_TTL_SECONDS=
ENABLE_HEAVY_CONTEXT_FOR_QA=
ENABLE_HEAVY_CONTEXT_FOR_BRIEFING=
```

Notes:

- `DATABRICKS_JOB_ID` must reference a Databricks job that uses `job_clusters[].new_cluster` and non-serverless task types (`notebook_task` or `python_wheel_task`).
- `DATABRICKS_RUN_TIMEOUT_SECONDS` defaults to `900`.
- `DATABRICKS_POLL_INTERVAL_SECONDS` defaults to `5`.
- `FOUNDRY_MODEL_DEPLOYMENT` defaults to `gpt-4.1-mini` if omitted.
- `FOUNDRY_API_VERSION` defaults to `2025-01-01-preview` if omitted.
- `CONTEXT_CACHE_TTL_SECONDS` defaults to `900` (15 minutes).
- `HEAVY_CONTEXT_CACHE_TTL_SECONDS` defaults to `21600` (6 hours).
- `ENABLE_HEAVY_CONTEXT_FOR_QA` defaults to `false`.
- `ENABLE_HEAVY_CONTEXT_FOR_BRIEFING` defaults to `true`.

## Run The App

From the repo root:

```bash
python3 -m streamlit run src/ui/streamlit_app.py
```

For the CLI entrypoint:

```bash
python3 -m src.app
```

## Deploy To Azure App Service

`https://<resource>.openai.azure.com` is your Azure OpenAI API endpoint, not a URL that hosts this Streamlit UI.
Deploy the app to Azure App Service and use the generated `https://<webapp-name>.azurewebsites.net` URL.

### Option A: Azure Portal (click-by-click)

1. Create a **Linux** Azure App Service web app using **Python 3.11** (or newer).
2. In **Configuration > General settings**, set **Startup Command** to:
   ```bash
   bash startup.sh
   ```
3. In **Configuration > Application settings**, add:
   - `DATABRICKS_HOST`
   - `DATABRICKS_TOKEN`
   - `DATABRICKS_JOB_ID`
   - `DATABRICKS_RUN_TIMEOUT_SECONDS` (optional, defaults to `900`)
   - `DATABRICKS_POLL_INTERVAL_SECONDS` (optional, defaults to `5`)
   - `FOUNDRY_ENDPOINT`
   - `FOUNDRY_API_KEY`
   - `FOUNDRY_MODEL_DEPLOYMENT` (optional, defaults to `gpt-4.1-mini`)
   - `FOUNDRY_API_VERSION` (optional, defaults to `2025-01-01-preview`)
4. In **Deployment Center**, deploy this repository (or ZIP deploy from local).
5. Browse to `https://<webapp-name>.azurewebsites.net`.

### Option B: One-command CLI deployment

Use the helper script included in this repo:

```bash
export RESOURCE_GROUP="rg-signaldesk-ai"
export LOCATION="westeurope"
export APP_SERVICE_PLAN="asp-signaldesk-ai"
export WEBAPP_NAME="signaldesk-ai-<unique>"

export DATABRICKS_HOST="..."
export DATABRICKS_TOKEN="..."
export DATABRICKS_JOB_ID="123456789012345"
export FOUNDRY_ENDPOINT="https://<your-resource>.openai.azure.com"
export FOUNDRY_API_KEY="..."

# Optional overrides:
# export FOUNDRY_MODEL_DEPLOYMENT="gpt-4.1-mini"
# export FOUNDRY_API_VERSION="2025-01-01-preview"
# export DATABRICKS_RUN_TIMEOUT_SECONDS="900"
# export DATABRICKS_POLL_INTERVAL_SECONDS="5"
# export APP_SERVICE_SKU="B1"
# export PYTHON_RUNTIME="PYTHON|3.11"

./scripts/deploy_app_service.sh
```

This script provisions App Service resources (if missing), sets app settings, deploys a ZIP package, and prints the final Azure URL.

### Verify deployment

1. Open `https://<webapp-name>.azurewebsites.net` and confirm the Streamlit page loads.
2. Ask a sample question and verify a model response appears.
3. Click **Generate Briefing** and **Show Raw Context** to verify Databricks + Foundry connectivity.
4. If blank/error, inspect runtime logs:
   ```bash
   az webapp log tail --resource-group <rg> --name <webapp-name>
   ```

## Databricks Job Requirements (Non-Serverless)

The app validates job config at runtime and fails fast unless all of the following are true:

- Job defines `job_clusters`.
- A cluster exists with `job_cluster_key: single_node_cluster`.
- That cluster uses `new_cluster` single-node settings (`num_workers=0`, `spark.databricks.cluster.profile=singleNode`, `spark.master=local[*]`).
- Each task uses `job_cluster_key` and task type `notebook_task` or `python_wheel_task`.
- Tasks do not include `sql_task`, `warehouse_id`, or `compute_key`.

Expected output from the Databricks job task is JSON in `dbutils.notebook.exit(...)` with keys like:

- `latest_dates`
- `regime`
- `top_movers`
- `market_breadth`
- `market_stress`
- `fx_watchlist`
- `macro_trends`
- `heavy` (optional object containing `market_coverage`, `fx_coverage`, `fx_history_summary`, `macro_coverage`)

## Billing Validation Query

Use this query in Databricks SQL to verify job runs are not billed as serverless:

```sql
SELECT
    usage_date,
    sku_name,
    usage_unit,
    usage_quantity,
    usage_metadata
FROM system.billing.usage
WHERE usage_date >= date_sub(current_date(), 7)
  AND usage_metadata.job_id = '<DATABRICKS_JOB_ID>'
ORDER BY usage_date DESC;
```

## Run Checks

The ad hoc test scripts are package-aware and should be run as modules from the repo root:

```bash
python3 -m tests.testy_smoke
python3 -m tests.briefing_test
python3 -m tests.context_test
python3 -m tests.sql_test
python3 -m tests.gold_query_test
```

## Gold Table Dependencies

The app expects these Gold tables:
- `fin_signals_dev.gold.cross_signal_summary`
- `fin_signals_dev.gold.daily_market_snapshot`
- `fin_signals_dev.gold.fx_trend_signals`
- `fin_signals_dev.gold.macro_indicator_trends`
- `fin_signals_dev.gold.top_movers_why` (optional; app falls back gracefully if unavailable)

## Fallback Behavior

If one or more queries fail or return empty data, SignalDesk AI renders fallback context text rather than failing the UI flow.

## Current Limitation

Context assembly is now cached with TTL and invalidates when latest source dates change. Heavy coverage/history queries can be toggled separately for Q&A vs briefing (sidebar controls in Streamlit, with env-var defaults).
