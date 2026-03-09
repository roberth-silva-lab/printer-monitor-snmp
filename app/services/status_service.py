import asyncio
import platform
import subprocess

from app.config.config import OIDS_INFO
from app.services.snmp_service import snmp_get_one

STATUS_ONLINE = "ONLINE"
STATUS_OFFLINE = "OFFLINE"
STATUS_SNMP_SEM_RESPOSTA = "SNMP BLOQUEADO"


def ping_host(ip: str, timeout_ms: int = 1200) -> bool:
    try:
        if platform.system().lower() == "windows":
            cmd = ["ping", "-n", "1", "-w", str(timeout_ms), ip]
        else:
            timeout_s = max(1, int(timeout_ms / 1000))
            cmd = ["ping", "-c", "1", "-W", str(timeout_s), ip]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=4)
        return result.returncode == 0
    except Exception:
        return False


async def _check_snmp(ip: str) -> bool:
    probe_oid = OIDS_INFO.get("Info :: sysName", "1.3.6.1.2.1.1.5.0")
    valor = await snmp_get_one(ip, probe_oid)
    return valor is not None


async def evaluate_printer_status(ip: str) -> dict:
    ping_ok = ping_host(ip)
    if not ping_ok:
        return {
            "status": STATUS_OFFLINE,
            "ping_ok": False,
            "snmp_ok": False,
            "detalhe": "Sem resposta ao ping.",
        }

    snmp_ok = await _check_snmp(ip)
    if snmp_ok:
        status = STATUS_ONLINE
        detalhe = "Ping e SNMP respondendo."
    else:
        status = STATUS_SNMP_SEM_RESPOSTA
        detalhe = "Ping responde, mas SNMP sem resposta."

    return {
        "status": status,
        "ping_ok": ping_ok,
        "snmp_ok": snmp_ok,
        "detalhe": detalhe,
    }


def evaluate_printer_status_sync(ip: str) -> dict:
    return asyncio.run(evaluate_printer_status(ip))


async def evaluate_fleet_status(printers: list[dict]) -> list[dict]:
    resultado = []
    for imp in printers:
        ip = str(imp.get("ip", "")).strip()
        status_data = await evaluate_printer_status(ip)
        resultado.append(
            {
                "Departamento": imp.get("departamento", ""),
                "Nome": imp.get("nome", ""),
                "IP": ip,
                "Status": status_data["status"],
                "Detalhe": status_data["detalhe"],
            }
        )
    return resultado


def evaluate_fleet_status_sync(printers: list[dict]) -> list[dict]:
    return asyncio.run(evaluate_fleet_status(printers))
