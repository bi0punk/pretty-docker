from dataclasses import dataclass, field


@dataclass
class PortMapping:
    container_port: str
    host_ip: str | None = None
    host_port: str | None = None

    def __str__(self) -> str:
        if self.host_ip and self.host_port:
            return f"{self.host_ip}:{self.host_port} -> {self.container_port}"
        return self.container_port


@dataclass
class ContainerInfo:
    name: str
    state: str
    image: str
    ports: list[PortMapping] = field(default_factory=list)

    def format_ports(self) -> str:
        if not self.ports:
            return "No ports exposed"
        return ", ".join(str(p) for p in self.ports)
