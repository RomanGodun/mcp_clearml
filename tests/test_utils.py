from __future__ import annotations

from types import SimpleNamespace
from datetime import datetime, timezone

from mcp_clearml.utils import compute_project_statistics, _date_key  # type: ignore


def test_date_key_handles_iso_and_datetime():
    assert _date_key("2024-01-02T03:04:05Z") == "02.01.2024"
    assert _date_key(datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)) == "02.01.2024"
    assert _date_key(None) is None
    assert _date_key("not-a-date") is None


def _task(status: str | None, task_type: str | None, user: str | None, tags: list[str] | None, created: str | None):
    data = SimpleNamespace(user=user, tags=tags or [], created=created)
    return SimpleNamespace(status=status, task_type=task_type, data=data)


def test_compute_project_statistics_counts_all():
    tasks = [
        _task("completed", "training", "alice", ["a", "pipe: tag"], "2024-01-02T00:00:00Z"),
        _task("failed", "inference", "bob", ["b"], "2024-01-02T12:00:00Z"),
        _task("completed", "training", "alice", ["a"], "2024-01-03T00:00:00Z"),
    ]
    stats = compute_project_statistics(tasks)

    assert stats["total_tasks"] == 3
    assert stats["tasks_per_status"]["completed"] == 2
    assert stats["tasks_per_type"]["training"] == 2
    assert stats["tasks_per_user"]["alice"] == 2
    # pipe: ... bucket
    assert stats["tasks_per_tags"]["pipe: ..."] == 1
    # date aggregation
    assert stats["tasks_per_day"]["02.01.2024"] == 2


