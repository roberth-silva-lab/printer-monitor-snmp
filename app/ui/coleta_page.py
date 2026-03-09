import asyncio

import pandas as pd
import streamlit as st

from app.config.config import OIDS_CONTADORES, OIDS_INFO
from app.repositories.history_repository import append_long
from app.repositories.printers_repository import carregar_impressoras
from app.services.snmp_service import coletar_impressora, processar_atualizacao
from app.services.status_service import evaluate_printer_status_sync
from app.ui.components import render_page_header, render_section_title, render_status_badge


def _get_mapa_total():
    mapa_total = {}
    mapa_total.update(OIDS_INFO)
    mapa_total.update(OIDS_CONTADORES)
    return mapa_total


async def _coletar_uma_impressora(imp: dict):
    mapa_total = _get_mapa_total()
    return await coletar_impressora(imp["ip"], mapa_total)


def render():
    render_page_header(
        "Coleta SNMP",
        "Execute leitura individual ou em lote para atualizar o histórico.",
        "🔄",
    )

    impressoras = carregar_impressoras()
    if not impressoras:
        st.warning("Nenhuma impressora cadastrada.")
        return

    nomes = [imp["nome"] for imp in impressoras]
    aba1, aba2 = st.tabs(["Coletar todas", "Coletar uma"])

    with aba1:
        render_section_title("Leitura em lote")
        st.write("Executa leitura SNMP em todas as impressoras cadastradas.")

        if st.button("Iniciar coleta de todas", type="primary"):
            with st.spinner("Coletando dados das impressoras..."):
                ok, msg, falhas = asyncio.run(processar_atualizacao())

            if ok:
                st.success(msg)
            else:
                st.error(msg)

            if falhas:
                st.warning("Impressoras sem resposta:")
                st.dataframe(falhas, width="stretch")

    with aba2:
        render_section_title("Leitura individual")
        selecionada = st.selectbox("Escolha a impressora", options=nomes)
        imp = next((i for i in impressoras if i["nome"] == selecionada), None)

        if imp:
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("Verificar status"):
                    status_data = evaluate_printer_status_sync(imp["ip"])
                    render_status_badge(status_data["status"])
                    st.caption(status_data["detalhe"])

            with col2:
                if st.button("Testar ping"):
                    status_data = evaluate_printer_status_sync(imp["ip"])
                    if status_data["ping_ok"]:
                        st.success(f"{imp['nome']} respondeu ao ping.")
                    else:
                        st.error(f"{imp['nome']} não respondeu ao ping.")

            with col3:
                if st.button("Coletar dados desta impressora", type="primary"):
                    with st.spinner("Consultando impressora..."):
                        dados = asyncio.run(_coletar_uma_impressora(imp))

                    if any(v is not None for v in dados.values()):
                        agora = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                        rows = []
                        for chave, valor in dados.items():
                            rows.append(
                                {
                                    "Data": agora,
                                    "Departamento": imp.get("departamento", ""),
                                    "Nome": imp.get("nome", ""),
                                    "IP": imp.get("ip", ""),
                                    "Chave": chave,
                                    "Valor": valor,
                                }
                            )

                        append_long(rows)
                        st.success("Coleta realizada e salva no histórico.")
                        st.json(dados)
                    else:
                        st.error("A impressora não respondeu ao SNMP.")
