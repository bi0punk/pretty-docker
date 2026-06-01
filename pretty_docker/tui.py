from __future__ import annotations

import sys

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widgets import Collapsible, Footer, Header, Static

from pretty_docker.docker_ops import (
    ContainerNotFoundError,
    DockerNotAvailableError,
    list_containers,
)
from pretty_docker.models import ContainerInfo


class ContainerDetails(Static):
    pass


class DockerTuiApp(App[None]):
    TITLE = "Pretty Docker"
    CSS = """
    Screen {
        background: $surface;
    }
    Collapsible {
        margin: 0 1;
        border: solid $primary;
    }
    Collapsible > Static {
        padding: 0 1;
    }
    ContainerDetails {
        padding: 0 2;
    }
    """

    BINDINGS = [
        Binding("c", "collapse_all", "Collapse All"),
        Binding("e", "expand_all", "Expand All"),
        Binding("r", "refresh", "Refresh"),
        Binding("q", "quit", "Quit"),
    ]

    containers: reactive[list[ContainerInfo]] = reactive([])
    loading: reactive[bool] = reactive(True)

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(id="container-list")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_containers()

    def refresh_containers(self) -> None:
        self.loading = True
        self.run_worker(self._load_containers(), exclusive=True)

    async def _load_containers(self) -> list[ContainerInfo]:
        try:
            self.containers = await self._fetch_containers()
        except DockerNotAvailableError as e:
            self.notify(str(e), severity="error", timeout=10)
            self.containers = []
        except ContainerNotFoundError as e:
            self.notify(str(e), severity="error", timeout=10)
            self.containers = []
        finally:
            self.loading = False
        return self.containers

    async def _fetch_containers(self) -> list[ContainerInfo]:
        from asyncio import to_thread
        return await to_thread(list_containers, True)

    def watch_containers(self, containers: list[ContainerInfo]) -> None:
        container_list = self.query_one("#container-list", VerticalScroll)
        container_list.remove_children()
        for c in containers:
            collapsible = Collapsible(collapsed=True, title=c.name)
            details = ContainerDetails(
                f"[bold]State:[/bold] {c.state}\n"
                f"[bold]Image:[/bold] {c.image}\n"
                f"[bold]Ports:[/bold] {c.format_ports()}"
            )
            collapsible.compose_add_child(details)
            container_list.mount(collapsible)
        if self.loading:
            container_list.mount(
                Static("[dim]Loading containers...[/dim]", id="loading-msg")
            )

    def action_collapse_all(self) -> None:
        for c in self.query(Collapsible):
            c.collapsed = True

    def action_expand_all(self) -> None:
        for c in self.query(Collapsible):
            c.collapsed = False

    def action_refresh(self) -> None:
        self.refresh_containers()

    def action_quit(self) -> None:
        self.exit()


def main() -> int:
    app = DockerTuiApp()
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
