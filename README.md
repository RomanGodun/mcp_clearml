
<p align="center">
  <img src="docs/photo_2025-09-01_14-40-55.jpg" alt="mcp_clearml cover" width="550" />
</p>

![PyPI version](https://img.shields.io/pypi/v/mcp_clearml.svg)
[![Documentation Status](https://readthedocs.org/projects/mcp-clearml/badge/?version=latest)](https://mcp-clearml.readthedocs.io/en/latest/?version=latest)

MCP server for ClearML: browse projects, search and compare tasks, list datasets and models — all via Model Context Protocol.

- PyPI: https://pypi.org/project/mcp_clearml/
- License: MIT
- Docs: https://mcp-clearml.readthedocs.io

---

## What you get

This server exposes a curated set of ClearML operations as MCP tools:

- Projects
  - `list_of_all_projects`: list all projects (id, name)
  - `find_project_by_pattern`: find by name substring (case-insensitive)
  - `get_project_stats`: aggregated counters for a project (statuses, users, tags, days)
- Tasks (bulk/filters)
  - `get_tasks_core_info`: core fields by task ids
  - `get_tasks_full_info`: core + parameters/metrics/artifacts/models by task ids
  - `find_tasks_core_info_by_pattern`: IDs by name/status/tags
  - `find_tasks_full_info_by_pattern`: full profiles by name/status/tags
  - `get_tasks_core_info_by_project`: stats + core list for a project
  - `get_tasks_full_info_by_project`: stats + full profiles for a project
- Models
  - `find_models_by_pattern`: search models by name fragment (includes url/uri when present)
  - `find_models_info`: info for specific model ids
- Datasets
  - `find_datasets_by_project`: list datasets in a project (optional recursive)
  - `find_datasets_by_pattern`: list datasets by partial name
  - `get_datasets_full_info`: per-dataset sizes, uploader and parsed metadata (csv/csv.gz/json)
- Compare
  - `compare_tasks`: cross-task summary + aligned metrics + parameters diff

See also in-code guides to help LLMs choose the right tool:
- Categories: `mcp_clearml.docs.CATEGORY_GUIDE`
- Per-tool hints: `mcp_clearml.docs.TOOL_GUIDE`

---

## Requirements

- Python >= 3.12
- ClearML account with valid credentials in `~/.clearml/clearml.conf`
- Recommended `uv` to run via `uvx` without installing globally

---

## Quick Start

### Prerequisites
Ensure your `~/.clearml/clearml.conf` contains your credentials:

```ini
[api]
api_server = https://api.clear.ml
web_server = https://app.clear.ml
files_server = https://files.clear.ml

credentials {
    "access_key": "your-access-key",
    "secret_key": "your-secret-key"
}
```
You can obtain keys in ClearML Settings.

### Install / Run

- Install from PyPI:

```bash
pip install mcp_clearml
```

- Run without installation (via uvx):

```bash
uvx mcp-clearml
```

- Local dev:

```bash
uv sync
uv run mcp-clearml
```

---

## Run MCP server (stdio)

The `mcp-clearml` command validates ClearML connectivity and starts an MCP stdio server.

---

## Integrations (MCP clients)

### Claude Desktop

Config file:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "clearml": {
      "command": "uvx",
      "args": ["mcp-clearml"]
    }
  }
}
```

Alternative (if installed via pip):

```json
{
  "mcpServers": {
    "clearml": {
      "command": "python",
      "args": ["-m", "mcp_clearml.mcp"]
    }
  }
}
```

### Cursor

Settings → MCP → Add Server:

```json
{
  "mcp.servers": {
    "clearml": {
      "command": "uvx",
      "args": ["mcp-clearml"]
    }
  }
}
```

You can also add a rule in `.cursorrules` to remind using the `clearml` MCP server for experiment analysis.

### Continue

`~/.continue/config.json`:

```json
{
  "mcpServers": {
    "clearml": {
      "command": "uvx",
      "args": ["mcp-clearml"]
    }
  }
}
```

### Cody

```json
{
  "cody.experimental.mcp": {
    "servers": {
      "clearml": {
        "command": "uvx",
        "args": ["mcp-clearml"]
      }
    }
  }
}
```

### Any MCP‑compatible assistant

```json
{
  "mcpServers": {
    "clearml": {
      "command": "uvx",
      "args": ["mcp-clearml"]
    }
  }
}
```

Verified with: Zed, OpenHands, Roo‑Cline, and others.

---

## Use in Claude Code (or any MCP client)

Add the stdio server with the same command. Then call tools by name (e.g., "find tasks by pattern", "compare_tasks"). Generic MCP UIs will connect over stdio automatically.

---

## Examples

- "List projects" → `list_of_all_projects`
- "Stats for project X" → `get_project_stats { project_name: "X" }`
- "Find tasks by name fragment and get full details" →
  1) `find_tasks_core_info_by_pattern { task_name_pattern: "resnet" }`
  2) `get_tasks_full_info { task_ids: ["..."] }`
- "Compare two tasks" → `compare_tasks { task_ids: ["task_id_1", "task_id_2"] }`
- "Find datasets by project" → `find_datasets_by_project { project_name: "X", recursive_project_search: true }`

---

## Development

Setup & test locally:

```bash
uv sync --extra test
uv run pytest -q
```

Coverage gate is configured at 65% (see `[tool.coverage.*]` in `pyproject.toml`).

Lint/type check:

```bash
uv run ruff check --output-format=github src/ tests/
uv run ty check || true
```

---

## Release (GitHub Actions)

- Tests run on all branches/PRs (`.github/workflows/tests.yml`).
- Tag‑based release (`.github/workflows/release.yml`):
  1) push tag `vX.Y.Z` → runs tests (`verify`)
  2) build wheels/sdist, create GitHub Release with artifacts
  3) optional PyPI publish if `PYPI_API_TOKEN` is set

See `docs/releasing.md` for the exact steps.

---

## Credits

Acknowledgment: thanks to prassanna-ravishankar for the ClearML MCP project that inspired this work.
