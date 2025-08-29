from __future__ import annotations

from types import SimpleNamespace
from pathlib import Path
import sys

from mcp_clearml.services import datasets as svc


def test_parse_metadata_from_uri_tries_formats(monkeypatch, tmp_path: Path):
    # create a tiny json file
    p = tmp_path / "meta.json"
    p.write_text('{"a": 1}')

    class _SM:
        @staticmethod
        def download_file(remote_url: str, skip_zero_size_check: bool = False):
            return str(p)

    monkeypatch.setattr("mcp_clearml.services.datasets.StorageManager", _SM)

    meta, is_no_meta, reason = svc._parse_metadata_from_uri("dummy://uri")  # type: ignore
    assert meta == {"a": 1}
    assert is_no_meta is False
    assert reason is None


def test_find_datasets_by_project_empty(monkeypatch):
    class _Dataset:
        @staticmethod
        def list_datasets(**kwargs):
            return []
    # Functions import `Dataset` from the `clearml` top-level package at call time
    # so patch sys.modules entry instead of module attribute
    monkeypatch.setitem(sys.modules, 'clearml', type('pkg', (), {'Dataset': _Dataset}))
    out = svc.find_datasets_by_project("proj")
    assert isinstance(out, dict) and "error" in out


def test_find_datasets_by_pattern_returns_items(monkeypatch):
    class _Dataset:
        @staticmethod
        def list_datasets(**kwargs):
            return [{"id": "d1"}, {"id": "d2"}]
    monkeypatch.setitem(sys.modules, 'clearml', type('pkg', (), {'Dataset': _Dataset}))
    out = svc.find_datasets_by_pattern("name")
    assert isinstance(out, list) and out[0]["id"] == "d1"

