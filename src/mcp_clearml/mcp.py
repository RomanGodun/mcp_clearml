"""ClearML MCP Server implementation.

This module exposes MCP tools while delegating business logic to services/* and
data shaping to utils in task_utils.py. The public tool names, parameters,
and response schemas are preserved to maintain compatibility with existing
clients and tests.
"""

from typing import Any

from clearml import Model, Task
from .services.datasets import (
    get_datasets_full_info as svc_datasets_full_info,
    find_datasets_by_project as svc_find_datasets_by_project,
    find_datasets_by_pattern as svc_find_datasets_by_pattern,
)
from fastmcp import FastMCP
from .services.tasks import (
    extract_task_artifacts,
    extract_task_models,
    extract_task_metrics,
    extract_task_parameters,
)
from .services.projects import (
    list_projects as svc_list_projects, 
    find_projects_by_pattern as svc_find_projects_by_pattern, 
    get_project_statistics as svc_project_stats
)
from .services.tasks import (
    get_core_info as svc_tasks_core_info,
    get_full_info as svc_tasks_full_info,
    get_core_info_by_project as svc_tasks_core_by_project,
    get_full_info_by_project as svc_tasks_full_by_project,
    find_tasks_ids_by_pattern as svc_find_tasks_ids_by_pattern,
    find_tasks_full_by_pattern as svc_find_tasks_full_by_pattern,
)
from .services.models import (
    filter_models as svc_filter_models,
    to_model_dict as svc_model_dict,
    get_models_info as svc_models_info,
)
from .services.compare import compare_tasks as svc_compare_tasks
from .docs import TOOL_GUIDE, CATEGORY_GUIDE


mcp = FastMCP("mcp-clearml")

def ensure_clearml_connection_ready() -> None:
    """Verify ClearML connectivity via backend API.

    This performs a lightweight API call using a backend session to ensure
    credentials and server connectivity are valid before starting the MCP server.
    """
    try:
        # Local import to avoid hard dependency at import time
        from clearml.backend_api import Session  # type: ignore

        # The most lightweight check: session construction only.
        # If credentials/config are invalid, this typically raises early.
        _ = Session()
    except Exception as e:
        raise RuntimeError(f"Failed to validate ClearML connection: {e!s}")

@mcp.tool()
async def list_tools_guide() -> dict[str, str]:
    """
    Return concise guidance for all available MCP tools.

    Use this to help an agent/model choose the correct tool by intent.
    """
    try:
        return dict(TOOL_GUIDE)
    except Exception as e:
        return {"error": f"Failed to list tools guide: {e!s}"}

@mcp.tool()
async def get_tool_guide(tool_name: str) -> dict[str, str] | dict[str, str]:
    """
    Return concise guidance for a specific MCP tool name.

    If unknown tool name is provided, an empty guide string is returned.
    """
    try:
        guide = TOOL_GUIDE.get(tool_name, "")
        return {"tool": tool_name, "guide": guide}
    except Exception as e:
        return {"error": f"Failed to get tool guide: {e!s}"}

@mcp.tool()
async def list_categories_guide() -> dict[str, str]:
    """
    Return high-level categories guidance for tool selection.

    Use this to help decide between project-level stats, bulk task info,
    task search, and model search flows.
    """
    try:
        return dict(CATEGORY_GUIDE)
    except Exception as e:
        return {"error": f"Failed to list categories guide: {e!s}"}

@mcp.tool()
async def generate_tools_guide_markdown() -> dict[str, str]:
    """
    Generate a consolidated Markdown guide for tool selection.

    The output includes category-level guidance and per-tool quick references,
    suitable for copy-paste into README or a separate docs page.
    """
    try:
        lines: list[str] = []
        lines.append("# ClearML MCP Tools Guide\n")
        lines.append("\n")
        lines.append("## Categories\n")
        for category, guide in CATEGORY_GUIDE.items():
            lines.append(f"- **{category}**: {guide}")
        lines.append("\n\n")
        lines.append("## Tools\n")
        for tool, guide in TOOL_GUIDE.items():
            lines.append(f"- **{tool}**: {guide}")
        markdown = "\n".join(lines)
        return {"markdown": markdown}
    except Exception as e:
        return {"error": f"Failed to generate tools guide markdown: {e!s}"}

@mcp.tool()
async def list_of_all_projects() -> list[dict[str, Any]]:
    """
    List all ClearML projects (id, name).

    - Input: none
    - Output: list[{ id: str|None, name: str }]

    When to use:
    - As a first step to discover projects before drilling down.

    See also docs guides: tools → list_of_all_projects; categories → projects.
    """
    try:
        return svc_list_projects()
    except Exception as e:
        return [{"error": f"Failed to list projects: {e!s}"}]

