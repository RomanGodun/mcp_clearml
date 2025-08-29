from __future__ import annotations

from typing import Any

from clearml import Task

from ..utils import compute_project_statistics


def list_projects() -> list[dict[str, Any]]:
    """Return a list of available ClearML projects (id, name)."""
    projects = Task.get_projects()
    return [
        {
            "id": proj.id if hasattr(proj, "id") else None,
            "name": proj.name,
        }
        for proj in projects
    ]


def find_projects_by_pattern(pattern: str) -> list[dict[str, Any]]:
    """Find projects whose names contain the given pattern (case-insensitive)."""
    all_projects = Task.get_projects()
    pattern_lower = pattern.lower()
    matching: list[dict[str, Any]] = []
    for proj in all_projects:
        if pattern_lower in proj.name.lower():
            matching.append({"id": getattr(proj, "id", None), "name": proj.name})
    return matching


def get_project_statistics(project_name: str) -> dict[str, Any]:
    """Compute aggregated statistics for a project using existing helper."""
    tasks_in_project = Task.get_tasks(project_name=project_name)
    if not tasks_in_project:
        return {"error": "No tasks found, possibly due to incorrect project name"}
    return compute_project_statistics(tasks_in_project)


