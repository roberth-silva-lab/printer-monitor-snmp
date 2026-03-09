import os

import pandas as pd
import streamlit as st

from app.services.report_service import (
    gerar_excel_snapshot,
    gerar_pdf_por_departamento,
    gerar_pdf_por_impressora,
    gerar_pdf_todas,
    gerar_zip_por_departamento,
    gerar_zip_por_impressora,
    obter_nome_arquivo,
)
from app.ui.components import render_empty_state, render_page_header, render_section_title


def _download_file_button(path_file: str, label: str, mime: str):
    if not path_file or not os.path.exists(path_file):
        st.error("Arquivo não foi gerado.")
        return

    with open(path_file, "rb") as f:
        st.download_button(
            label=label,
            data=f.read(),
            file_name=obter_nome_arquivo(path_file),
            mime=mime,
        )


def render(piv_df: pd.DataFrame):
    render_page_header(
        "Relatórios e Exportações",
        "Geração de PDF consolidado, por agrupamento e exportação para Excel.",
        "📄",
    )

    if piv_df is None or piv_df.empty:
        render_empty_state("Nenhum dado disponível para relatório.")
        return

    modo = st.radio(
        "Tipo de relatório",
        options=[
            "Uma impressora",
            "Um departamento",
            "Todas as impressoras",
            "Separado por departamento (ZIP)",
            "Separado por impressora (ZIP)",
            "Exportar para Excel",
        ],
    )

    st.divider()

    if modo == "Uma impressora":
        render_section_title("Relatório por impressora")
        nomes = sorted(piv_df["Nome"].dropna().unique().tolist())
        nome = st.selectbox("Escolha a impressora", nomes)

        if st.button("Gerar PDF da impressora", type="primary"):
            path_pdf = gerar_pdf_por_impressora(piv_df, nome)
            st.success("PDF gerado com sucesso.")
            _download_file_button(path_pdf, "Baixar PDF", "application/pdf")

    elif modo == "Um departamento":
        render_section_title("Relatório por departamento")
        departamentos = sorted(piv_df["Departamento"].dropna().unique().tolist())
        depto = st.selectbox("Escolha o departamento", departamentos)

        if st.button("Gerar PDF do departamento", type="primary"):
            path_pdf = gerar_pdf_por_departamento(piv_df, depto)
            st.success("PDF gerado com sucesso.")
            _download_file_button(path_pdf, "Baixar PDF", "application/pdf")

    elif modo == "Todas as impressoras":
        render_section_title("Relatório consolidado")
        st.write("Gera um único PDF com todas as impressoras da última leitura.")

        if st.button("Gerar PDF consolidado", type="primary"):
            path_pdf = gerar_pdf_todas(piv_df)
            st.success("PDF gerado com sucesso.")
            _download_file_button(path_pdf, "Baixar PDF consolidado", "application/pdf")

    elif modo == "Separado por departamento (ZIP)":
        render_section_title("ZIP por departamento")
        st.write("Cria um PDF por departamento e compacta em um arquivo ZIP.")

        if st.button("Gerar ZIP por departamento", type="primary"):
            zip_name, zip_bytes = gerar_zip_por_departamento(piv_df)
            st.success("ZIP gerado com sucesso.")
            st.download_button(
                label="Baixar ZIP",
                data=zip_bytes,
                file_name=zip_name,
                mime="application/zip",
            )

    elif modo == "Separado por impressora (ZIP)":
        render_section_title("ZIP por impressora")
        st.write("Cria um PDF por impressora e compacta em um arquivo ZIP.")

        if st.button("Gerar ZIP por impressora", type="primary"):
            zip_name, zip_bytes = gerar_zip_por_impressora(piv_df)
            st.success("ZIP gerado com sucesso.")
            st.download_button(
                label="Baixar ZIP",
                data=zip_bytes,
                file_name=zip_name,
                mime="application/zip",
            )

    elif modo == "Exportar para Excel":
        render_section_title("Exportação para Excel")
        st.write("Exporta a visão consolidada da última leitura para arquivo XLSX.")

        if st.button("Gerar Excel", type="primary"):
            path_excel = gerar_excel_snapshot(piv_df)
            st.success("Arquivo Excel gerado com sucesso.")
            _download_file_button(
                path_excel,
                "Baixar Excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
