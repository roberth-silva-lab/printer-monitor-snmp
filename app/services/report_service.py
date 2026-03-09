from datetime import datetime
from pathlib import Path

import pandas as pd

from app.core.paths import EXPORTS_DIR
from app.pdf.pdf_generator import gerar_pdf_snapshot, zip_files


def _slugify(value: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in ("_", "-") else "_" for ch in (value or "").strip())
    safe = "_".join(part for part in safe.split("_") if part)
    return safe or "geral"


def _agora_tag() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def gerar_nome_arquivo(prefixo: str, sufixo: str = "", extensao: str = "pdf") -> str:
    sufixo_limpo = _slugify(sufixo) if sufixo else ""
    ts = _agora_tag()
    if sufixo_limpo:
        return f"{prefixo}_{sufixo_limpo}_{ts}.{extensao}"
    return f"{prefixo}_{ts}.{extensao}"


def _build_export_path(filename: str) -> str:
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return str(EXPORTS_DIR / filename)


def _build_pdf_path(prefixo: str, sufixo: str, titulo: str, df: pd.DataFrame) -> str:
    filename = gerar_nome_arquivo(prefixo, sufixo, "pdf")
    output = _build_export_path(filename)
    gerar_pdf_snapshot(output, titulo, df)
    return output


def gerar_pdf_por_impressora(piv_df: pd.DataFrame, nome_impressora: str) -> str:
    df_sel = piv_df[piv_df["Nome"] == nome_impressora].copy()
    return _build_pdf_path(
        "Relatorio_Impressora",
        nome_impressora,
        f"Relatorio - Impressora {nome_impressora}",
        df_sel,
    )


def gerar_pdf_por_departamento(piv_df: pd.DataFrame, departamento: str) -> str:
    df_sel = piv_df[piv_df["Departamento"] == departamento].copy()
    return _build_pdf_path(
        "Relatorio_Departamento",
        departamento,
        f"Relatorio - Departamento {departamento}",
        df_sel,
    )


def gerar_pdf_todas(piv_df: pd.DataFrame) -> str:
    return _build_pdf_path(
        "Relatorio_Consolidado",
        "todas_impressoras",
        "Relatorio Consolidado - Todas as impressoras",
        piv_df.copy(),
    )


def gerar_excel_snapshot(piv_df: pd.DataFrame, prefixo: str = "Exportacao_Consolidada") -> str:
    filename = gerar_nome_arquivo(prefixo, "dados", "xlsx")
    output = _build_export_path(filename)

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        piv_df.to_excel(writer, index=False, sheet_name="snapshot")
        workbook = writer.book
        worksheet = writer.sheets["snapshot"]
        worksheet.autofilter(0, 0, max(len(piv_df), 1), max(len(piv_df.columns) - 1, 0))

        header_format = workbook.add_format({"bold": True, "bg_color": "#1F2937", "font_color": "#FFFFFF"})
        for idx, col in enumerate(piv_df.columns):
            worksheet.write(0, idx, col, header_format)
            best_width = max(14, min(42, len(str(col)) + 3))
            worksheet.set_column(idx, idx, best_width)

    return output


def _zip_from_paths(prefixo: str, filepaths: list[str]) -> tuple[str, bytes]:
    filename = gerar_nome_arquivo(prefixo, "", "zip")
    return filename, zip_files(filepaths)


def gerar_zip_por_departamento(piv_df: pd.DataFrame) -> tuple[str, bytes]:
    pdfs = []
    for depto in sorted(piv_df["Departamento"].dropna().unique().tolist()):
        df_sel = piv_df[piv_df["Departamento"] == depto].copy()
        pdfs.append(
            _build_pdf_path(
                "Relatorio_Departamento",
                depto,
                f"Relatorio - Departamento {depto}",
                df_sel,
            )
        )

    return _zip_from_paths("Relatorios_Departamentos", pdfs)


def gerar_zip_por_impressora(piv_df: pd.DataFrame) -> tuple[str, bytes]:
    pdfs = []
    for nome in sorted(piv_df["Nome"].dropna().unique().tolist()):
        df_sel = piv_df[piv_df["Nome"] == nome].copy()
        pdfs.append(
            _build_pdf_path(
                "Relatorio_Impressora",
                nome,
                f"Relatorio - Impressora {nome}",
                df_sel,
            )
        )

    return _zip_from_paths("Relatorios_Impressoras", pdfs)


def obter_nome_arquivo(path: str) -> str:
    return Path(path).name
