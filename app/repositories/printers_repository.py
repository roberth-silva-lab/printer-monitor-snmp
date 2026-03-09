# app/repositories/printers_repository.py

import json
from typing import List, Dict

from app.config.config import ARQ_PRINTERS
from app.core.paths import ensure_base_dirs


def garantir_arquivo_impressoras() -> None:
    ensure_base_dirs()
    if not ARQ_PRINTERS.exists():
        ARQ_PRINTERS.write_text("[]", encoding="utf-8")


def carregar_impressoras() -> List[Dict]:
    garantir_arquivo_impressoras()

    try:
        with open(ARQ_PRINTERS, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def salvar_impressoras(lista: List[Dict]) -> None:
    ensure_base_dirs()
    with open(ARQ_PRINTERS, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)