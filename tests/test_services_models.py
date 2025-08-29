from __future__ import annotations

from types import SimpleNamespace

from mcp_clearml.services import models as svc


def test_filter_models_by_name_framework_and_tags():
    ms = [
        SimpleNamespace(name="A", framework="tf", tags=["x", "y"]),
        SimpleNamespace(name="B", framework="pt", tags=["y"]),
    ]
    out = svc.filter_models(ms, name_lower="a", framework=None, tags=None)
    assert [m.name for m in out] == ["A"]
    out = svc.filter_models(ms, name_lower=None, framework="pt", tags=["y"])
    assert [m.name for m in out] == ["B"]


def test_to_model_dict_maps_fields():
    m = SimpleNamespace(
        id="m1", name="n", project="p", framework="tf", created="c", tags=["t"], task="tid", url="u", uri="r"
    )
    d = svc.to_model_dict(m)
    assert d["id"] == "m1" and d["url"] == "u" and d["uri"] == "r"


