from pathlib import Path

from src.logger import get_logger

logger = get_logger(__name__)

EIGRP_CONFIG_DIR = Path(__file__).resolve().parent.parent / "configs" / "eigrp"


def load_eigrp_config(hostname: str) -> list[str]:
    safe_hostname = hostname.strip("#>").strip()
    config_path = EIGRP_CONFIG_DIR / f"{safe_hostname}.txt"

    if not config_path.exists():
        raise FileNotFoundError(
            f"Pas de config EIGRP externe trouvee pour {safe_hostname} "
            f"(attendu : {config_path})"
        )

    lines = []
    for raw_line in config_path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("!"):
            continue
        lines.append(raw_line)

    return lines


def migrate_to_eigrp(connection, hostname: str) -> None:
    config_lines = load_eigrp_config(hostname)
    logger.info("Application de la migration EIGRP sur %s (%d lignes)", hostname, len(config_lines))

    output = connection.send_config_set(config_lines)
    logger.debug("Sortie migration EIGRP sur %s :\n%s", hostname, output)