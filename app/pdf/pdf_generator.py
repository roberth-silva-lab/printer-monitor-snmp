import os
from datetime import datetime
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

import pandas as pd
from fpdf import FPDF

from app.config.config import HP_LOGO_LOCAL
from app.core.utils import pdf_safe


COL_MAP = {
    "Departamento": "Departamento",
    "Nome": "Impressora",
    "IP": "IP",
    "Status": "Status",
    "Impressora :: Contagem total de páginas do mecanismo": "Contador total",
    "Info :: sysDescr (modelo/firmware)": "Modelo/Firmware",
    "Info :: sysName": "SysName",
    "Info :: sysUpTime": "Uptime",
}


class PDFRelatorio(FPDF):
    def __init__(self, title: str = "Relatorio de Utilizacao", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._title = title
        self._generated_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def header(self):
        logo_path = str(HP_LOGO_LOCAL)

        if logo_path and os.path.exists(logo_path):
            try:
                self.image(logo_path, 10, 7, 14)
            except Exception:
                pass

        self.set_fill_color(240, 244, 248)
        self.set_draw_color(220, 226, 232)
        self.rect(8, 6, 194, 20, style="DF")

        self.set_xy(28, 9)
        self.set_font("Arial", "B", 13)
        self.cell(0, 6, pdf_safe(self._title), new_x="LMARGIN", new_y="NEXT")

        self.set_x(28)
        self.set_font("Arial", "", 9)
        self.cell(0, 5, pdf_safe(f"Gerado em: {self._generated_at}"), new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def footer(self):
        self.set_y(-12)
        self.set_draw_color(220, 226, 232)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.set_font("Arial", "I", 8)
        self.cell(0, 8, f"Pagina {self.page_no()}", align="C")


def _cell_kpi(pdf: FPDF, label: str, value: str):
    x, y = pdf.get_x(), pdf.get_y()
    width, height = 45, 18

    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rect(x, y, width, height, style="DF")

    pdf.set_xy(x + 2, y + 3)
    pdf.set_font("Arial", "", 8)
    pdf.cell(width - 4, 4, pdf_safe(label), new_x="LMARGIN", new_y="NEXT")

    pdf.set_x(x + 2)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(width - 4, 7, pdf_safe(value), new_x="LMARGIN", new_y="NEXT")

    pdf.set_xy(x + width + 3, y)


def _draw_executive_summary(pdf: FPDF, titulo: str, df_snapshot: pd.DataFrame):
    total_registros = len(df_snapshot) if df_snapshot is not None else 0
    total_dept = (
        int(df_snapshot["Departamento"].nunique())
        if df_snapshot is not None and not df_snapshot.empty and "Departamento" in df_snapshot.columns
        else 0
    )
    total_impressoras = (
        int(df_snapshot["Nome"].nunique())
        if df_snapshot is not None and not df_snapshot.empty and "Nome" in df_snapshot.columns
        else 0
    )
    total_paginas = 0
    contador_col = "Impressora :: Contagem total de páginas do mecanismo"
    if df_snapshot is not None and not df_snapshot.empty and contador_col in df_snapshot.columns:
        total_paginas = int(pd.to_numeric(df_snapshot[contador_col], errors="coerce").fillna(0).sum())

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 9, "Resumo executivo", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(0, 5, pdf_safe(f"Escopo: {titulo}"))
    pdf.ln(1)

    _cell_kpi(pdf, "Registros", str(total_registros))
    _cell_kpi(pdf, "Impressoras", str(total_impressoras))
    _cell_kpi(pdf, "Departamentos", str(total_dept))
    _cell_kpi(pdf, "Paginas totais", str(total_paginas))
    pdf.ln(20)


def _draw_label_value(pdf: FPDF, label: str, value: str):
    page_width = pdf.w - pdf.l_margin - pdf.r_margin
    label_w = 58
    value_w = page_width - label_w

    if pdf.get_y() > 265:
        pdf.add_page()

    pdf.set_font("Arial", "B", 9)
    pdf.set_fill_color(246, 248, 251)
    pdf.multi_cell(label_w, 7, pdf_safe(label), border=1, fill=True, new_x="RIGHT", new_y="TOP")

    x = pdf.get_x()
    y = pdf.get_y()
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(value_w, 7, pdf_safe(value), border=1, new_x="LMARGIN", new_y="NEXT")
    if pdf.get_y() < y + 7:
        pdf.set_y(y + 7)
    pdf.set_x(pdf.l_margin)


def _draw_printer_block(pdf: FPDF, index: int, row: pd.Series, colunas_final: list[str]):
    if pdf.get_y() > 240:
        pdf.add_page()

    nome_imp = str(row.get("Nome", f"Impressora {index}")).strip() or f"Impressora {index}"
    depto = str(row.get("Departamento", "")).strip()
    status = str(row.get("Status", "")).strip()

    pdf.set_fill_color(238, 243, 249)
    pdf.set_draw_color(215, 223, 232)
    pdf.rect(pdf.l_margin, pdf.get_y(), 190, 10, style="DF")
    pdf.set_font("Arial", "B", 11)
    title = f"{index}. {nome_imp}"
    if depto:
        title += f" | {depto}"
    if status:
        title += f" | {status}"
    pdf.set_x(pdf.l_margin + 2)
    pdf.cell(186, 10, pdf_safe(title), new_x="LMARGIN", new_y="NEXT")

    for col in colunas_final:
        label = COL_MAP.get(col, col)
        valor = str(row.get(col, ""))
        _draw_label_value(pdf, label, valor)

    pdf.ln(2)


def pdf_blocos_impressoras(pdf: FPDF, df: pd.DataFrame):
    if df is None or df.empty:
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 8, "Nenhum dado encontrado para este relatorio.")
        return

    df = df.copy().fillna("")
    colunas_ordem = [
        "Departamento",
        "Nome",
        "IP",
        "Status",
        "Impressora :: Contagem total de páginas do mecanismo",
        "Info :: sysDescr (modelo/firmware)",
        "Info :: sysName",
        "Info :: sysUpTime",
    ]
    colunas_existentes = [c for c in colunas_ordem if c in df.columns]
    outras_colunas = [c for c in df.columns if c not in colunas_existentes]
    colunas_final = colunas_existentes + outras_colunas

    for idx, (_, row) in enumerate(df.iterrows(), start=1):
        _draw_printer_block(pdf, idx, row, colunas_final)


def gerar_pdf_snapshot(output_path: str, titulo: str, df_snapshot: pd.DataFrame):
    pdf = PDFRelatorio(title=titulo, orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()

    _draw_executive_summary(pdf, titulo, df_snapshot)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Detalhamento por impressora", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    pdf_blocos_impressoras(pdf, df_snapshot)
    pdf.output(output_path)


def zip_files(filepaths: list[str]) -> bytes:
    mem = BytesIO()
    with ZipFile(mem, mode="w", compression=ZIP_DEFLATED) as zf:
        for fp in filepaths:
            if fp and os.path.exists(fp):
                zf.write(fp, arcname=os.path.basename(fp))
    mem.seek(0)
    return mem.getvalue()
