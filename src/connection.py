from netmiko import ConnectHandler
from netmiko.ssh_autodetect import SSHDetect

from src.role import detect_role
from src.logger import get_logger

logger = get_logger(__name__)


def autodetect_device_type(host: str, username: str, password: str, port: int = 22) -> str:
    guesser = SSHDetect(
        device_type="autodetect",
        host=host,
        username=username,
        password=password,
        port=port,
    )
    best_match = guesser.autodetect()
    if not best_match:
        raise RuntimeError(f"Autodetect impossible pour {host}")
    logger.info("device_type autodetecte pour %s : %s", host, best_match)
    return best_match


def connect(host: str, credentials, port: int = 22, timeout: int = 15):
    device_type = autodetect_device_type(
        host, credentials.username, credentials.password, port
    )

    connection = ConnectHandler(
        device_type=device_type,
        host=host,
        username=credentials.username,
        password=credentials.password,
        secret=credentials.secret,
        port=port,
        timeout=timeout,
    )

    try:
        connection.enable()
    except Exception as e:
        logger.warning("enable() a echoue ou n'etait pas necessaire : %s", e)

    prompt = connection.find_prompt()
    role = detect_role(prompt)

    logger.info("Connecte a %s (prompt='%s', role=%s)", host, prompt, role)

    return connection, prompt, role