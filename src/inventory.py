import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv

from src.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DeviceConfig:
    name: str
    mgmt_ip: str
    role_hint: str
    site: str
    vlan_id: int


@dataclass
class Credentials:
    username: str
    password: str
    secret: str


@dataclass
class Inventory:
    devices: list
    eigrp_as: int
    conn_port: int
    conn_timeout: int
    credentials: Credentials


def load_credentials() -> Credentials:
    load_dotenv()

    username = os.environ.get("NET_USERNAME")
    password = os.environ.get("NET_PASSWORD")
    secret = os.environ.get("NET_SECRET", password)

    missing = [
        var for var, val in (("NET_USERNAME", username), ("NET_PASSWORD", password))
        if not val
    ]
    if missing:
        raise RuntimeError(
            f"Variables d'environnement manquantes : {', '.join(missing)}. "
            "Copie .env.example en .env et complete-le."
        )

    return Credentials(username=username, password=password, secret=secret)


def load_inventory(path: str = "inventory.yaml") -> Inventory:
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise FileNotFoundError(f"Inventaire introuvable : {yaml_path}")

    with yaml_path.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    devices = []
    for site in raw.get("sites", []):
        for dev in site.get("devices", []):
            devices.append(
                DeviceConfig(
                    name=dev["name"],
                    mgmt_ip=dev["mgmt_ip"],
                    role_hint=dev.get("role_hint", "unknown"),
                    site=site["name"],
                    vlan_id=site.get("vlan_id"),
                )
            )

    if not devices:
        raise ValueError("Aucun equipement trouve dans l'inventaire")

    conn = raw.get("connection", {})
    eigrp = raw.get("eigrp", {})

    logger.info("Inventaire charge : %d equipement(s)", len(devices))

    return Inventory(
        devices=devices,
        eigrp_as=eigrp.get("as_number", 100),
        conn_port=conn.get("port", 22),
        conn_timeout=conn.get("timeout", 15),
        credentials=load_credentials(),
    )