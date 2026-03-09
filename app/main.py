import os

import streamlit as st

from app.core.paths import ensure_base_dirs
from app.repositories.history_repository import load_long_df
from app.repositories.printers_repository import carregar_impressoras
from app.services.analytics_service import snapshot_ultima_leitura
from app.ui import cadastro_page, coleta_page, dashboard_page, relatorios_page
from app.ui.components import inject_global_css, render_sidebar_branding

LOGO_PATH = os.path.join("app", "pdf", "assets", "hp_logo.png")


def bootstrap():
    ensure_base_dirs()
    carregar_impressoras()
    load_long_df()


def render_sidebar():
    with st.sidebar:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=82)

        render_sidebar_branding(
            "Print Monitor Pro",
            "Monitoramento SNMP, histórico e relatórios corporativos",
        )

        menu = st.radio(
            "Navegação",
            [
                "Dashboard",
                "Cadastro",
                "Coleta SNMP",
                "Relatórios PDF",
            ],
        )
        st.caption("Versão Streamlit")
        return menu


def main():
    st.set_page_config(
        page_title="Print Monitor Pro",
        page_icon="🖨️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    bootstrap()
    inject_global_css()

    menu = render_sidebar()
    df_long = load_long_df()
    piv_df = snapshot_ultima_leitura(df_long)

    if menu == "Dashboard":
        dashboard_page.render(piv_df, df_long)
    elif menu == "Cadastro":
        cadastro_page.render()
    elif menu == "Coleta SNMP":
        coleta_page.render()
    elif menu == "Relatórios PDF":
        relatorios_page.render(piv_df)


if __name__ == "__main__":
    main()