@mcp.tool()
async def find_project_by_pattern(pattern: str) -> list[dict[str, Any]]:
    """
    Find projects by case-insensitive name substring.

    - Input: pattern (str)
    - Output: list[{ id: str|None, name: str }]

    When to use:
    - You have a fragment of the project name and need matches.

    See also docs guides: tools → find_project_by_pattern; categories → projects.
    """
    try:
        return svc_find_projects_by_pattern(pattern)
    except Exception as e:
        return [{"error": f"Failed to find projects by pattern: {e!s}"}]

@mcp.tool()
async def get_project_stats(project_name: str) -> dict[str, Any]:
    """
    Project info/overview: return aggregate counters for a project (no task list).

    Use this when you need counters only (no task list). The response matches the
    "statistics" object returned by get_task_core_info_by_project(project_name):
      - total_tasks: total number of tasks in the project
      - tasks_per_status: count of tasks by status
      - tasks_per_type: count of tasks by type
      - tasks_per_user: count of tasks by user
      - tasks_per_tags: count of tasks by tag (tags starting with "pipe: " are grouped as "pipe: ...")
      - tasks_per_day: count of tasks by creation date (DD.MM.YYYY)

    If you also need the full list of tasks and their fields, call get_tasks_info_by_project
    (or get_full_tasks_info_by_project for full per-task details).
    For details on a single task, call get_task_core_info_by_id (or get_full_task_info_by_id).
    When to use:
    - Answering generic prompts like "Give project info for <project_name>". If a task list is required, use get_tasks_core_info_by_project.

    See also docs guides: tools → get_project_stats; categories → projects.
    """
    try:
        return svc_project_stats(project_name)
    except Exception as e:
        return {"error": f"Failed to get project stats: {e!s}"}

@mcp.tool()
async def get_tasks_core_info(task_ids: list[str]) -> list[dict[str, Any]] | dict[str, Any]:
    """
    Return core fields for tasks by IDs.

    - Input: task_ids (list[str])
    - Output per task: { id, name, status, type, project, created, last_update, tags, comment, user, parent }

    When to use:
    - You need lightweight task info. For full profiles, use get_tasks_full_info.

    See also docs guides: tools → get_tasks_core_info; categories → tasks_bulk.
    """
    try:
        return svc_tasks_core_info(task_ids)
    except Exception as e:
        return {"error": f"Failed to get tasks core info: {e!s}"}

@mcp.tool()
async def get_tasks_full_info(task_ids: list[str]) -> list[dict[str, Any]] | dict[str, Any]:
    """
    Return full task profiles by IDs (core + parameters, metrics, artifacts, models).

    - Input: task_ids (list[str])
    - Output per task: { core fields + parameters, metrics, artifacts, models }

    When to use:
    - You need all task details at once for inspection or comparison.

    See also docs guides: tools → get_tasks_full_info; categories → tasks_bulk.
    """
    try:
        return svc_tasks_full_info(task_ids)
    except Exception as e:
        return {"error": f"Failed to get tasks full info: {e!s}"}

@mcp.tool()
async def get_tasks_parameters(task_ids: list[str]) -> list[dict[str, Any]] | dict[str, Any]:
    """
    Return parameters/configuration for tasks.

    - Input: task_ids (list[str])
    - Output per task: nested parameters dict

    When to use:
    - You only need parameters; for all details, call get_tasks_full_info.

    See also docs guides: tools → get_tasks_parameters; categories → tasks_bulk.
    """
    try:
        tasks = Task.get_tasks(task_ids=task_ids)
        return [extract_task_parameters(t) for t in tasks or []]
    except Exception as e:
        return {"error": f"Failed to get tasks parameters: {e!s}"}

@mcp.tool()
async def get_tasks_metrics(task_ids: list[str]) -> list[dict[str, Any]] | dict[str, Any]:
    """
    Return reported scalars/metrics for tasks with basic stats.

    - Input: task_ids (list[str])
    - Output per task: { metric: { variant: { last_value, min_value, max_value, iterations }}}

    When to use:
    - You only need metrics; for all details, call get_tasks_full_info.

    See also docs guides: tools → get_tasks_metrics; categories → tasks_bulk.
    """
    try:
        tasks = Task.get_tasks(task_ids=task_ids)
        return [extract_task_metrics(t) for t in tasks or []]
    except Exception as e:
        return {"error": f"Failed to get tasks metrics: {e!s}"}

