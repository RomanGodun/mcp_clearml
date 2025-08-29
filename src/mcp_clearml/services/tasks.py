from __future__ import annotations

from typing import Any

from clearml import Task
from ..utils import compute_project_statistics


def _normalize_enum_like(value: Any) -> str | None:
    if value is None:
        return None
    if hasattr(value, "value"):
        try:
            return str(value.value)
        except Exception:
            return str(value)
    return str(value)


def extract_task_core_info(task: Any) -> dict[str, Any]:
    status = _normalize_enum_like(getattr(task, "status", None))
    task_type = _normalize_enum_like(getattr(task, "task_type", None))

    data = getattr(task, "data", None)
    created = getattr(data, "created", None) if data is not None else None
    last_update = getattr(data, "last_update", None) if data is not None else None
    user = getattr(data, "user", None) if data is not None else None
    parent = getattr(data, "parent", None) if data is not None else None
    tags = list(getattr(data, "tags", []) or []) if data is not None else []

    return {
        "id": getattr(task, "id", None),
        "name": getattr(task, "name", None),
        "status": status,
        "type": task_type,
        "project": task.get_project_name() if hasattr(task, "get_project_name") else None,
        "created": str(created) if created else None,
        "last_update": str(last_update) if last_update else None,
        "tags": tags,
        "comment": getattr(task, "comment", None),
        "user": user,
        "parent": parent,
    }


def extract_task_artifacts(task: Any) -> dict[str, dict[str, Any]]:
    artifacts: dict[str, dict[str, Any]] = {}
    try:
        for key, artifact in (getattr(task, "artifacts", {}) or {}).items():
            artifacts[key] = {
                "type": getattr(artifact, "type", None),
                "mode": getattr(artifact, "mode", None),
                "uri": getattr(artifact, "uri", None),
                "content_type": getattr(artifact, "content_type", None),
                "timestamp": str(getattr(artifact, "timestamp", None)) if hasattr(artifact, "timestamp") else None,
            }
    except Exception:
        pass
    return artifacts


def extract_task_models(task: Any) -> dict[str, list[dict[str, Any]]]:
    models_info: dict[str, list[dict[str, Any]]] = {"input": [], "output": []}
    try:
        models = getattr(task, "models", {}) or {}
        if models.get("input"):
            for model in models["input"]:
                models_info["input"].append(
                    {
                        "id": getattr(model, "id", None),
                        "name": getattr(model, "name", None),
                        "url": getattr(model, "url", None),
                        "framework": getattr(model, "framework", None),
                        "uri": getattr(model, "uri", None),
                    }
                )
        if models.get("output"):
            for model in models["output"]:
                models_info["output"].append(
                    {
                        "id": getattr(model, "id", None),
                        "name": getattr(model, "name", None),
                        "url": getattr(model, "url", None),
                        "framework": getattr(model, "framework", None),
                        "uri": getattr(model, "uri", None),
                    }
                )
    except Exception:
        pass
    return models_info


def extract_task_metrics(task: Any) -> dict[str, dict[str, dict[str, Any]]]:
    metrics: dict[str, dict[str, dict[str, Any]]] = {}
    try:
        scalars = task.get_reported_scalars()
        for metric, variants in scalars.items():
            metrics[metric] = {}
            for variant, data in (variants or {}).items():
                if data and "y" in data:
                    ys = data["y"] or []
                    metrics[metric][variant] = {
                        "last_value": ys[-1] if ys else None,
                        "min_value": min(ys) if ys else None,
                        "max_value": max(ys) if ys else None,
                        "iterations": len(ys),
                    }
    except Exception:
        pass
    return metrics


def extract_task_parameters(task: Any) -> dict[str, Any]:
    try:
        return task.get_parameters_as_dict()
    except Exception:
        return {}


def get_core_info(task_ids: list[str]) -> list[dict[str, Any]]:
    tasks = Task.get_tasks(task_ids=task_ids)
    return [extract_task_core_info(t) for t in tasks or []]


def get_full_info(task_ids: list[str]) -> list[dict[str, Any]]:
    tasks = Task.get_tasks(task_ids=task_ids)
    results: list[dict[str, Any]] = []
    for t in tasks or []:
        core_info = extract_task_core_info(t)
        results.append(
            {
                **core_info,
                "parameters": extract_task_parameters(t),
                "metrics": extract_task_metrics(t),
                "artifacts": extract_task_artifacts(t),
                "models": extract_task_models(t),
            }
        )
    return results


def get_core_info_by_project(project_name: str) -> dict[str, Any]:
    tasks_in_project = Task.get_tasks(project_name=project_name)
    if not tasks_in_project:
        return {"error": f"No tasks found, possibly due to incorrect project name"}
    task_details = [extract_task_core_info(t) for t in tasks_in_project]
    return {"statistics": compute_project_statistics(tasks_in_project), "tasks_details": task_details}


def get_full_info_by_project(project_name: str) -> dict[str, Any]:
    tasks_in_project = Task.get_tasks(project_name=project_name)
    if not tasks_in_project:
        return {"error": f"No tasks found, possibly due to incorrect project name"}
    details: list[dict[str, Any]] = []
    for t in tasks_in_project:
        core_info = extract_task_core_info(t)
        details.append(
            {
                **core_info,
                "parameters": extract_task_parameters(t),
                "metrics": extract_task_metrics(t),
                "artifacts": extract_task_artifacts(t),
                "models": extract_task_models(t),
            }
        )
    return {"statistics": compute_project_statistics(tasks_in_project), "tasks_details": details}


def find_tasks_ids_by_pattern(task_name_pattern: str | None, status: str | None, tags: list[str] | None) -> list[str] | dict[str, Any]:
    try:
        tf: dict[str, Any] | None = None
        if status or task_name_pattern:
            tf = {}
            if status:
                tf["status"] = [status]
            if task_name_pattern:
                tf["search_text"] = task_name_pattern

        arf = [
            "id",
            "name",
            "status",
            "type",
            "project",
            "user",
            "created",
            "last_update",
            "tags",
            "comment",
            "parent",
        ]

        results = Task.query_tasks(
            project_name=None,
            task_name=None,
            tags=tags,
            additional_return_fields=arf,
            task_filter=tf,
        )

        if results and isinstance(results, list) and isinstance(results[0], dict):
            return [item.get("id") for item in results if isinstance(item, dict) and item.get("id")]
        return list(results or [])
    except Exception as e:
        return {"error": f"Failed to find tasks by pattern: {e!s}"}


def find_tasks_full_by_pattern(task_name_pattern: str | None, status: str | None, tags: list[str] | None) -> list[dict[str, Any]] | dict[str, Any]:
    try:
        tf: dict[str, Any] | None = None
        if status or task_name_pattern:
            tf = {}
            if status:
                tf["status"] = [status]
            if task_name_pattern:
                tf["search_text"] = task_name_pattern

        task_ids = Task.query_tasks(
            project_name=None,
            task_name=None,
            tags=tags,
            additional_return_fields=["id"],
            task_filter=tf,
        )

        details: list[dict[str, Any]] = []
        for task_id in task_ids or []:
            try:
                t = Task.get_task(task_id=task_id)
                core_info = extract_task_core_info(t)
                details.append(
                    {
                        **core_info,
                        "parameters": extract_task_parameters(t),
                        "metrics": extract_task_metrics(t),
                        "artifacts": extract_task_artifacts(t),
                        "models": extract_task_models(t),
                    }
                )
            except Exception:
                continue
        return details
    except Exception as e:
        return {"error": f"Failed to find full tasks by pattern: {e!s}"}


