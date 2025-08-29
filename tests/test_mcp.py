from __future__ import annotations

import pytest

from mcp_clearml.mcp import ensure_clearml_connection_ready


def test_ensure_clearml_connection_ready_ok(monkeypatch):
    class _Session:
        def __init__(self):
            pass
    monkeypatch.setitem(__import__('sys').modules, 'clearml.backend_api', type('pkg', (), {'Session': _Session}))
    ensure_clearml_connection_ready()  # should not raise


def test_ensure_clearml_connection_ready_error(monkeypatch):
    class _Session:
        def __init__(self):
            raise RuntimeError("bad creds")
    monkeypatch.setitem(__import__('sys').modules, 'clearml.backend_api', type('pkg', (), {'Session': _Session}))
    with pytest.raises(RuntimeError):
        ensure_clearml_connection_ready()