@mcp.tool()
async def get_tasks_artifacts(task_ids: list[str]) -> list[dict[str, Any]] | dict[str, Any]:
    """
    Return artifacts/outputs for tasks.

    - Input: task_ids (list[str])
    - Output per task: { key: { type, mode, uri, content_type, timestamp } }

    When to use:
    - You only need artifact info; for all details, call get_tasks_full_info.

    See also docs guides: tools → get_tasks_artifacts; categories → tasks_bulk.
    """
    try:
        tasks = Task.get_tasks(task_ids=task_ids)
        return [extract_task_artifacts(t) for t in tasks or []]
    except Exception as e:
        return {"error": f"Failed to get tasks artifacts: {e!s}"}

@mcp.tool()
async def get_tasks_models(task_ids: list[str]) -> list[dict[str, Any]] | dict[str, Any]:
    """
    Return task models metadata (input/output lists).

    - Input: task_ids (list[str])
    - Output per task: { input: [model], output: [model] }, model: { id, name, url, framework, uri }

    When to use:
    - You only need model info; for all details, call get_tasks_full_info.

    See also docs guides: tools → get_tasks_models; categories → tasks_bulk.
    """
    try:
        tasks = Task.get_tasks(task_ids=task_ids)
        return [extract_task_models(t) for t in tasks or []]
    except Exception as e:
        return {"error": f"Failed to get tasks models: {e!s}"}

@mcp.tool()
async def get_tasks_core_info_by_project(project_name: str) -> dict[str, Any]:
    """
    Get comprehensive statistics and task details for a ClearML project.
    
    Args:
        project_name (str): The exact name of the ClearML project to analyze
        
    Returns:
        dict: A dictionary containing:
            - tasks_details: List of individual task information (id, name, status, type, etc.)
            - statistics: Aggregated counters for:
                * tasks_per_status: Count of tasks by status (completed, running, failed, etc.)
                * tasks_per_type: Count of tasks by type (training, inference, etc.) 
                * tasks_per_user: Count of tasks by user who created them
                * tasks_per_tags: Count of tasks by tags (grouped for pipe: tags)
                * tasks_per_day: Count of tasks by creation date (DD.MM.YYYY format)
                * total_tasks: Total number of tasks in the project
            
    Returns error dict if project not found or no tasks exist.

    When to use:
    - You need project stats + core task list in a single call.

    See also docs guides: tools → get_tasks_core_info_by_project; categories → tasks_by_project.
    """
    # Delegate to service layer (preserves original error text and schema)
    try:
        return svc_tasks_core_by_project(project_name)
    except Exception as e:
        return {"error": f"Failed to get tasks core info by project: {e!s}"}

@mcp.tool()
async def get_tasks_full_info_by_project(project_name: str) -> dict[str, Any]:
    """
    Return both aggregated statistics and full task details for a ClearML project.

    Each task entry includes core metadata plus parameters, metrics, artifacts, and models.

    When to use:
    - You need stats + full per-task profiles for the whole project.

    See also docs guides: tools → get_tasks_full_info_by_project; categories → tasks_by_project.
    """
    try:
        return svc_tasks_full_by_project(project_name)
    except Exception as e:
        return {"error": f"Failed to get full tasks info for project: {e!s}"}

@mcp.tool()
async def find_tasks_core_info_by_pattern(
    task_name_pattern: str | None = None,
    status: str | None = None,
    tags: list[str] | None = None) -> list[str] | dict[str, Any]:
    """
    Search tasks by name/status/tags and return only task IDs.

    - Input: task_name_pattern (str|None), status (str|None), tags (list[str]|None)
    - Output: list[str] (task IDs) or {"error": str}

    When to use:
    - You need IDs to fetch details later (e.g., with get_tasks_full_info).

    See also docs guides: tools → find_tasks_core_info_by_pattern; categories → tasks_search.
    """
    try:
        return svc_find_tasks_ids_by_pattern(task_name_pattern, status, tags)
    except Exception as e:
        return {"error": f"Failed to find tasks by pattern: {e!s}"}

@mcp.tool()
async def find_tasks_full_info_by_pattern(
    task_name_pattern: str | None = None,
    status: str | None = None,
    tags: list[str] | None = None,) -> list[dict[str, Any]] | dict[str, Any]:
    """
    Search tasks by name/status/tags and return full profiles.

    - Input: task_name_pattern (str|None), status (str|None), tags (list[str]|None)
    - Output: list of full task dicts (core + parameters, metrics, artifacts, models)

    When to use:
    - You want detailed matches in one call. For IDs only, use find_tasks_core_info_by_pattern.

    See also docs guides: tools → find_tasks_full_info_by_pattern; categories → tasks_search.
    """
    try:
        return svc_find_tasks_full_by_pattern(task_name_pattern, status, tags)
    except Exception as e:
        return {"error": f"Failed to find full tasks by pattern: {e!s}"}

