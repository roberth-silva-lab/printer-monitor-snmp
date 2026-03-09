# app/core/utils.py

import ipaddress
from datetime import datetime


def ip_valido(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip.strip())
        return True
    except ValueError:
        return False


def agora_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def pdf_safe(text) -> str:
    if text is None:
        return ""

    s = str(text)
    s = (
        s.replace("•", "-")
         .replace("–", "-")
         .replace("—", "-")
         .replace("“", '"')
         .replace("”", '"')
         .replace("’", "'")
         .replace("´", "'")
    )
    return s.encode("latin-1", "replace").decode("latin-1")