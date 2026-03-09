from app.core.paths import DATA_DIR, PDF_ASSETS_DIR

# SNMP
COMMUNITY = "public"
PORT = 161
TIMEOUT = 4
RETRIES = 2

# Arquivos
ARQ_PRINTERS = DATA_DIR / "impressoras_config.json"
ARQ_DADOS = DATA_DIR / "historico_bilhetagem_long.csv"

# Assets PDF
HP_LOGO_LOCAL = PDF_ASSETS_DIR / "hp_logo.png"

# OIDs básicos
OIDS_INFO = {
    "Info :: sysDescr (modelo/firmware)": "1.3.6.1.2.1.1.1.0",
    "Info :: sysName": "1.3.6.1.2.1.1.5.0",
    "Info :: sysUpTime": "1.3.6.1.2.1.1.3.0",
}

OIDS_CONTADORES = {
    "Impressora :: Contagem total de páginas do mecanismo": "1.3.6.1.2.1.43.10.2.1.4.1.1",
}

CSV_COLUMNS = ["Data", "Departamento", "Nome", "IP", "Chave", "Valor"]
