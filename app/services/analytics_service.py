import pandas as pd

COUNTER_COLUMN = "Impressora :: Contagem total de páginas do mecanismo"
LEGACY_COUNTER_COLUMN = "Impressora :: Contagem total de pÃ¡ginas do mecanismo"
LEGACY_SYS_DESCR_COLUMN = "Info :: sysDescr (modelo/firmware)"


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        LEGACY_COUNTER_COLUMN: COUNTER_COLUMN,
    }
    return df.rename(columns=rename_map)


def snapshot_ultima_leitura(df_long: pd.DataFrame) -> pd.DataFrame:
    if df_long is None or df_long.empty:
        return pd.DataFrame()

    colunas_obrigatorias = ["Data", "Departamento", "Nome", "IP", "Chave", "Valor"]
    for col in colunas_obrigatorias:
        if col not in df_long.columns:
            return pd.DataFrame()

    df = df_long.copy()
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df = df.dropna(subset=["Data"])
    if df.empty:
        return pd.DataFrame()

    d = df.sort_values("Data").groupby(["Nome", "Chave"], as_index=False).tail(1)
    piv = d.pivot_table(
        index=["Departamento", "Nome", "IP"],
        columns="Chave",
        values="Valor",
        aggfunc="first",
    ).reset_index()

    piv.columns.name = None
    piv = _normalize_columns(piv)
    return piv
