import asyncio
import logging
import os
from pathlib import Path

import pandas as pd
from telegram import Update
from telegram.ext import ContextTypes

from app.repositories.history_repository import load_long_df
from app.repositories.printers_repository import carregar_impressoras
from app.services.analytics_service import snapshot_ultima_leitura
from app.services.report_service import (
    gerar_pdf_por_departamento,
    gerar_pdf_por_impressora,
    gerar_pdf_todas,
)
from app.services.snmp_service import processar_atualizacao
from app.services.status_service import evaluate_fleet_status_sync
from app.telegram.keyboards import list_keyboard, menu_coleta_keyboard, menu_relatorio_keyboard

LOGGER = logging.getLogger(__name__)


def _admin_ids() -> set[int]:
    admins: set[int] = set()

    raw_list = os.getenv("TELEGRAM_ADMIN_IDS", "").strip()
    if raw_list:
        for part in raw_list.split(","):
            value = part.strip()
            if value.isdigit():
                admins.add(int(value))

    # Backward compatibility para configuracao antiga com um unico ID.
    raw_single = os.getenv("TELEGRAM_ADMIN_ID", "").strip()
    if raw_single.isdigit():
        admins.add(int(raw_single))

    return admins


def _from_user_id(update: Update) -> int | None:
    if update.effective_user:
        return update.effective_user.id
    return None


async def _deny_access(update: Update):
    if update.message:
        await update.message.reply_text("Acesso nao autorizado para este bot.")
    elif update.callback_query:
        await update.callback_query.answer("Acesso nao autorizado.", show_alert=True)


async def _authorized(update: Update, command_name: str = "") -> bool:
    user_id = _from_user_id(update)
    admins = _admin_ids()

    LOGGER.info("Update recebido | cmd=%s | user_id=%s | admin_ids=%s", command_name, user_id, sorted(admins))

    if not admins:
        return True
    if user_id in admins:
        return True

    await _deny_access(update)
    return False


def _format_help() -> str:
    return (
        "Comandos disponiveis:\n"
        "/start - Iniciar atendimento\n"
        "/status - Resumo ONLINE/OFFLINE/SNMP\n"
        "/coletar - Executar coleta SNMP\n"
        "/relatorio - Gerar relatorio PDF\n"
        "/impressoras - Listar impressoras cadastradas\n"
        "/meuid - Mostrar seu user id\n"
        "/ajuda - Exibir ajuda"
    )


def _snapshot_df():
    return snapshot_ultima_leitura(load_long_df())


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _authorized(update, "/start"):
        return
    await update.message.reply_text("Print Monitor Pro Bot ativo.\nUse /ajuda para ver os comandos.")


async def meuid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = _from_user_id(update)
    chat_id = update.effective_chat.id if update.effective_chat else None
    await update.message.reply_text(f"Seu user_id: {user_id}\nChat id atual: {chat_id}")


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _authorized(update, "/ajuda"):
        return
    await update.message.reply_text(_format_help())


async def printers_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _authorized(update, "/impressoras"):
        return

    impressoras = carregar_impressoras()
    if not impressoras:
        await update.message.reply_text("Nenhuma impressora cadastrada.")
        return

    linhas = [f"- {imp.get('nome', '')} | {imp.get('departamento', '')} | {imp.get('ip', '')}" for imp in impressoras]
    await update.message.reply_text("Impressoras cadastradas:\n" + "\n".join(linhas))


async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _authorized(update, "/status"):
        return

    impressoras = carregar_impressoras()
    if not impressoras:
        await update.message.reply_text("Nenhuma impressora cadastrada.")
        return

    status_rows = await asyncio.to_thread(evaluate_fleet_status_sync, impressoras)
    total = len(status_rows)
    online = sum(1 for r in status_rows if r["Status"] == "ONLINE")
    offline = sum(1 for r in status_rows if r["Status"] == "OFFLINE")
    snmp_block = sum(1 for r in status_rows if r["Status"] == "SNMP BLOQUEADO")

    resumo = (
        f"Status geral ({total} impressoras):\n"
        f"ONLINE: {online}\n"
        f"OFFLINE: {offline}\n"
        f"SNMP BLOQUEADO: {snmp_block}"
    )
    await update.message.reply_text(resumo)


async def coletar_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _authorized(update, "/coletar"):
        return
    await update.message.reply_text("Escolha o tipo de coleta:", reply_markup=menu_coleta_keyboard())