@mcp.tool()
async def find_models_by_pattern(pattern: str) -> list[dict[str, Any]] | dict[str, Any]:
    """
    Return model info filtered by name substring (includes url/uri when available).

    - Input: pattern (str)
    - Output per model: { id, name, project, framework, created, tags, task_id, url, uri }

    When to use:
    - You need to search models by a name fragment and also get download locations/URIs when present.

    See also docs guides: tools → find_models_by_pattern; categories → models_search.
    """
    try:
        models = Model.query_models(project_name=None)
        name_lower = pattern.lower() if pattern else None
        filtered = svc_filter_models(models, name_lower, None, None)
        return [svc_model_dict(m) for m in filtered]
    except Exception as e:
        return {"error": f"Failed to find models by pattern: {e!s}"}

@mcp.tool()
async def find_models_info(models_ids: list[str]) -> list[dict[str, Any]] | dict[str, Any]:
    """
    Return model info for specified IDs (core fields plus url/uri when available).

    - Input: models_ids (list[str])
    - Output per model: { id, name, project, framework, created, tags, task_id, url, uri }

    When to use:
    - You have model IDs and need complete info including download locations/URIs.

    See also docs guides: tools → find_models_info; categories → models_by_id.
    """
    try:
        return svc_models_info(models_ids)
    except Exception as e:
        return {"error": f"Failed to get models info: {e!s}"}

@mcp.tool()
async def find_datasets_by_project(project_name: str, recursive_project_search: bool = False) -> list[dict[str, Any]] | dict[str, Any]:
    """
    Find datasets by project.

    - Input: project_name (exact), recursive_project_search (bool; include subprojects)
    - Output: list of dataset dicts as returned by ClearML Dataset.list_datasets, or {"error": str}

    When to use:
    - You know the project and want all datasets in it.

    See also docs guides: tools → find_datasets_by_project; categories → datasets.
    """
    try:
        return svc_find_datasets_by_project(project_name, recursive_project_search)
    except Exception as e:
        return {"error": f"Failed to find datasets by project: {e!s}"}

@mcp.tool()
async def find_datasets_by_pattern(pattern: str) -> list[dict[str, Any]] | dict[str, Any]:
    """
    Find datasets by partial name pattern.

    - Input: pattern (substring; server-side partial match when supported)
    - Output: list of dataset dicts as returned by ClearML Dataset.list_datasets, or {"error": str}

    When to use:
    - You need to discover datasets by a name fragment across projects.

    See also docs guides: tools → find_datasets_by_pattern; categories → datasets.
    """
    try:
        return svc_find_datasets_by_pattern(pattern)
    except Exception as e:
        return {"error": f"Failed to find datasets by pattern: {e!s}"}

@mcp.tool()
async def get_datasets_full_info(dataset_ids: list[str]) -> list[dict[str, Any]] | dict[str, Any]:
    """
    Return full info for datasets (sizes, uploader, metadata parsed).

    - Input: dataset_ids (list[str])
    - Output per dataset: { id, project, name, created, tags, version, upload_username,
      size_mb, size_compressed_mb, metadata: dict, meta_status: {is_no_meta, no_meta_reason}, is_latest }
    - Metadata formats: CSV.gz → CSV → JSON (first object)

    When to use:
    - You need dataset details for reporting, selection, or further analysis.

    See also docs guides: tools → get_datasets_full_info; categories → datasets.
    """
    try:
        return svc_datasets_full_info(dataset_ids)
    except Exception as e:
        return {"error": f"Failed to get datasets full info: {e!s}"}

@mcp.tool()
async def compare_tasks(task_ids: list[str]) -> dict[str, Any]:
    """
    Compare multiple tasks by metrics and parameters.

    - Input: task_ids (list[str])
    - Output: {
        summary: { projects, statuses, types, users, latest_updates, common_metrics, unique_metrics, artifacts_count, artifact_keys, models_count, model_frameworks },
        comparisons: { metrics: aligned table, parameters_diff: differing parameters },
        tasks: full task profiles (same shape as get_tasks_full_info)
      }

    When to use:
    - You need a consolidated comparison output for analysis/visualization.

    See also docs guides: tools → compare_tasks.
    """
    try:
        return svc_compare_tasks(task_ids)
    except Exception as e:
        return {"error": f"Failed to compare tasks: {e!s}"}


def main() -> None:
    """Entry point for uvx clearml-mcp."""
    ensure_clearml_connection_ready()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
