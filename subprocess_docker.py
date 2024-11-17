import subprocess
from textual.app import App, ComposeResult
from textual.widgets import Collapsible, Footer, Label
import json

def get_docker_container_names():
    # Ejecuta el comando `docker ps -a` y obtiene los nombres de los contenedores
    result = subprocess.run(
        ["docker", "ps", "-a", "--format", "{{.Names}}"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip().split("\n")

def get_container_details(container_name):
    # Ejecuta el comando `docker inspect` para obtener detalles del contenedor
    result = subprocess.run(
        ["docker", "inspect", container_name],
        capture_output=True,
        text=True
    )
    container_info = json.loads(result.stdout)[0]
    
    # Extraer información relevante del contenedor
    state = container_info["State"]["Status"]
    image = container_info["Config"]["Image"]
    ports = container_info.get("NetworkSettings", {}).get("Ports", {})
    
    # Formatear los detalles para mostrar
    ports_info = ", ".join(f"{key}: {value}" for key, value in ports.items()) if ports else "No ports exposed"
    
    details = f"""
    **State:** {state}
    **Image:** {image}
    **Ports:** {ports_info}
    """
    return details

class CollapsibleApp(App[None]):
    """An example of collapsible container with Docker container names and details."""

    BINDINGS = [
        ("c", "collapse_or_expand(True)", "Collapse All"),
        ("e", "collapse_or_expand(False)", "Expand All"),
    ]

    def compose(self) -> ComposeResult:
        """Compose app with collapsible containers for each Docker container."""
        yield Footer()
        
        container_names = get_docker_container_names()
        
        # Crea un Collapsible para cada contenedor Docker
        for name in container_names:
            with Collapsible(collapsed=True, title=name):
                details = get_container_details(name)
                yield Label(details)
                
    def action_collapse_or_expand(self, collapse: bool) -> None:
        for child in self.walk_children(Collapsible):
            child.collapsed = collapse


if __name__ == "__main__":
    app = CollapsibleApp()
    app.run()
