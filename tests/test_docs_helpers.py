from __future__ import annotations

from mcp_clearml import docs


def test_category_and_tool_guides_present():
    assert "projects" in docs.CATEGORY_GUIDE
    assert "get_project_stats" in docs.TOOL_GUIDE
    assert docs.get_tool_guide("get_project_stats")

