# app/services/printer_service.py

from app.core.utils import ip_valido


def validar_dados_impressora(nome: str, ip: str, departamento: str) -> tuple[bool, str]:
    if not nome.strip():
        return False, "Informe o nome da impressora."

    if not ip.strip():
        return False, "Informe o IP da impressora."

    if not departamento.strip():
        return False, "Informe o departamento."

    if not ip_valido(ip):
        return False, "IP inválido."

    return True, ""


def impressora_duplicada(impressoras: list[dict], ip: str) -> bool:
    ip_limpo = ip.strip()
    return any(str(item.get("ip", "")).strip() == ip_limpo for item in impressoras)