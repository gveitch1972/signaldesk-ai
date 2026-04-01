import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from src.config import (
    DATABRICKS_HOST,
    DATABRICKS_JOB_ID,
    DATABRICKS_POLL_INTERVAL_SECONDS,
    DATABRICKS_RUN_TIMEOUT_SECONDS,
    DATABRICKS_TOKEN,
    ENABLE_SERVERLESS_COMPUTE,
)

_ALLOWED_TASK_TYPES = {"notebook_task", "python_wheel_task", "spark_python_task"}
_FORBIDDEN_TASK_KEYS = {"sql_task", "warehouse_id", "compute_key"}
_VALIDATED_JOB_ID: str | None = None
_CONTEXT_TASK_KEY = "build_briefing_context"


def _as_bool(value: str, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _use_serverless_compute() -> bool:
    return _as_bool(os.getenv("USE_SERVERLESS_COMPUTE"), ENABLE_SERVERLESS_COMPUTE)


def _require(value: str, env_name: str) -> str:
    if value:
        return value
    raise RuntimeError(f"Missing required Databricks setting: {env_name}")


def _build_base_url() -> str:
    host = _require(DATABRICKS_HOST, "DATABRICKS_HOST").strip().rstrip("/")
    if host.startswith("http://") or host.startswith("https://"):
        return host
    return f"https://{host}"


def _api_request(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    token = _require(DATABRICKS_TOKEN, "DATABRICKS_TOKEN")
    url = f"{_build_base_url()}{path}"
    body = None
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url=url, data=body, headers=headers, method=method.upper())
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Databricks API error {exc.code} for {path}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Databricks API connection error for {path}: {exc.reason}") from exc


def _job_id() -> int:
    raw = _require(DATABRICKS_JOB_ID, "DATABRICKS_JOB_ID").strip()
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError("DATABRICKS_JOB_ID must be a numeric Databricks job id.") from exc


def get_job_settings(job_id: int | None = None) -> dict[str, Any]:
    effective_job_id = _job_id() if job_id is None else job_id
    query = urllib.parse.urlencode({"job_id": str(effective_job_id)})
    data = _api_request("GET", f"/api/2.1/jobs/get?{query}")
    settings = data.get("settings", {})
    if not settings:
        raise RuntimeError(f"Databricks job {effective_job_id} has no settings.")
    return settings


def _validate_new_cluster(cluster: dict[str, Any]) -> None:
    if not isinstance(cluster, dict) or not cluster:
        raise RuntimeError("Databricks job cluster must define new_cluster.")
    if cluster.get("num_workers") != 0:
        raise RuntimeError("Databricks job cluster must set num_workers=0 for single-node execution.")
    spark_conf = cluster.get("spark_conf", {})
    if spark_conf.get("spark.databricks.cluster.profile") != "singleNode":
        raise RuntimeError(
            "Databricks job cluster must set spark.databricks.cluster.profile=singleNode."
        )
    if spark_conf.get("spark.master") != "local[*]":
        raise RuntimeError("Databricks job cluster must set spark.master=local[*].")


def validate_non_serverless_job_settings(settings: dict[str, Any]) -> None:
    job_clusters = settings.get("job_clusters") or []
    if not job_clusters:
        raise RuntimeError("Databricks job must define at least one job_clusters entry.")

    cluster_map: dict[str, dict[str, Any]] = {}
    for entry in job_clusters:
        key = entry.get("job_cluster_key")
        if not key:
            raise RuntimeError("Each job_clusters entry must include job_cluster_key.")
        cluster_map[key] = entry.get("new_cluster") or {}
        _validate_new_cluster(cluster_map[key])

    if "single_node_cluster" not in cluster_map:
        raise RuntimeError("Databricks job must include job_cluster_key='single_node_cluster'.")

    tasks = settings.get("tasks") or []
    if not tasks:
        raise RuntimeError("Databricks job must define at least one task.")

    for task in tasks:
        task_key = task.get("task_key", "<unknown>")
        job_cluster_key = task.get("job_cluster_key")
        if not job_cluster_key:
            raise RuntimeError(f"Task '{task_key}' must define job_cluster_key.")
        if job_cluster_key not in cluster_map:
            raise RuntimeError(f"Task '{task_key}' references unknown job_cluster_key '{job_cluster_key}'.")
        for key in _FORBIDDEN_TASK_KEYS:
            if key in task:
                raise RuntimeError(f"Task '{task_key}' uses forbidden compute field '{key}'.")
        task_types = [name for name in _ALLOWED_TASK_TYPES if name in task]
        if len(task_types) != 1:
            raise RuntimeError(
                f"Task '{task_key}' must use exactly one supported task type: {sorted(_ALLOWED_TASK_TYPES)}."
            )


def ensure_non_serverless_job_configuration() -> None:
    global _VALIDATED_JOB_ID

    if _use_serverless_compute():
        return

    current = str(_job_id())
    if _VALIDATED_JOB_ID == current:
        return

    settings = get_job_settings(int(current))
    validate_non_serverless_job_settings(settings)
    _VALIDATED_JOB_ID = current


def _poll_run_completion(run_id: int) -> dict[str, Any]:
    started_at = time.time()
    while True:
        query = urllib.parse.urlencode({"run_id": str(run_id)})
        details = _api_request("GET", f"/api/2.1/jobs/runs/get?{query}")
        state = details.get("state", {})
        life_cycle_state = state.get("life_cycle_state")
        result_state = state.get("result_state")
        state_message = state.get("state_message", "")

        if life_cycle_state in {"TERMINATED", "SKIPPED", "INTERNAL_ERROR"}:
            if result_state != "SUCCESS":
                raise RuntimeError(
                    f"Databricks job run {run_id} failed with state={life_cycle_state} "
                    f"result={result_state}: {state_message}"
                )
            return details

        if time.time() - started_at > DATABRICKS_RUN_TIMEOUT_SECONDS:
            raise RuntimeError(f"Timed out waiting for Databricks job run {run_id}.")

        time.sleep(max(1, DATABRICKS_POLL_INTERVAL_SECONDS))


def _resolve_output_run_id(run_details: dict[str, Any], fallback_run_id: int) -> int:
    tasks = run_details.get("tasks")
    if isinstance(tasks, list) and tasks:
        for task in tasks:
            if task.get("task_key") == _CONTEXT_TASK_KEY and task.get("run_id") is not None:
                return int(task["run_id"])
        for task in tasks:
            if task.get("run_id") is not None:
                return int(task["run_id"])
    return int(fallback_run_id)


def run_context_job(include_heavy: bool) -> dict[str, Any]:
    ensure_non_serverless_job_configuration()

    payload = {
        "job_id": _job_id(),
        "notebook_params": {
            "include_heavy": "true" if include_heavy else "false",
        },
    }
    run = _api_request("POST", "/api/2.1/jobs/run-now", payload)
    run_id = run.get("run_id")
    if run_id is None:
        raise RuntimeError("Databricks run-now did not return run_id.")

    run_details = _poll_run_completion(int(run_id))
    output_run_id = _resolve_output_run_id(run_details, fallback_run_id=int(run_id))

    query = urllib.parse.urlencode({"run_id": str(output_run_id)})
    output = _api_request("GET", f"/api/2.1/jobs/runs/get-output?{query}")
    notebook_output = output.get("notebook_output", {})
    result = notebook_output.get("result")
    if not result:
        raise RuntimeError(
            "Databricks job output did not include notebook_output.result JSON payload."
        )
    try:
        parsed = json.loads(result)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Databricks job output result is not valid JSON.") from exc
    if not isinstance(parsed, dict):
        raise RuntimeError("Databricks job output JSON must be an object.")
    return parsed


def build_billing_validation_query(days_back: int = 7) -> str:
    days = max(1, int(days_back))
    job_id = _job_id()
    return f"""
SELECT
    usage_date,
    sku_name,
    usage_unit,
    usage_quantity,
    usage_metadata
FROM system.billing.usage
WHERE usage_date >= date_sub(current_date(), {days})
  AND usage_metadata.job_id = '{job_id}'
ORDER BY usage_date DESC
""".strip()
