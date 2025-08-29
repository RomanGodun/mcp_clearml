from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any

import pytest

import mcp_clearml.mcp as m


@pytest.mark.asyncio
async def test_guides_ok(monkeypatch):
    # list_tools_guide
    out = await m.list_tools_guide()
    assert isinstance(out, dict) and out

    # get_tool_guide
    out2 = await m.get_tool_guide("get_project_stats")
    assert out2.get("tool") == "get_project_stats"

    # list_categories_guide
    out3 = await m.list_categories_guide()
    assert isinstance(out3, dict) and "projects" in out3

    # generate_tools_guide_markdown
    md = await m.generate_tools_guide_markdown()
    assert "## Tools" in md.get("markdown", "")


@pytest.mark.asyncio
async def test_projects_and_tasks_tools(monkeypatch):
    # Mock services
    monkeypatch.setattr(m, "svc_list_projects", lambda: [{"id": "1", "name": "A"}])
    monkeypatch.setattr(m, "svc_find_projects_by_pattern", lambda p: [{"id": "1", "name": "A"}] if p.lower() in "a" else [])
    monkeypatch.setattr(m, "svc_project_stats", lambda name: {"total_tasks": 0})
    monkeypatch.setattr(m, "svc_tasks_core_info", lambda ids: [{"id": i} for i in ids])
    monkeypatch.setattr(m, "svc_tasks_full_info", lambda ids: [{"id": i, "parameters": {}} for i in ids])
    monkeypatch.setattr(m, "svc_tasks_core_by_project", lambda n: {"statistics": {}, "tasks_details": []})
    monkeypatch.setattr(m, "svc_tasks_full_by_project", lambda n: {"statistics": {}, "tasks_details": []})
    monkeypatch.setattr(m, "svc_find_tasks_ids_by_pattern", lambda *a, **k: ["t1", "t2"]) 
    monkeypatch.setattr(m, "svc_find_tasks_full_by_pattern", lambda *a, **k: [{"id": "t1"}, {"id": "t2"}])

    assert await m.list_of_all_projects() == [{"id": "1", "name": "A"}]
    assert await m.find_project_by_pattern("a") == [{"id": "1", "name": "A"}]
    assert (await m.get_project_stats("A"))["total_tasks"] == 0
    assert (await m.get_tasks_core_info(["t1"]))[0]["id"] == "t1"
    assert (await m.get_tasks_full_info(["t1"]))[0]["id"] == "t1"
    assert "statistics" in await m.get_tasks_core_info_by_project("A")
    assert "statistics" in await m.get_tasks_full_info_by_project("A")
    assert await m.find_tasks_core_info_by_pattern("n", None, None) == ["t1", "t2"]
    assert len(await m.find_tasks_full_info_by_pattern("n", None, None)) == 2


@pytest.mark.asyncio
async def test_models_and_datasets_tools(monkeypatch):
    # Models
    class _Model:
        def __init__(self, **kw): self.__dict__.update(kw)
    monkeypatch.setattr(m, "Model", SimpleNamespace(query_models=lambda project_name=None: [_Model(name="A", framework="tf", tags=["x"], id="m1", url=None, uri=None)]))
    monkeypatch.setattr(m, "svc_filter_models", lambda models, name_lower, fw, tags: models)
    monkeypatch.setattr(m, "svc_model_dict", lambda mod: {"id": getattr(mod, "id", None) or "m1"})
    monkeypatch.setattr(m, "svc_models_info", lambda ids: [{"id": i} for i in ids])

    r = await m.find_models_by_pattern("a")
    assert r and r[0]["id"] == "m1"
    r = await m.find_models_info(["m1"]) 
    assert r and r[0]["id"] == "m1"

    # Datasets delegate
    monkeypatch.setattr(m, "svc_find_datasets_by_project", lambda name, rec: [{"id": "d1"}])
    monkeypatch.setattr(m, "svc_find_datasets_by_pattern", lambda p: [{"id": "d2"}])
    monkeypatch.setattr(m, "svc_datasets_full_info", lambda ids: [{"id": i} for i in ids])

    assert (await m.find_datasets_by_project("p")) == [{"id": "d1"}]
    assert (await m.find_datasets_by_pattern("p")) == [{"id": "d2"}]
    assert (await m.get_datasets_full_info(["d1"])) == [{"id": "d1"}]


@pytest.mark.asyncio
async def test_compare_tasks(monkeypatch):
    monkeypatch.setattr(m, "svc_compare_tasks", lambda ids: {"summary": {"num_tasks": len(ids)}, "comparisons": {}, "tasks": []})
    out = await m.compare_tasks(["t1", "t2"]) 
    assert out["summary"]["num_tasks"] == 2

