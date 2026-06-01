from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from pretty_docker.docker_ops import (
    DockerNotAvailableError,
    _container_to_info,
    _map_port,
    get_container_details,
    list_containers,
)
from pretty_docker.models import ContainerInfo, PortMapping


class TestMapPort:
    def test_no_host_config(self) -> None:
        assert _map_port("8080/tcp", None) == [PortMapping(container_port="8080/tcp")]

    def test_empty_host_config(self) -> None:
        assert _map_port("8080/tcp", []) == [PortMapping(container_port="8080/tcp")]

    def test_with_host_config(self) -> None:
        result = _map_port("8080/tcp", [{"HostIp": "0.0.0.0", "HostPort": "8080"}])
        assert result == [
            PortMapping(container_port="8080/tcp", host_ip="0.0.0.0", host_port="8080")
        ]

    def test_multiple_host_configs(self) -> None:
        result = _map_port("8080/tcp", [
            {"HostIp": "0.0.0.0", "HostPort": "8080"},
            {"HostIp": "::", "HostPort": "8080"},
        ])
        assert result == [
            PortMapping(container_port="8080/tcp", host_ip="0.0.0.0", host_port="8080"),
            PortMapping(container_port="8080/tcp", host_ip="::", host_port="8080"),
        ]


class FakeContainer:
    def __init__(self, name: str, attrs: dict | None = None) -> None:
        self.name = name
        self.attrs = attrs or {}

    def reload(self) -> None:
        pass


class TestContainerToInfo:
    def test_basic(self) -> None:
        container = FakeContainer(
            name="my_app",
            attrs={
                "State": {"Status": "running"},
                "Config": {"Image": "nginx:latest"},
                "NetworkSettings": {"Ports": {}},
            },
        )
        info = _container_to_info(container)
        assert info.name == "my_app"
        assert info.state == "running"
        assert info.image == "nginx:latest"
        assert info.ports == []

    def test_with_ports(self) -> None:
        container = FakeContainer(
            name="web",
            attrs={
                "State": {"Status": "running"},
                "Config": {"Image": "nginx:latest"},
                "NetworkSettings": {
                    "Ports": {
                        "80/tcp": [{"HostIp": "0.0.0.0", "HostPort": "8080"}],
                    }
                },
            },
        )
        info = _container_to_info(container)
        assert info.ports == [
            PortMapping(container_port="80/tcp", host_ip="0.0.0.0", host_port="8080")
        ]

    def test_no_state(self) -> None:
        container = FakeContainer(name="test", attrs={})
        info = _container_to_info(container)
        assert info.state == "unknown"
        assert info.image == "unknown"

    def test_none_ports(self) -> None:
        container = FakeContainer(
            name="test",
            attrs={
                "State": {"Status": "running"},
                "Config": {"Image": "alpine"},
                "NetworkSettings": {"Ports": None},
            },
        )
        info = _container_to_info(container)
        assert info.ports == []


class TestFormatPorts:
    def test_no_ports(self) -> None:
        info = ContainerInfo(name="test", state="running", image="alpine")
        assert info.format_ports() == "No ports exposed"

    def test_with_ports(self) -> None:
        info = ContainerInfo(
            name="test",
            state="running",
            image="nginx",
            ports=[PortMapping(container_port="80/tcp", host_ip="0.0.0.0", host_port="8080")],
        )
        assert info.format_ports() == "0.0.0.0:8080 -> 80/tcp"

    def test_multiple_ports(self) -> None:
        info = ContainerInfo(
            name="test",
            state="running",
            image="nginx",
            ports=[
                PortMapping(container_port="80/tcp", host_ip="0.0.0.0", host_port="8080"),
                PortMapping(container_port="443/tcp", host_ip="0.0.0.0", host_port="8443"),
            ],
        )
        result = info.format_ports()
        assert "0.0.0.0:8080 -> 80/tcp" in result
        assert "0.0.0.0:8443 -> 443/tcp" in result


class TestListContainers:
    @patch("pretty_docker.docker_ops.docker.from_env")
    def test_success(self, mock_from_env: MagicMock) -> None:
        mock_client = MagicMock()
        mock_from_env.return_value = mock_client
        fake_container = FakeContainer(
            name="test",
            attrs={
                "State": {"Status": "running"},
                "Config": {"Image": "alpine"},
                "NetworkSettings": {"Ports": {}},
            },
        )
        mock_client.containers.list.return_value = [fake_container]

        result = list_containers()
        assert len(result) == 1
        assert result[0].name == "test"

    @patch("pretty_docker.docker_ops.docker.from_env")
    def test_docker_not_available(self, mock_from_env: MagicMock) -> None:
        from docker.errors import DockerException

        mock_from_env.side_effect = DockerException("connection failed")

        with pytest.raises(DockerNotAvailableError):
            list_containers()

    @patch("pretty_docker.docker_ops.docker.from_env")
    def test_passes_all_flag(self, mock_from_env: MagicMock) -> None:
        mock_client = MagicMock()
        mock_from_env.return_value = mock_client
        mock_client.containers.list.return_value = []

        list_containers(all=True)
        mock_client.containers.list.assert_called_with(all=True)

        list_containers(all=False)
        mock_client.containers.list.assert_called_with(all=False)


class TestGetContainerDetails:
    @patch("pretty_docker.docker_ops.docker.from_env")
    def test_success(self, mock_from_env: MagicMock) -> None:
        mock_client = MagicMock()
        mock_from_env.return_value = mock_client
        fake = FakeContainer(
            name="my_app",
            attrs={
                "State": {"Status": "exited"},
                "Config": {"Image": "alpine"},
                "NetworkSettings": {"Ports": {}},
            },
        )
        mock_client.containers.get.return_value = fake

        info = get_container_details("my_app")
        assert info.name == "my_app"
        assert info.state == "exited"

    @patch("pretty_docker.docker_ops.docker.from_env")
    def test_not_found(self, mock_from_env: MagicMock) -> None:
        from docker.errors import NotFound

        mock_client = MagicMock()
        mock_from_env.return_value = mock_client
        mock_client.containers.get.side_effect = NotFound("not found")

        from pretty_docker.docker_ops import ContainerNotFoundError

        with pytest.raises(ContainerNotFoundError):
            get_container_details("ghost")
