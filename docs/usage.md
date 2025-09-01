# Usage

This project provides an MCP stdio server exposing ClearML operations as tools. You typically don’t import it in code; you run the server and connect with an MCP‑compatible client (Cursor, Claude, Continue, Cody, etc.).

## Run the server

Install from PyPI and run:

```bash
pip install mcp_clearml
mcp-clearml
```

Or run without installation using uvx:

```bash
uvx mcp-clearml
```

The command validates your ClearML credentials (from `~/.clearml/clearml.conf`) and starts an MCP stdio server.

## Client configuration snippets

### Claude Desktop (macOS/Windows)

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

### Continue

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

## Example tool flows

- List projects → `list_of_all_projects`
- Project stats → `get_project_stats { project_name: "X" }`
- Find tasks then fetch details →
  1) `find_tasks_core_info_by_pattern { task_name_pattern: "resnet" }`
  2) `get_tasks_full_info { task_ids: ["..."] }`
- Compare tasks → `compare_tasks { task_ids: ["id1", "id2"] }`
- Datasets in project → `find_datasets_by_project { project_name: "X", recursive_project_search: true }`
