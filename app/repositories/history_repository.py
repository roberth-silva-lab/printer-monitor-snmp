# app/repositories/history_repository.py

import csv
import pandas as pd

from app.config.config import ARQ_DADOS, CSV_COLUMNS
from app.core.paths import ensure_base_dirs


def garantir_arquivo_historico() -> None:
    ensure_base_dirs()

    if not ARQ_DADOS.exists():
        with open(ARQ_DADOS, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()


def append_long(rows: list[dict]) -> None:
    if not rows:
        return

    garantir_arquivo_historico()

    with open(ARQ_DADOS, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        for row in rows:
            writer.writerow(row)


def load_long_df() -> pd.DataFrame:
    garantir_arquivo_historico()

    try:
        df = pd.read_csv(ARQ_DADOS)

        rename_map = {
            "Dados": "Data",
            "data": "Data",
            "departamento": "Departamento",
            "nome": "Nome",
            "ip": "IP",
            "chave": "Chave",
            "valor": "Valor",
        }
        df = df.rename(columns=rename_map)

        colunas_obrigatorias = ["Data", "Departamento", "Nome", "IP", "Chave", "Valor"]
        faltando = [col for col in colunas_obrigatorias if col not in df.columns]

        if faltando:
            return pd.DataFrame(columns=CSV_COLUMNS)

        df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
        return df

    except Exception:
        return pd.DataFrame(columns=CSV_COLUMNS)