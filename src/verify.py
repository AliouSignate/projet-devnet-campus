from dataclasses import dataclass, field

from src.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DeviceReport:
    hostname: str
    reachable: bool
    role: str
    error: str = ""


def build_summary(reports: list[DeviceReport]) -> str:
    lines = ["=== Rapport de verification post-deploiement ==="]
    for r in reports:
        status = "OK" if r.reachable else "ECHEC"
        lines.append(f"- {r.hostname} [{r.role}] : {status}")
        if r.error:
            lines.append(f"    erreur : {r.error}")
    return "\n".join(lines)