async def relatorio_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _authorized(update, "/relatorio"):
        return
    await update.message.reply_text("Escolha o tipo de relatorio:", reply_markup=menu_relatorio_keyboard())


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _authorized(update, "callback"):
        return

    query = update.callback_query
    await query.answer()
    data = query.data or ""

    if data == "noop":
        await query.edit_message_text("Sem opcoes disponiveis no momento.")
        return

    if data == "collect_all":
        await query.edit_message_text("Executando coleta de todas as impressoras...")
        ok, msg, falhas = await processar_atualizacao()
        extra = f"\nFalhas: {', '.join(f.get('nome', '?') for f in falhas)}" if falhas else ""
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"{msg}{extra}")
        return

    if data == "collect_one_menu":
        impressoras = carregar_impressoras()
        nomes = [imp.get("nome", "Sem nome") for imp in impressoras]
        await query.edit_message_text("Selecione a impressora:", reply_markup=list_keyboard(nomes, "collect_one"))
        return

    if data.startswith("collect_one:"):
        idx = int(data.split(":")[1])
        impressoras = carregar_impressoras()
        if idx >= len(impressoras):
            await query.edit_message_text("Impressora invalida.")
            return

        imp = impressoras[idx]
        await query.edit_message_text(f"Coletando dados de {imp.get('nome', '')}...")
        from app.config.config import OIDS_CONTADORES, OIDS_INFO
        from app.repositories.history_repository import append_long
        from app.services.snmp_service import coletar_impressora

        mapa_total = {**OIDS_INFO, **OIDS_CONTADORES}
        dados = await coletar_impressora(imp.get("ip", ""), mapa_total)

        if any(v is not None for v in dados.values()):
            agora = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            rows = [
                {
                    "Data": agora,
                    "Departamento": imp.get("departamento", ""),
                    "Nome": imp.get("nome", ""),
                    "IP": imp.get("ip", ""),
                    "Chave": chave,
                    "Valor": valor,
                }
                for chave, valor in dados.items()
            ]
            append_long(rows)
            linhas = [f"{k}: {v}" for k, v in dados.items()]
            mensagem = f"Coleta concluida para {imp.get('nome', '')}:\n" + "\n".join(linhas[:20])
        else:
            mensagem = f"Sem resposta SNMP de {imp.get('nome', '')}."
        await context.bot.send_message(chat_id=query.message.chat_id, text=mensagem)
        return

    if data == "report_all":
        await query.edit_message_text("Gerando relatorio consolidado...")
        piv_df = _snapshot_df()
        if piv_df.empty:
            await context.bot.send_message(chat_id=query.message.chat_id, text="Sem dados para relatorio.")
            return
        path_pdf = await asyncio.to_thread(gerar_pdf_todas, piv_df)
        await _send_pdf(context, query.message.chat_id, path_pdf, "Relatorio consolidado")
        return

    if data == "report_dept_menu":
        piv_df = _snapshot_df()
        if piv_df.empty:
            await query.edit_message_text("Sem dados para relatorio.")
            return
        depts = sorted(piv_df["Departamento"].dropna().unique().tolist())
        await query.edit_message_text(
            "Selecione o departamento:",
            reply_markup=list_keyboard([str(d) for d in depts], "report_dept"),
        )
        return

    if data == "report_printer_menu":
        piv_df = _snapshot_df()
        if piv_df.empty:
            await query.edit_message_text("Sem dados para relatorio.")
            return
        nomes = sorted(piv_df["Nome"].dropna().unique().tolist())
        await query.edit_message_text(
            "Selecione a impressora:",
            reply_markup=list_keyboard([str(n) for n in nomes], "report_printer"),
        )
        return

    if data.startswith("report_dept:"):
        idx = int(data.split(":")[1])
        piv_df = _snapshot_df()
        depts = sorted(piv_df["Departamento"].dropna().unique().tolist())
        if idx >= len(depts):
            await query.edit_message_text("Departamento invalido.")
            return
        depto = depts[idx]
        await query.edit_message_text(f"Gerando relatorio do departamento {depto}...")
        path_pdf = await asyncio.to_thread(gerar_pdf_por_departamento, piv_df, depto)
        await _send_pdf(context, query.message.chat_id, path_pdf, f"Relatorio do departamento {depto}")
        return

    if data.startswith("report_printer:"):
        idx = int(data.split(":")[1])
        piv_df = _snapshot_df()
        nomes = sorted(piv_df["Nome"].dropna().unique().tolist())
        if idx >= len(nomes):
            await query.edit_message_text("Impressora invalida.")
            return
        nome = nomes[idx]
        await query.edit_message_text(f"Gerando relatorio da impressora {nome}...")
        path_pdf = await asyncio.to_thread(gerar_pdf_por_impressora, piv_df, nome)
        await _send_pdf(context, query.message.chat_id, path_pdf, f"Relatorio da impressora {nome}")
        return

    await query.edit_message_text("Acao nao reconhecida.")


async def _send_pdf(context: ContextTypes.DEFAULT_TYPE, chat_id: int, path_pdf: str, caption: str):
    if not path_pdf or not os.path.exists(path_pdf):
        await context.bot.send_message(chat_id=chat_id, text="Falha ao gerar PDF.")
        return

    with open(path_pdf, "rb") as pdf_file:
        await context.bot.send_document(
            chat_id=chat_id,
            document=pdf_file,
            filename=Path(path_pdf).name,
            caption=caption,
        )
