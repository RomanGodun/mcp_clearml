"""
Centralized tool documentation helpers for MCP model/tool selection.

This module contains standardized selection guides that can be referenced
from tool docstrings to help agent models choose the correct tool.
"""

from __future__ import annotations

from typing import Final


# High-level selection rules for categories
CATEGORY_GUIDE: Final[dict[str, str]] = {
    "projects": (
        "For project info/overview, use get_project_stats (aggregate counters, no task list). "
        "For per-project task listings (stats + tasks), see the tasks_by_project category."
    ),
    "tasks_bulk": (
        "Use get_tasks_core_info for core fields (id, name, status, type, project, dates, tags, user, parent). "
        "Use get_tasks_full_info when you also need parameters, metrics, artifacts, and models."
    ),
    "tasks_search": (
        "Use find_tasks_core_info_by_pattern to retrieve IDs matching name/status/tags. "
        "Use find_tasks_full_info_by_pattern to retrieve full per-task profiles for matches."
    ),
    "models_search": (
        "Use find_models_core_info_by_pattern for core model fields (id, name, project, framework, created, tags, task_id). "
        "Use find_models_full_info_by_pattern when you also need url/uri."
    ),
    "models_by_id": (
        "Use find_models_core_info when you already have model IDs and need core fields. "
        "Use find_models_full_info when you also need url/uri for those IDs."
    ),
    "tasks_by_project": (
        "Use get_tasks_core_info_by_project for project statistics plus a core task list. "
        "Use get_tasks_full_info_by_project for statistics plus full per-task profiles."
    ),
    "datasets": (
        "Use find_datasets_by_project to list datasets in a project (pass recursive_project_search=True to include subprojects). "
        "Use find_datasets_by_pattern to find by partial name. "
        "Use get_datasets_full_info when you need sizes/uploader/metadata parsed into a dict."
    ),
}


# Per-tool concise guidance (English; referenced by docstrings or external UIs)
TOOL_GUIDE: Final[dict[str, str]] = {
    # Projects
    "list_of_all_projects": (
        "List all ClearML projects (id, name). Then drill down using get_project_stats or tasks-by-project tools."
    ),
    "find_project_by_pattern": (
        "Find projects by name substring (case-insensitive). Use results with get_project_stats or tasks-by-project tools."
    ),
    "get_project_stats": (
        "Project info/overview: return aggregate counters for a project (no task list). "
        "Ideal for generic 'project info' queries. For stats + tasks, use get_tasks_core_info_by_project or get_tasks_full_info_by_project."
    ),

    # Tasks by project
    "get_tasks_core_info_by_project": (
        "Return project statistics and core info list for all tasks in the project."
    ),
    "get_tasks_full_info_by_project": (
        "Return project statistics and full info list (core + params/metrics/artifacts/models) for all tasks."
    ),

    # Tasks by ids (bulk)
    "get_tasks_core_info": (
        "Given task_ids, return core task fields for each (id, name, status, type, project, created, last_update, tags, comment, user, parent)."
    ),
    "get_tasks_full_info": (
        "Given task_ids, return full profiles for each (core + parameters, metrics, artifacts, models)."
    ),
    "get_tasks_parameters": (
        "Given task_ids, return parameters/configuration per task."
    ),
    "get_tasks_metrics": (
        "Given task_ids, return reported scalars/metrics per task with basic stats (last/min/max, count)."
    ),
    "get_tasks_artifacts": (
        "Given task_ids, return artifacts/outputs per task (type, mode, uri, content_type, timestamp if available)."
    ),
    "get_tasks_models": (
        "Given task_ids, return model metadata per task, separated into input/output lists."
    ),

    # Task search by pattern
    "find_tasks_core_info_by_pattern": (
        "Search across projects by name substring/status/tags and return only matching task IDs."
    ),
    "find_tasks_full_info_by_pattern": (
        "Search across projects by name substring/status/tags and return full task profiles for matches."
    ),

    # Models search by pattern
    "find_models_by_pattern": (
        "Return model info filtered by name substring (core fields plus url/uri when available)."
    ),
    # Models by IDs
    "find_models_info": (
        "Return model info for specified IDs (core fields plus url/uri when available)."
    ),

    # Datasets
    "find_datasets_by_project": (
        "Return dataset dicts for a given project. Optional recursive_project_search includes subprojects."
    ),
    "find_datasets_by_pattern": (
        "Return dataset dicts whose names contain the given pattern (server-side partial match when supported)."
    ),
    "get_datasets_full_info": (
        "Given dataset_ids, return full dataset info including sizes, uploader, and parsed metadata (CSV/CSV.gz/JSON)."
    ),

    # Compare
    "compare_tasks": (
        "Compare multiple tasks by metrics; optionally restrict to specified metric names."
    ),
}


def get_tool_guide(tool_name: str) -> str:
    """Return concise guidance for the specified tool name.

    This helper can be used by UIs or agent scaffolds to surface the right
    tool to users and models. Returns an empty string for unknown tools.
    """
    return TOOL_GUIDE.get(tool_name, "")



