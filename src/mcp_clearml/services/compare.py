from __future__ import annotations

from collections import Counter
from typing import Any

from .tasks import get_full_info as svc_tasks_full_info


def compare_tasks(task_ids: list[str]) -> dict[str, Any]:
    """
    Build a cross-task comparison structure for the given task IDs.

    Returns dict with keys: summary, comparisons{metrics, parameters_diff}, tasks(full profiles).
    """
    full_tasks = svc_tasks_full_info(task_ids)

    def _get(d: dict[str, Any], key: str, default: Any) -> Any:
        return d.get(key, default) if isinstance(d, dict) else default

    statuses: Counter[str] = Counter()
    types: Counter[str] = Counter()
    users: Counter[str] = Counter()
    projects: Counter[str] = Counter()
    latest_updates: dict[str, str | None] = {}

    all_metric_names: set[str] = set()
    per_task_metrics: dict[str, dict[str, dict[str, Any]]] = {}

    def _flatten(prefix: str, obj: Any, out: dict[str, Any]) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                key_path = f"{prefix}/{k}" if prefix else str(k)
                _flatten(key_path, v, out)
        else:
            out[prefix] = obj

    flattened_params_by_task: dict[str, dict[str, Any]] = {}
    artifacts_count: dict[str, int] = {}
    artifact_keys: dict[str, list[str]] = {}
    models_count: dict[str, dict[str, int]] = {}
    model_frameworks: dict[str, list[str]] = {}

    for task in full_tasks:
        task_id = _get(task, "id", None)
        if not task_id:
            continue
        statuses[_get(task, "status", None) or "unknown"] += 1
        types[_get(task, "type", None) or "unknown"] += 1
        users[_get(task, "user", None) or "unknown"] += 1
        projects[_get(task, "project", None) or "unknown"] += 1
        latest_updates[task_id] = _get(task, "last_update", None)

        metrics = _get(task, "metrics", {}) or {}
        per_task_metrics[task_id] = metrics
        all_metric_names.update(metrics.keys())

        params = _get(task, "parameters", {}) or {}
        flat: dict[str, Any] = {}
        _flatten("", params, flat)
        flattened_params_by_task[task_id] = flat

        artifacts = _get(task, "artifacts", {}) or {}
        artifacts_count[task_id] = len(artifacts)
        artifact_keys[task_id] = list(artifacts.keys()) if isinstance(artifacts, dict) else []

        models = _get(task, "models", {}) or {}
        input_models = models.get("input", []) if isinstance(models, dict) else []
        output_models = models.get("output", []) if isinstance(models, dict) else []
        models_count[task_id] = {"input": len(input_models or []), "output": len(output_models or [])}
        mfs: list[str] = []
        for coll in (input_models or []) + (output_models or []):
            fw = getattr(coll, "framework", None) if not isinstance(coll, dict) else coll.get("framework")
            if fw:
                mfs.append(str(fw))
        model_frameworks[task_id] = mfs

    common_metrics = [
        m for m in all_metric_names if all(m in per_task_metrics.get(tid, {}) for tid in per_task_metrics.keys())
    ]
    unique_metrics: dict[str, list[str]] = {}
    for tid, m in per_task_metrics.items():
        unique_metrics[tid] = [
            k for k in m.keys() if any(k not in per_task_metrics.get(other, {}) for other in per_task_metrics.keys() if other != tid)
        ]

    aligned_metrics: dict[str, dict[str, dict[str, Any]]] = {}
    for metric in all_metric_names:
        aligned_metrics[metric] = {}
        variants_union: set[str] = set()
        for tid, m in per_task_metrics.items():
            if metric in m:
                variants_union.update((m[metric] or {}).keys())
        for variant in variants_union:
            aligned_metrics[metric][variant] = {}
            for tid, m in per_task_metrics.items():
                stats = _get(_get(m, metric, {}), variant, None)
                aligned_metrics[metric][variant][tid] = stats

    all_param_keys: set[str] = set()
    for flat in flattened_params_by_task.values():
        all_param_keys.update(flat.keys())

    diff_parameters: dict[str, dict[str, Any]] = {}
    for key in sorted(all_param_keys):
        values: dict[str, Any] = {tid: flattened_params_by_task.get(tid, {}).get(key) for tid in flattened_params_by_task.keys()}
        distinct = {v for v in values.values() if v is not None}
        if len(distinct) > 1:
            diff_parameters[key] = values

    summary = {
        "num_tasks": len(per_task_metrics.keys()),
        "projects": dict(projects),
        "statuses": dict(statuses),
        "types": dict(types),
        "users": dict(users),
        "latest_updates": latest_updates,
        "common_metrics": sorted(common_metrics),
        "unique_metrics": unique_metrics,
        "artifacts_count": artifacts_count,
        "artifact_keys": artifact_keys,
        "models_count": models_count,
        "model_frameworks": model_frameworks,
    }

    return {
        "summary": summary,
        "comparisons": {
            "metrics": aligned_metrics,
            "parameters_diff": diff_parameters,
        },
        "tasks": full_tasks,
    }


