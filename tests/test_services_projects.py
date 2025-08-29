from __future__ import annotations

from types import SimpleNamespace

from mcp_clearml.services import projects as svc


def test_list_and_find_projects(monkeypatch):
    class _P:
        def __init__(self, _id, name):
            self.id = _id
            self.name = name

    monkeypatch.setattr(
        "mcp_clearml.services.projects.Task.get_projects",
        staticmethod(lambda: [_P("1", "Alpha"), _P("2", "Beta")]),
    )
    res = svc.list_projects()
    assert {p["name"] for p in res} == {"Alpha", "Beta"}
    found = svc.find_projects_by_pattern("alp")
    assert found == [{"id": "1", "name": "Alpha"}]


def test_get_project_statistics_uses_helper(monkeypatch):
    # one task with minimal fields
    monkeypatch.setattr(
        "mcp_clearml.services.projects.Task.get_tasks",
        staticmethod(lambda project_name=None: [SimpleNamespace(status="completed", task_type="training", data=SimpleNamespace(user="u", tags=[], created="2024-01-01T00:00:00Z"))]),
    )
    stats = svc.get_project_statistics("proj")
    assert stats["total_tasks"] == 1


