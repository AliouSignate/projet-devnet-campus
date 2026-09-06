from src.role import detect_role


def test_router_hostname_simple():
    assert detect_role("R1-DKR") == "router"


def test_core_switch_hostname_simple():
    assert detect_role("SW1-CORE") == "core_switch"


def test_access_switch_hostname_simple():
    assert detect_role("SW1-ACC") == "access_switch"


def test_unknown_hostname():
    assert detect_role("MYSTERE") == "unknown"


def test_router_hostname_with_prompt():
    assert detect_role("R1-DKR#") == "router"


def test_core_switch_hostname_with_prompt():
    assert detect_role("SW1-CORE#") == "core_switch"