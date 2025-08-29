from __future__ import annotations

from typing import Any
from pathlib import Path
import json
import gzip
import csv

from clearml import Task, StorageManager
from clearml.backend_api import Session


def _safe_first_dict_row_from_csv(file_path: Path, gzipped: bool) -> dict[str, Any] | None:
    try:
        if gzipped:
            with gzip.open(file_path, mode="rt", newline="") as gz:
                reader = csv.DictReader(gz)
                row = next(reader, None)
        else:
            with file_path.open("rt", newline="") as f:
                reader = csv.DictReader(f)
                row = next(reader, None)
        if isinstance(row, dict):
            return {k: (v if v != "" else None) for k, v in row.items()}
    except Exception:
        return None
    return None


def _safe_first_dict_from_json(file_path: Path) -> dict[str, Any] | None:
    try:
        with file_path.open("rt") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
        if isinstance(data, list) and data and isinstance(data[0], dict):
            return data[0]
    except Exception:
        return None
    return None


def _parse_metadata_from_uri(meta_uri: str) -> tuple[dict[str, Any], bool, str | None]:
    """
    Try to download and parse metadata from URI.
    Returns: (metadata_dict, is_no_meta, no_meta_reason)
    """
    try:
        local_file = StorageManager.download_file(remote_url=meta_uri, skip_zero_size_check=False)
        if not local_file:
            return {}, True, "metadata file not found at resolved uri"

        p = Path(local_file)
        # Try gzip CSV
        meta = _safe_first_dict_row_from_csv(p, gzipped=True)
        if meta is not None:
            return meta, False, None
        # Try plain CSV
        meta = _safe_first_dict_row_from_csv(p, gzipped=False)
        if meta is not None:
            return meta, False, None
        # Try JSON / NDJSON (first JSON object)
        meta = _safe_first_dict_from_json(p)
        if meta is not None:
            return meta, False, None

        return {}, True, "unsupported or empty metadata format"
    except Exception as e:
        return {}, True, f"failed to download/parse metadata: {e}"


def _extract_project_name(task_obj: Task | None, project_field: Any) -> str | None:
    if isinstance(project_field, dict):
        return project_field.get("name") or project_field.get("id")
    if project_field:
        return project_field
    try:
        return task_obj.get_project_name() if task_obj else None
    except Exception:
        return None


def _get_task_details_for_dataset_id(session: Session, ds_id: str) -> dict[str, Any] | None:
    req = session.send_request("tasks", "get_by_id", data={"task": [ds_id]})
    payload = req.json() if req is not None else None
    ds_task = (payload or {}).get("data", {}).get("task") if isinstance(payload, dict) else None
    if isinstance(ds_task, dict):
        return ds_task
    # fallback to Task
    try:
        t = Task.get_task(task_id=ds_id)
        return {
            "id": getattr(t, "id", ds_id),
            "name": getattr(t, "name", None),
            "user": getattr(t, "user", None),
            "created": getattr(getattr(t, "data", None), "created", None),
            "tags": getattr(getattr(t, "data", None), "tags", None),
            "runtime": {},
            "execution": {"artifacts": []},
            "project": t.get_project_name() if t else None,
        }
    except Exception:
        return None


def get_datasets_full_info(dataset_ids: list[str]) -> list[dict[str, Any]]:
    session = Session()
    results: list[dict[str, Any]] = []

    for ds_id in dataset_ids or []:
        ds_task = _get_task_details_for_dataset_id(session, ds_id)
        if not isinstance(ds_task, dict):
            results.append({"id": ds_id, "error": "Failed to load dataset task details"})
            continue

        ds_id_val = ds_task.get("id", ds_id)
        name = ds_task.get("name")
        created = ds_task.get("created")
        tags_val = ds_task.get("tags") or []
        uploader = ds_task.get("user")

        # Project
        t_obj = None
        try:
            t_obj = Task.get_task(task_id=ds_id_val)
        except Exception:
            t_obj = None
        project_name = _extract_project_name(t_obj, ds_task.get("project"))

        # Sizes
        runtime = ds_task.get("runtime", {}) or {}
        size_bytes = runtime.get("ds_total_size")
        size_compressed_bytes = runtime.get("ds_total_size_compressed")
        size_mb = (size_bytes / 1024.0 / 1024.0) if isinstance(size_bytes, (int, float)) else None
        size_compressed_mb = (size_compressed_bytes / 1024.0 / 1024.0) if isinstance(size_compressed_bytes, (int, float)) else None

        # Metadata artifact
        meta_uri = None
        execution = ds_task.get("execution", {}) or {}
        for art in (execution.get("artifacts") or []):
            if isinstance(art, dict) and art.get("key") == "metadata":
                meta_uri = art.get("uri")
                break

        metadata: dict[str, Any] = {}
        is_no_meta = True
        no_meta_reason = None
        if meta_uri:
            metadata, is_no_meta, no_meta_reason = _parse_metadata_from_uri(meta_uri)
        else:
            no_meta_reason = "metadata artifact not present"

        results.append({
            "id": ds_id_val,
            "project": project_name,
            "name": name,
            "created": created,
            "tags": tags_val or [],
            "version": None,
            "upload_username": uploader,
            "size_mb": size_mb,
            "size_compressed_mb": size_compressed_mb,
            "metadata": metadata,
            "meta_status": {
                "is_no_meta": is_no_meta,
                "no_meta_reason": no_meta_reason,
            },
        })

    # Mark latest per name by created
    latest_created: dict[str, Any] = {}
    for d in results:
        n = d.get("name")
        c = d.get("created")
        if n is None or c is None:
            continue
        prev = latest_created.get(n)
        if prev is None or str(c) > str(prev):
            latest_created[n] = c
    for d in results:
        n = d.get("name")
        c = d.get("created")
        d["is_latest"] = bool(n and c and latest_created.get(n) == c)

    return results


def find_datasets_by_project(project_name: str, recursive_project_search: bool = False) -> list[dict[str, Any]] | dict[str, Any]:
    from clearml import Dataset
    try:
        results = Dataset.list_datasets(
            dataset_project=project_name,
            recursive_project_search=recursive_project_search,
        )
        items = [item for item in (results or []) if isinstance(item, dict)]
        if not items:
            return {"error": f"No datasets found for project: {project_name}"}
        return items
    except Exception as e:
        return {"error": f"Failed to find datasets by project: {e!s}"}


def find_datasets_by_pattern(pattern: str) -> list[dict[str, Any]] | dict[str, Any]:
    from clearml import Dataset
    try:
        results = Dataset.list_datasets(dataset_name=pattern, partial_name=True)
        items = [item for item in (results or []) if isinstance(item, dict)]
        if not items:
            return {"error": f"No datasets found for pattern: {pattern}"}
        return items
    except Exception as e:
        return {"error": f"Failed to find datasets by pattern: {e!s}"}


