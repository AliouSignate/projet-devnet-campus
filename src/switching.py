from src.logger import get_logger

logger = get_logger(__name__)


def enable_portfast_on_access_ports(connection, access_interfaces: list[str]) -> None:
    if not access_interfaces:
        logger.warning("Aucune interface d'accès fournie - rien a faire.")
        return

    config_lines = []
    for iface in access_interfaces:
        config_lines.append(f"interface {iface}")
        config_lines.append(" spanning-tree portfast")
        config_lines.append(" exit")

    output = connection.send_config_set(config_lines)
    logger.info("Portfast active sur %d interface(s) d'acces : %s", len(access_interfaces), access_interfaces)
    logger.debug("Sortie portfast :\n%s", output)


def guard_against_trunk_ports(access_interfaces: list[str], trunk_interfaces: list[str]) -> None:
    overlap = set(access_interfaces) & set(trunk_interfaces)
    if overlap:
        raise ValueError(
            f"Interfaces declarees a la fois en acces et en trunk : {overlap} "
            "- portfast ne doit jamais etre active sur un lien trunk/uplink."
        )