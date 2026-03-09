from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def menu_coleta_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Coletar todas", callback_data="collect_all")],
            [InlineKeyboardButton("Coletar uma", callback_data="collect_one_menu")],
        ]
    )


def menu_relatorio_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Uma impressora", callback_data="report_printer_menu")],
            [InlineKeyboardButton("Um departamento", callback_data="report_dept_menu")],
            [InlineKeyboardButton("Todas as impressoras", callback_data="report_all")],
        ]
    )


def list_keyboard(items: list[str], prefix: str, chunk_size: int = 2) -> InlineKeyboardMarkup:
    rows = []
    for idx in range(0, len(items), chunk_size):
        row_items = items[idx: idx + chunk_size]
        rows.append(
            [
                InlineKeyboardButton(text=name[:28], callback_data=f"{prefix}:{idx + offset}")
                for offset, name in enumerate(row_items)
            ]
        )
    return InlineKeyboardMarkup(rows if rows else [[InlineKeyboardButton("Sem opções", callback_data="noop")]])
