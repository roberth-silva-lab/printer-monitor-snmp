import pandas as pd
import plotly.express as px
import streamlit as st

from app.repositories.printers_repository import carregar_impressoras
from app.services.status_service import evaluate_fleet_status_sync
from app.ui.components import (
    render_empty_state,
    render_metric_card,
    render_page_header,
    render_section_title,
)

CONTADOR_COLUNA = "Impressora :: Contagem total de páginas do mecanismo"


def _to_numeric_safe(series):
    return pd.to_numeric(series, errors="coerce")


def _enrich_with_status(df: pd.DataFrame) -> pd.DataFrame:
    printers = carregar_impressoras()
    if not printers:
        out = df.copy()
        out["Status"] = "SNMP BLOQUEADO"
        return out

    status_rows = evaluate_fleet_status_sync(printers)
    status_df = pd.DataFrame(status_rows)
    if status_df.empty:
        out = df.copy()
        out["Status"] = "SNMP BLOQUEADO"
        return out

    out = df.merge(status_df[["Nome", "IP", "Status"]], on=["Nome", "IP"], how="left")
    out["Status"] = out["Status"].fillna("SNMP BLOQUEADO")
    return out


def _plot_paginas_por_departamento(df: pd.DataFrame):
    dept_df = (
        df.groupby("Departamento", dropna=False)[CONTADOR_COLUNA]
        .sum(min_count=1)
        .reset_index()
        .fillna(0)
        .sort_values(CONTADOR_COLUNA, ascending=False)
    )

    fig = px.bar(
        dept_df,
        x="Departamento",
        y=CONTADOR_COLUNA,
        text_auto=True,
        color="Departamento",
    )
    fig.update_layout(
        title="Volume de páginas por departamento",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    st.plotly_chart(fig, width="stretch")


def _plot_top_impressoras(df: pd.DataFrame):
    top_df = (
        df[["Nome", "Departamento", CONTADOR_COLUNA]]
        .copy()
        .sort_values(CONTADOR_COLUNA, ascending=False)
        .head(10)
    )

    fig = px.bar(
        top_df,
        x="Nome",
        y=CONTADOR_COLUNA,
        color="Departamento",
        text_auto=True,
    )
    fig.update_layout(
        title="Top 10 impressoras por contador",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, width="stretch")


def render(piv_df: pd.DataFrame, df_long: pd.DataFrame):
    render_page_header(
        "Dashboard",
        "Visão consolidada das impressoras, indicadores e status de conectividade.",
        "📊",
    )

    if piv_df is None or piv_df.empty:
        render_empty_state("Nenhum dado coletado ainda. Acesse 'Coleta SNMP' para iniciar.")
        return

    df = piv_df.copy()
    if CONTADOR_COLUNA not in df.columns:
        df[CONTADOR_COLUNA] = 0
    df[CONTADOR_COLUNA] = _to_numeric_safe(df[CONTADOR_COLUNA]).fillna(0)

    with st.container(border=True):
        col_btn1, col_btn2 = st.columns([1, 3])
        with col_btn1:
            atualizar_status = st.button("Atualizar status de rede", type="primary")
        with col_btn2:
            st.caption("ONLINE = responde ping e SNMP | OFFLINE = sem ping | SNMP BLOQUEADO = ping ok e SNMP sem resposta")

    if "dashboard_status_df" not in st.session_state:
        st.session_state["dashboard_status_df"] = _enrich_with_status(df)
    elif atualizar_status:
        st.session_state["dashboard_status_df"] = _enrich_with_status(df)

    df = st.session_state["dashboard_status_df"].copy()

    total_impressoras = df["Nome"].nunique() if "Nome" in df.columns else 0
    total_departamentos = df["Departamento"].nunique() if "Departamento" in df.columns else 0
    total_paginas = int(df[CONTADOR_COLUNA].sum())

    ultima_coleta = "-"
    if df_long is not None and not df_long.empty and "Data" in df_long.columns:
        ultima_data = pd.to_datetime(df_long["Data"], errors="coerce").max()
        if pd.notna(ultima_data):
            ultima_coleta = ultima_data.strftime("%d/%m/%Y %H:%M:%S")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Total de impressoras", total_impressoras)
    with c2:
        render_metric_card("Total de departamentos", total_departamentos)
    with c3:
        render_metric_card("Total de páginas", total_paginas)
    with c4:
        render_metric_card("Última coleta", ultima_coleta)

    st.divider()
    render_section_title("Filtros")
    filtro_col1, filtro_col2 = st.columns([1, 1])
    with filtro_col1:
        departamentos = ["Todos"] + sorted(df["Departamento"].dropna().astype(str).unique().tolist())
        depto_sel = st.selectbox("Departamento", departamentos)
    with filtro_col2:
        busca_nome = st.text_input("Nome da impressora", placeholder="Ex.: CAC1")

    df_filtrado = df.copy()
    if depto_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Departamento"] == depto_sel]
    if busca_nome.strip():
        df_filtrado = df_filtrado[df_filtrado["Nome"].astype(str).str.contains(busca_nome.strip(), case=False, na=False)]

    if df_filtrado.empty:
        render_empty_state("Nenhum resultado para os filtros selecionados.")
        return

    render_section_title("Status operacional")
    status_counts = df_filtrado["Status"].value_counts(dropna=False).to_dict()
    s1, s2, s3 = st.columns(3)
    with s1:
        render_metric_card("ONLINE", status_counts.get("ONLINE", 0))
    with s2:
        render_metric_card("OFFLINE", status_counts.get("OFFLINE", 0))
    with s3:
        render_metric_card("SNMP BLOQUEADO", status_counts.get("SNMP BLOQUEADO", 0))

    col1, col2 = st.columns(2)
    with col1:
        render_section_title("Páginas por departamento")
        _plot_paginas_por_departamento(df_filtrado)
    with col2:
        render_section_title("Top impressoras")
        _plot_top_impressoras(df_filtrado)

    st.divider()
    render_section_title("Tabela consolidada")
    tabela = df_filtrado.sort_values(["Departamento", "Nome"]).reset_index(drop=True)
    st.dataframe(tabela, width="stretch")
