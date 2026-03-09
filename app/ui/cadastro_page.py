import streamlit as st

from app.models.printer import Printer
from app.repositories.printers_repository import carregar_impressoras, salvar_impressoras
from app.services.printer_service import impressora_duplicada, validar_dados_impressora
from app.ui.components import render_page_header, render_section_title


def render():
    render_page_header(
        "Cadastro de Impressoras",
        "Cadastre nome, IP e departamento para habilitar a coleta SNMP.",
        "🖨️",
    )

    with st.container():
        with st.form("cadastro_impressora_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                nome = st.text_input("Nome da impressora")
            with c2:
                ip = st.text_input("IP")
            with c3:
                departamento = st.text_input("Departamento")

            submitted = st.form_submit_button("Salvar impressora", type="primary")
            if submitted:
                ok, msg = validar_dados_impressora(nome, ip, departamento)
                if not ok:
                    st.error(msg)
                else:
                    impressoras = carregar_impressoras()
                    if impressora_duplicada(impressoras, ip):
                        st.warning("Já existe uma impressora cadastrada com esse IP.")
                    else:
                        nova = Printer(nome=nome, ip=ip, departamento=departamento)
                        impressoras.append(nova.to_dict())
                        salvar_impressoras(impressoras)
                        st.success("Impressora cadastrada com sucesso.")
                        st.rerun()

    st.divider()
    render_section_title("Impressoras cadastradas")
    impressoras = carregar_impressoras()
    if not impressoras:
        st.info("Nenhuma impressora cadastrada.")
        return

    st.dataframe(impressoras, width="stretch")
    st.divider()
    if st.button("Limpar cadastro de impressoras"):
        salvar_impressoras([])
        st.success("Cadastro limpo com sucesso.")
        st.rerun()
