def detect_role(hostname: str) -> str:
    name = hostname.upper()
    
    if name.startswith("R"):
        return "router"
    elif "CORE" in name:
        return "core_switch"
    elif "ACC" in name:
        return "access_switch"
    else:
        return "unknown"