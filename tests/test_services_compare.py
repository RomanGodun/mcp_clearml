from __future__ import annotations

from typing import Any

from mcp_clearml.services import compare as svc


def _task(
    tid: str,
    status: str = "completed",
    type_: str = "training",
    user: str = "alice",
    project: str = "proj",
    metrics: dict[str, dict[str, dict[str, Any]]] | None = None,
    parameters: dict[str, Any] | None = None,
    artifacts: dict[str, Any] | None = None,
    models: dict[str, list[dict[str, Any]]] | None = None,
    last_update: str | None = None,
) -> dict[str, Any]:
    return {
        "id": tid,
        "status": status,
        "type": type_,
        "user": user,
        "project": project,
        "metrics": metrics or {},
        "parameters": parameters or {},
        "artifacts": artifacts or {},
        "models": models or {"input": [], "output": []},
        "last_update": last_update,
    }


def test_compare_tasks_builds_summary_and_comparisons(monkeypatch):
    tasks = [
        _task(
            "t1",
            metrics={"acc": {"val": {"last_value": 0.9, "min_value": 0.1, "max_value": 0.9, "iterations": 2}}},
            parameters={"lr": 0.001, "optim": {"name": "adam"}},
            artifacts={"model": {"uri": "s3://a"}},
            models={"input": [{"framework": "tf"}], "output": [{"framework": "pt"}]},
            last_update="2024-01-02T00:00:00Z",
        ),
        _task(
            "t2",
            metrics={"acc": {"val": {"last_value": 0.8, "min_value": 0.2, "max_value": 0.8, "iterations": 2}}, "loss": {"train": {"last_value": 0.1}}},
            parameters={"lr": 0.002, "optim": {"name": "sgd"}},
            artifacts={"logs": {}},
            models={"input": [], "output": [{"framework": "pt"}]},
            last_update="2024-01-03T00:00:00Z",
        ),
    ]

    monkeypatch.setattr(svc, "svc_tasks_full_info", lambda ids: tasks)

    out = svc.compare_tasks(["t1", "t2"])  # type: ignore

    # Summary
    assert out["summary"]["num_tasks"] == 2
    assert out["summary"]["statuses"]["completed"] == 2
    assert "latest_updates" in out["summary"]

    # Comparisons
    aligned = out["comparisons"]["metrics"]
    assert "acc" in aligned and "val" in aligned["acc"]
    # Parameters diff should include differing keys
    params_diff = out["comparisons"]["parameters"]=out["comparisons"].get("parameters_diff", {})
    assert any("optim" in k or "lr" in k for k in params_diff.keys())

