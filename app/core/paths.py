# app/core/paths.py

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PDF_DIR = BASE_DIR / "pdf"
PDF_ASSETS_DIR = PDF_DIR / "assets"
EXPORTS_DIR = BASE_DIR / "exports"

def ensure_base_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    PDF_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
