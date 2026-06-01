# pretty-docker

Terminal User Interface (TUI) and CLI tool for viewing Docker container information in a clean, formatted way.

Built with [Textual](https://textual.textualize.io/) for the TUI and [Rich](https://rich.readthedocs.io/) for the CLI, using the [Docker SDK](https://docker-py.readthedocs.io/) instead of shelling out to the `docker` CLI.

## Context

Managing Docker containers typically requires typing `docker ps -a` repeatedly, then `docker inspect` to get details. `pretty-docker` wraps these operations into two convenient interfaces:

- **TUI mode**: Interactive terminal app with collapsible panels for each container. Shows state, image, and port mappings at a glance. Expand any container to see full details. Keyboard-driven workflow.
- **CLI mode**: Quick formatted output (table or JSON) for scripting or when you just need a snapshot.

The original version used `subprocess` to call the Docker CLI and had an outdated Textual version with minimal error handling. This refactored version:

- Uses the **Docker SDK** for reliable, typed API access
- Runs on **Textual 8.x** with async workers for non-blocking UI
- Has **proper error handling** with user-facing notifications
- **Formats port mappings** correctly (instead of raw Python repr)

## Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| TUI Framework | Textual >= 8.0 |
| CLI Formatting | Rich >= 13.0 |
| Docker Integration | Docker SDK >= 7.0 |

## Installation

### From source

```bash
git clone https://github.com/drbash/pretty-docker.git
cd pretty-docker
pip install -e .
```

### Using pip (when published)

```bash
pip install pretty-docker
```

### Using uv (alternative)

```bash
uv pip install -e .
```

## Usage

### TUI mode

Interactive terminal interface:

```bash
pretty-docker-tui
```

**Keyboard shortcuts:**

| Key | Action |
|-----|--------|
| `c` | Collapse all containers |
| `e` | Expand all containers |
| `r` | Refresh container list |
| `q` | Quit |

Each container appears as a collapsible panel showing its name. Press **Enter** or click to expand and see state, image, and port details.

### CLI mode

Quick container overview:

```bash
# Table format (default)
pretty-docker

# Running containers only
pretty-docker --running

# JSON output (for scripting)
pretty-docker --json

# Combine flags
pretty-docker --running --json
```

### Example outputs

**CLI table:**
```
┌───────────────┬─────────┬────────────────┬──────────────────┐
│ Name          │ State   │ Image          │ Ports            │
├───────────────┼─────────┼────────────────┼──────────────────┤
│ my_app        │ running │ nginx:latest   │ 0.0.0.0:8080 -> 80/tcp │
│ redis_cache   │ running │ redis:7-alpine │ 0.0.0.0:6379 -> 6379/tcp │
│ old_worker    │ exited  │ python:3.12    │ No ports exposed │
└───────────────┴─────────┴────────────────┴──────────────────┘
```

**CLI JSON:**
```json
[
  {
    "name": "my_app",
    "state": "running",
    "image": "nginx:latest",
    "ports": [
      {
        "container_port": "80/tcp",
        "host_ip": "0.0.0.0",
        "host_port": "8080"
      }
    ]
  }
]
```

**TUI screen (conceptual):**
```
┌─────────────────────────────────────────────────────┐
│ Pretty Docker                                       │
├─────────────────────────────────────────────────────┤
│ ┌─ my_app ────────────────────────────────────────┐ │
│ │ State:  running                                  │ │
│ │ Image:  nginx:latest                             │ │
│ │ Ports:  0.0.0.0:8080 -> 80/tcp                   │ │
│ └──────────────────────────────────────────────────┘ │
│ ┌─ redis_cache ────────────────────────────────────┐ │
│ │ State:  running                                  │ │
│ │ Image:  redis:7-alpine                           │ │
│ │ Ports:  0.0.0.0:6379 -> 6379/tcp                 │ │
│ └──────────────────────────────────────────────────┘ │
│ ┌─ old_worker ─────────────────────────────────────┐ │
│ │ State:  exited                                   │ │
│ │ Image:  python:3.12                              │ │
│ │ Ports:  No ports exposed                         │ │
│ └──────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────┤
│ C Collapse All  E Expand All  R Refresh  Q Quit     │
└─────────────────────────────────────────────────────┘
```

## Development

### Setup

```bash
git clone https://github.com/drbash/pretty-docker.git
cd pretty-docker
pip install -e ".[dev]"
```

### Running tests

```bash
pytest
```

### Project structure

```
pretty-docker/
├── pyproject.toml           # Package config, dependencies, entry points
├── pretty_docker/
│   ├── __init__.py
│   ├── cli.py               # CLI mode with Rich tables / JSON output
│   ├── tui.py               # TUI mode with Textual interactive interface
│   ├── docker_ops.py        # Docker SDK wrapper with error handling
│   └── models.py            # Data models (ContainerInfo, PortMapping)
└── tests/
    ├── __init__.py
    └── test_docker_ops.py   # Unit tests with mocked Docker SDK
```

### Entry points

| Command | Module | Description |
|---------|--------|-------------|
| `pretty-docker` | `pretty_docker.cli:main` | CLI mode |
| `pretty-docker-tui` | `pretty_docker.tui:main` | TUI mode |

## License

MIT
