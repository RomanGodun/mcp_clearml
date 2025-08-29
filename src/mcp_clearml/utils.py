from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any
# Intentionally minimal: shared-only utilities remain here


def _date_key(created: Any) -> str | None:
    if not created:
        return None
    if isinstance(created, str):
        try:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
        except Exception:
            return None
    else:
        dt = created
    try:
        return dt.strftime("%d.%m.%Y")
    except Exception:
        return None


def compute_project_statistics(tasks: list[Any]) -> dict[str, Any]:
    status_counter: Counter[str] = Counter()
    type_counter: Counter[str] = Counter()
    user_counter: Counter[str] = Counter()
    tags_counter: Counter[str] = Counter()
    date_counter: Counter[str] = Counter()

    for task in tasks:
        data = getattr(task, "data", None)
        status = str(getattr(task, "status", "")) or None
        task_type = str(getattr(task, "task_type", "")) or None
        user = getattr(data, "user", None) if data is not None else None
        tags = list(getattr(data, "tags", []) or []) if data is not None else []
        created = getattr(data, "created", None) if data is not None else None

        if status:
            status_counter[status] += 1
        if task_type:
            type_counter[task_type] += 1
        if user:
            user_counter[user] += 1

        for tag in tags:
            if isinstance(tag, str) and tag.startswith("pipe: "):
                tags_counter["pipe: ..."] += 1
            else:
                tags_counter[tag] += 1

        key = _date_key(created)
        if key:
            date_counter[key] += 1

    return {
        "total_tasks": len(tasks),
        "tasks_per_status": dict(status_counter),
        "tasks_per_type": dict(type_counter),
        "tasks_per_user": dict(user_counter),
        "tasks_per_tags": dict(tags_counter),
        "tasks_per_day": dict(date_counter),
    }




