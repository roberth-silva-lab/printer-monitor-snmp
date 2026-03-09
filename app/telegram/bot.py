import atexit
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram.error import Conflict
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from app.core.paths import ensure_base_dirs
from app.telegram.handlers import (
    callback_handler,
    coletar_handler,
    help_handler,
    meuid_handler,
    printers_handler,
    relatorio_handler,
    start_handler,
    status_handler,
)

LOGGER = logging.getLogger(__name__)
LOCK_FILE = Path(".telegram_bot.lock")


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def _load_project_env() -> None:
    project_root = Path(__file__).resolve().parents[2]
    env_path = project_root / ".env"
    load_dotenv(dotenv_path=env_path, override=False)


def _resolve_telegram_token() -> str:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if token:
        return token
    return os.getenv("\ufeffTELEGRAM_BOT_TOKEN", "").strip()


def _acquire_lock() -> None:
    try:
        LOCK_FILE.write_text(str(os.getpid()), encoding="utf-8", newline="\n")
    except Exception as exc:
        raise RuntimeError(f"Falha ao criar lock local do bot: {exc}") from exc


def _release_lock() -> None:
    try:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
    except Exception:
        pass


def _is_pid_running(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _handle_stale_lock() -> None:
    if not LOCK_FILE.exists():
        return

    try:
        raw = LOCK_FILE.read_text(encoding="utf-8").strip()
        old_pid = int(raw) if raw.isdigit() else -1
    except Exception:
        old_pid = -1

    if not _is_pid_running(old_pid):
        _release_lock()


async def _error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    err = context.error
    if isinstance(err, Conflict):
        LOGGER.error(
            "Conflito com outro processo usando o mesmo bot/token. "
            "Pare a outra instancia e execute novamente."
        )
        context.application.stop_running()
        return

    LOGGER.exception("Erro nao tratado no bot", exc_info=err)


def build_application(token: str) -> Application:
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("ajuda", help_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("meuid", meuid_handler))
    app.add_handler(CommandHandler("status", status_handler))
    app.add_handler(CommandHandler("coletar", coletar_handler))
    app.add_handler(CommandHandler("relatorio", relatorio_handler))
    app.add_handler(CommandHandler("impressoras", printers_handler))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_error_handler(_error_handler)
    return app


def main() -> None:
    _configure_logging()
    ensure_base_dirs()
    _load_project_env()

    token = _resolve_telegram_token()
    if not token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN nao definido. Configure no .env "
            "ou como variavel de ambiente do sistema."
        )

    _handle_stale_lock()
    if LOCK_FILE.exists():
        raise RuntimeError(
            "Ja existe uma instancia local do bot em execucao. "
            "Feche a outra janela/processo e tente novamente."
        )

    _acquire_lock()
    atexit.register(_release_lock)

    application = build_application(token)
    try:
        application.run_polling(allowed_updates=["message", "callback_query"])
    except Conflict as exc:
        raise RuntimeError(
            "Conflito com outra instancia do bot (getUpdates). "
            "Garanta que apenas um processo esteja rodando."
        ) from exc
    finally:
        _release_lock()


if __name__ == "__main__":
    main()
