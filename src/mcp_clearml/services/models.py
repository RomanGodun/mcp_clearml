from __future__ import annotations

from typing import Any

from clearml import Model


def filter_models(models: list[Any], name_lower: str | None, framework: str | None, tags: list[str] | None) -> list[Any]:
    filtered: list[Any] = []
    for m in models or []:
        try:
            if framework and getattr(m, "framework", None) != framework:
                continue
            if tags:
                m_tags = list(getattr(m, "tags", []) or [])
                if not all(tag in m_tags for tag in tags):
                    continue
            if name_lower and not (getattr(m, "name", None) and name_lower in m.name.lower()):
                continue
            filtered.append(m)
        except Exception:
            continue
    return filtered


def to_model_dict(m: Any) -> dict[str, Any]:
    """Return a single, unified model dict (core fields plus url/uri when available)."""
    return {
        "id": getattr(m, "id", None),
        "name": getattr(m, "name", None),
        "project": getattr(m, "project", None),
        "framework": getattr(m, "framework", None),
        "created": str(getattr(m, "created", None)),
        "tags": list(getattr(m, "tags", []) or []),
        "task_id": getattr(m, "task", None),
        "url": getattr(m, "url", None),
        "uri": getattr(m, "uri", None),
    }


def get_models_by_ids(models_ids: list[str]) -> list[Any]:
    if not models_ids:
        return []
    result: list[Any] = []
    for mid in models_ids:
        try:
            model = Model(model_id=mid)
            result.append(model)
        except Exception:
            # Skip models that cannot be loaded
            continue
    return result

def get_models_info(models_ids: list[str]) -> list[dict[str, Any]]:
    """Return model info for given IDs (core fields plus url/uri when available)."""
    models = get_models_by_ids(models_ids)
    return [to_model_dict(m) for m in models]


