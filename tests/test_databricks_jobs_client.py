import pytest

import src.databricks_jobs_client as databricks_jobs_client
from src.databricks_jobs_client import (
    _resolve_output_run_id,
    ensure_non_serverless_job_configuration,
    validate_non_serverless_job_settings,
)


def _valid_settings():
    return {
        "job_clusters": [
            {
                "job_cluster_key": "single_node_cluster",
                "new_cluster": {
                    "num_workers": 0,
                    "spark_conf": {
                        "spark.databricks.cluster.profile": "singleNode",
                        "spark.master": "local[*]",
                    },
                },
            }
        ],
        "tasks": [
            {
                "task_key": "build_briefing_context",
                "job_cluster_key": "single_node_cluster",
                "notebook_task": {"notebook_path": "/Repos/project/notebook"},
            }
        ],
    }


def test_validate_non_serverless_settings_accepts_notebook_task():
    validate_non_serverless_job_settings(_valid_settings())


def test_validate_non_serverless_settings_accepts_spark_python_task():
    settings = _valid_settings()
    settings["tasks"][0].pop("notebook_task")
    settings["tasks"][0]["spark_python_task"] = {"python_file": "dbfs:/jobs/main.py"}

    validate_non_serverless_job_settings(settings)


def test_validate_non_serverless_settings_rejects_sql_task():
    settings = _valid_settings()
    settings["tasks"][0]["sql_task"] = {"query_id": "abc"}

    with pytest.raises(RuntimeError, match="forbidden compute field 'sql_task'"):
        validate_non_serverless_job_settings(settings)


def test_validate_non_serverless_settings_rejects_missing_job_cluster_key():
    settings = _valid_settings()
    del settings["tasks"][0]["job_cluster_key"]

    with pytest.raises(RuntimeError, match="must define job_cluster_key"):
        validate_non_serverless_job_settings(settings)


def test_validate_non_serverless_settings_rejects_non_single_node_cluster():
    settings = _valid_settings()
    settings["job_clusters"][0]["new_cluster"]["num_workers"] = 1

    with pytest.raises(RuntimeError, match="num_workers=0"):
        validate_non_serverless_job_settings(settings)


def test_resolve_output_run_id_prefers_context_task_run():
    details = {
        "tasks": [
            {"task_key": "upstream", "run_id": 111},
            {"task_key": "build_briefing_context", "run_id": 222},
        ]
    }
    assert _resolve_output_run_id(details, fallback_run_id=999) == 222


def test_resolve_output_run_id_falls_back_to_first_task_run():
    details = {"tasks": [{"task_key": "upstream", "run_id": 111}]}
    assert _resolve_output_run_id(details, fallback_run_id=999) == 111


def test_resolve_output_run_id_falls_back_to_parent_run():
    assert _resolve_output_run_id({}, fallback_run_id=999) == 999


def test_serverless_mode_skips_non_serverless_validation(monkeypatch):
    monkeypatch.setenv("USE_SERVERLESS_COMPUTE", "true")
    monkeypatch.setattr(databricks_jobs_client, "_VALIDATED_JOB_ID", None)

    def fail_if_called(job_id: int | None = None):
        raise AssertionError("get_job_settings should not be called in serverless mode")

    monkeypatch.setattr(databricks_jobs_client, "get_job_settings", fail_if_called)
    ensure_non_serverless_job_configuration()
