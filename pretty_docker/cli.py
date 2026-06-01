from __future__ import annotations

import json
import sys
from argparse import ArgumentParser, Namespace

from rich.console import Console
from rich.table import Table

from pretty_docker.docker_ops import (
    ContainerNotFoundError,
    DockerNotAvailableError,
    list_containers,
)


def build_table(containers: list) -> Table:
    table = Table(title="Docker Containers")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("State", style="magenta")
    table.add_column("Image", style="green")
    table.add_column("Ports", style="yellow")
    for c in containers:
        table.add_row(c.name, c.state, c.image, c.format_ports())
    return table


def run_json(containers: list) -> str:
    data = [
        {
            "name": c.name,
            "state": c.state,
            "image": c.image,
            "ports": [p.__dict__ for p in c.ports],
        }
        for c in containers
    ]
    return json.dumps(data, indent=2)


def parse_args(argv: list[str] | None = None) -> Namespace:
    parser = ArgumentParser(prog="pretty-docker", description="Docker container viewer")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of table",
    )
    parser.add_argument(
        "--running",
        action="store_true",
        help="Show only running containers",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    console = Console()

    try:
        containers = list_containers(all=not args.running)
    except DockerNotAvailableError as e:
        console.print(f"[red]Error:[/red] {e}", stderr=True)
        return 1
    except ContainerNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}", stderr=True)
        return 1

    if not containers:
        console.print("[yellow]No containers found.[/yellow]")
        return 0

    if args.json:
        console.print(run_json(containers))
    else:
        table = build_table(containers)
        console.print(table)

    return 0


if __name__ == "__main__":
    sys.exit(main())
