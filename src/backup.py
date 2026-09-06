from datetime import datetime
from pathlib import Path

from src.logger import get_logger

logger = get_logger(__name__)

BACKUP_DIR = Path(__file__).resolve().parent.parent / "backups"
BACKUP_DIR.mkdir(exist_ok=True)


def backup_running_config(connection, hostname: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_hostname = hostname.strip("#>").strip() or "unknown"
    backup_path = BACKUP_DIR / f"{safe_hostname}_{timestamp}.txt"

    running_config = connection.send_command("show running-config")
    backup_path.write_text(running_config, encoding="utf-8")

    logger.info("Backup de %s sauvegarde -> %s", safe_hostname, backup_path)
    return backup_path


def save_running_config(connection, hostname: str) -> None:
    connection.save_config()
    logger.info("Configuration sauvegardee (save_config) sur %s", hostname)