from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

from src.inventory import load_inventory
from src.connection import connect
from src.backup import backup_running_config, save_running_config
from src.routing import migrate_to_eigrp
from src.switching import enable_portfast_on_access_ports
from src.verify import DeviceReport, build_summary
from src.logger import get_logger

logger = get_logger(__name__)

# Interfaces d'acces vers les PC, par hostname declare dans l'inventaire.
# Seuls les switches d'acces ont une entree ici.
ACCESS_INTERFACES_BY_HOSTNAME = {
    "SW1-ACC": ["Ethernet0/1", "Ethernet0/2"],
    "SW2-ACC": ["Ethernet0/1", "Ethernet0/2"],
    "SW3-ACC": ["Ethernet0/1", "Ethernet0/2"],
}


def process_device(device, credentials, port: int, timeout: int) -> DeviceReport:
    hostname_declare = device.name

    try:
        connection, real_hostname, role = connect(
            device.mgmt_ip, credentials, port=port, timeout=timeout
        )
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as exc:
        logger.error("Connexion impossible a %s (%s) : %s", hostname_declare, device.mgmt_ip, exc)
        return DeviceReport(hostname=hostname_declare, reachable=False, role="unknown", error=str(exc))
    except Exception as exc:
        logger.exception("Erreur inattendue lors de la connexion a %s", hostname_declare)
        return DeviceReport(hostname=hostname_declare, reachable=False, role="unknown", error=str(exc))

    try:
        # 1. Backup AVANT toute modification
        backup_running_config(connection, real_hostname)

        # 2. Config selon le role
        if role == "router":
            migrate_to_eigrp(connection, real_hostname)

        elif role in ("core_switch", "access_switch"):
            access_ifaces = ACCESS_INTERFACES_BY_HOSTNAME.get(hostname_declare, [])
            if access_ifaces:
                enable_portfast_on_access_ports(connection, access_ifaces)

        else:
            logger.warning("Role inconnu pour %s - aucune config appliquee.", real_hostname)

                # 3. Sauvegarde en NVRAM APRES application
        try:
            save_running_config(connection, real_hostname)
        except Exception as exc:
            logger.warning(
                "save_config a echoue sur %s (config appliquee mais non persistee en NVRAM) : %s",
                real_hostname, exc
            )

        return DeviceReport(hostname=real_hostname, reachable=True, role=role)

    except Exception as exc:
        logger.exception("Erreur lors du traitement de %s", real_hostname)
        return DeviceReport(hostname=real_hostname, reachable=False, role=role, error=str(exc))

    finally:
        try:
            connection.disconnect()
        except Exception:
            pass


def main() -> None:
    inventory = load_inventory("inventory.yaml")

    reports = []
    for device in inventory.devices:
        logger.info("=== Traitement de %s (%s) ===", device.name, device.mgmt_ip)
        report = process_device(
            device,
            inventory.credentials,
            port=inventory.conn_port,
            timeout=inventory.conn_timeout,
        )
        reports.append(report)

    summary = build_summary(reports)
    logger.info("\n%s", summary)
    print(summary)


if __name__ == "__main__":
    main()