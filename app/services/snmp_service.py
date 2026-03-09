# app/services/snmp_service.py

from datetime import datetime

from pysnmp.hlapi.v3arch.asyncio import (
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    get_cmd,
)

from app.config.config import COMMUNITY, OIDS_CONTADORES, OIDS_INFO, PORT, RETRIES, TIMEOUT
from app.repositories.history_repository import append_long
from app.repositories.printers_repository import carregar_impressoras


async def snmp_get_one(ip: str, oid: str):
    """
    Faz um GET SNMP para um OID específico.
    Tenta primeiro SNMP v2c e depois v1, igual à base antiga.
    """
    try:
        target = await UdpTransportTarget.create(
            (ip, PORT),
            timeout=TIMEOUT,
            retries=RETRIES,
        )

        for mp in (1, 0):  # v2c depois v1
            error_indication, error_status, error_index, var_binds = await get_cmd(
                SnmpEngine(),
                CommunityData(COMMUNITY, mpModel=mp),
                target,
                ContextData(),
                ObjectType(ObjectIdentity(oid)),
            )

            if not error_indication and not error_status and var_binds:
                val = var_binds[0][1]
                try:
                    return int(val)
                except Exception:
                    return str(val)

        return None
    except Exception:
        return None


async def coletar_impressora(ip: str, mapa_oids: dict) -> dict:
    """
    Coleta todos os OIDs mapeados para uma impressora.
    """
    out = {}
    for chave, oid in mapa_oids.items():
        out[chave] = await snmp_get_one(ip, oid)
    return out


def obter_mapa_oids() -> dict:
    """
    Junta OIDs informativos + contadores.
    """
    mapa_total = {}
    mapa_total.update(OIDS_INFO)
    mapa_total.update(OIDS_CONTADORES)
    return mapa_total


async def processar_atualizacao():
    """
    Lê todas as impressoras cadastradas e salva no histórico CSV.
    Retorna:
        (ok: bool, mensagem: str, falhas: list[dict])
    """
    impressoras = carregar_impressoras()
    if not impressoras:
        return False, "Nenhuma impressora cadastrada.", []

    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mapa_total = obter_mapa_oids()

    rows = []
    falhas = []
    ok_count = 0

    for imp in impressoras:
        ip = str(imp.get("ip", "")).strip()
        dados = await coletar_impressora(ip, mapa_total)

        if any(v is not None for v in dados.values()):
            ok_count += 1
            for chave, valor in dados.items():
                rows.append(
                    {
                        "Data": agora,
                        "Departamento": imp.get("departamento", ""),
                        "Nome": imp.get("nome", ""),
                        "IP": ip,
                        "Chave": chave,
                        "Valor": valor,
                    }
                )
        else:
            falhas.append(imp)

    if ok_count == 0:
        return False, "Nenhuma impressora respondeu SNMP. Verifique rede/ACL/community/SNMP.", falhas

    append_long(rows)
    return True, f"Sucesso! {ok_count} impressora(s) lida(s).", falhas