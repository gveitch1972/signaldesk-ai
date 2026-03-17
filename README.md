# SignalDesk AI

SignalDesk AI is a small Python 3 app that builds market briefings from Databricks data and Azure OpenAI.

## Setup

Use Python 3, not the system `python` command if that still points to Python 2.7 on your machine.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e .
```

## Run The App

From the repo root:

```bash
python3 -m streamlit run src/ui/streamlit_app.py
```

For the CLI entrypoint:

```bash
python3 -m src.app
```

## Run Checks

The ad hoc test scripts are package-aware now and should be run as modules from the repo root:

```bash
python3 -m tests.testy_smoke
python3 -m tests.briefing_test
python3 -m tests.context_test
python3 -m tests.sql_test
python3 -m tests.gold_query_test
```
