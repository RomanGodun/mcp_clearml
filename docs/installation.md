# Installation

## Prerequisites

- Python >= 3.12
- ClearML credentials in `~/.clearml/clearml.conf`:

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

## Install from PyPI

```sh
pip install mcp_clearml
```

## Run without installing (uvx)

```sh
uvx mcp-clearml
```

## From source

Get the code from the [GitHub repo](https://github.com/RomanGodun/mcp_clearml):

```sh
git clone https://github.com/RomanGodun/mcp_clearml
cd mcp_clearml
uv sync
uv run mcp-clearml
```
