#!/usr/bin/env bash
set -euo pipefail

PORT_VALUE="${PORT:-8501}"

exec python -m streamlit run src/ui/streamlit_app.py \
  --server.address 0.0.0.0 \
  --server.port "${PORT_VALUE}" \
  --server.headless true
