from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import builtins
import pytest

from mcp_clearml.services import tasks as svc


class _DummyTask:
    def __init__(self, **kwargs: Any) -> None:
        self.__dict__.update(kwargs)
    def get_project_name(self):
        return getattr(self, "project_name", None)


def test_extract_task_core_info_handles_enums_and_missing_fields():
    enum_like = SimpleNamespace(value="Completed")
    data = SimpleNamespace(
        created="2024-01-02T00:00:00Z",
        last_update="2024-01-02T05:00:00Z",
        user="alice",
        parent=None,
        tags=["x"],
    )
    t = _DummyTask(id="t1", name="task", status=enum_like, task_type="training", data=data, project_name="proj")
    core = svc.extract_task_core_info(t)
    assert core["status"] == "Completed"
    assert core["type"] == "training"
    assert core["project"] == "proj"
    assert core["tags"] == ["x"]


def test_extract_task_artifacts_and_models_metrics_params_robust():
    t = _DummyTask(
        artifacts={
            "a": SimpleNamespace(type="blob", mode="download", uri="s3://x", content_type="text", timestamp=1)
        },
        models={
            "input": [SimpleNamespace(id="m1", name="in", url=None, framework="tf", uri=None)],
            "output": [SimpleNamespace(id="m2", name="out", url=None, framework="pt", uri=None)],
        },
        get_reported_scalars=lambda: {"acc": {"val": {"y": [0.1, 0.2]}}},
        get_parameters_as_dict=lambda: {"a": 1},
    )
    assert "a" in svc.extract_task_artifacts(t)
    m = svc.extract_task_models(t)
    assert m["input"][0]["framework"] == "tf"
    mx = svc.extract_task_metrics(t)
    assert mx["acc"]["val"]["last_value"] == 0.2
    assert svc.extract_task_parameters(t)["a"] == 1


def test_get_core_info_uses_Task_get_tasks(monkeypatch):
    calls = {}
    def fake_get_tasks(task_ids=None, project_name=None):
        calls["called"] = True
        return [
            _DummyTask(id="t1", name="n1", status="completed", task_type="training", data=SimpleNamespace(tags=[])),
        ]
    monkeypatch.setattr("mcp_clearml.services.tasks.Task.get_tasks", staticmethod(fake_get_tasks))
    res = svc.get_core_info(["t1"])  # type: ignore
    assert res and res[0]["id"] == "t1"


def test_find_tasks_ids_by_pattern_builds_filter_and_handles_dict_response(monkeypatch):
    def fake_query_tasks(**kwargs):
        return [{"id": "t1"}, {"id": "t2"}]
    monkeypatch.setattr("mcp_clearml.services.tasks.Task.query_tasks", staticmethod(fake_query_tasks))
    ids = svc.find_tasks_ids_by_pattern(task_name_pattern="acc", status="completed", tags=["x"])  # type: ignore
    assert ids == ["t1", "t2"]


def test_find_tasks_full_by_pattern_loads_each_task(monkeypatch):
    def fake_query_tasks(**kwargs):
        return ["t1", "t2"]
    def fake_get_task(task_id=None):
        return _DummyTask(id=task_id, name="n", data=SimpleNamespace(tags=[]))
    monkeypatch.setattr("mcp_clearml.services.tasks.Task.query_tasks", staticmethod(fake_query_tasks))
    monkeypatch.setattr("mcp_clearml.services.tasks.Task.get_task", staticmethod(fake_get_task))
    details = svc.find_tasks_full_by_pattern("n", None, None)  # type: ignore
    assert {d["id"] for d in details} == {"t1", "t2"}


