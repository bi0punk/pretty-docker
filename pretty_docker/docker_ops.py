from __future__ import annotations

import docker
from docker.errors import DockerException
from docker.models.containers import Container

from pretty_docker.models import ContainerInfo, PortMapping


class DockerNotAvailableError(Exception):
    pass


class ContainerNotFoundError(Exception):
    pass


def _map_port(container_port: str, host_config: list[dict] | None) -> list[PortMapping]:
    if not host_config:
        return [PortMapping(container_port=container_port)]
    return [
        PortMapping(
            container_port=container_port,
            host_ip=entry.get("HostIp"),
            host_port=entry.get("HostPort"),
        )
        for entry in host_config
    ]


def _container_to_info(container: Container) -> ContainerInfo:
    attrs = container.attrs or {}
    state = attrs.get("State", {}).get("Status", "unknown")
    image = attrs.get("Config", {}).get("Image", "unknown")
    ports_raw = attrs.get("NetworkSettings", {}).get("Ports", {}) or {}
    ports = [
        mapping
        for container_port, host_config in ports_raw.items()
        for mapping in _map_port(container_port, host_config)
    ]
    return ContainerInfo(
        name=container.name,
        state=state,
        image=image,
        ports=ports,
    )


def get_client() -> docker.DockerClient:
    try:
        return docker.from_env()
    except DockerException as e:
        raise DockerNotAvailableError(
            "Cannot connect to Docker daemon. Is Docker running?"
        ) from e


def list_containers(all: bool = True) -> list[ContainerInfo]:
    client = get_client()
    try:
        containers = client.containers.list(all=all)
        return [_container_to_info(c) for c in containers]
    except DockerException as e:
        raise DockerNotAvailableError(
            f"Failed to list containers: {e}"
        ) from e
    finally:
        client.close()


def get_container_details(name: str) -> ContainerInfo:
    client = get_client()
    try:
        container = client.containers.get(name)
        container.reload()
        return _container_to_info(container)
    except docker.errors.NotFound as e:
        raise ContainerNotFoundError(f"Container '{name}' not found") from e
    except DockerException as e:
        raise DockerNotAvailableError(
            f"Failed to inspect container '{name}': {e}"
        ) from e
    finally:
        client.close()
