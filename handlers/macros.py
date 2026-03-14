"""Klipper macro discovery and runner with aliases, pagination."""
from __future__ import annotations

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import lang, get as get_cfg
from lang import t
from helpers import auth_cb, btn, uid, offline_guard
import api

MACRO_PAGE_SIZE = 8


def _macro_display(name: str, aliases: dict[str, str]) -> str:
    return aliases.get(name, name.replace("_", " ").title())


async def _show_macros(q, user_id: int, page: int = 0):
    L = lang()
    cfg = get_cfg()
    aliases = cfg.get("macro_aliases", {})

    objects = await api.printer_objects(user_id=user_id)
    macros = sorted([
        o[len("gcode_macro "):]
        for o in objects
        if o.startswith("gcode_macro ")
        and not o[len("gcode_macro "):].startswith("_")
    ])

    total = len(macros)
    pages = max(1, (total + MACRO_PAGE_SIZE - 1) // MACRO_PAGE_SIZE)
    page = max(0, min(page, pages - 1))
    chunk = macros[page * MACRO_PAGE_SIZE: (page + 1) * MACRO_PAGE_SIZE]

    text = f"{t('macros.title', L)} ({total} {t('macros.found', L)}, {t('files.page', L)} {page+1}/{pages})"

    keyboard = []
    for macro in chunk:
        label = _macro_display(macro, aliases)
        keyboard.append([btn(label, f"macro:run_ask:{macro}")])

    nav = []
    if page > 0:
        nav.append(btn(t("btn.prev", L), f"macros:page:{page-1}"))
    if page < pages - 1:
        nav.append(btn(t("btn.next", L), f"macros:page:{page+1}"))
    if nav:
        keyboard.append(nav)

    keyboard.append([btn(t("btn.refresh", L), f"macros:page:{page}"), btn(t("btn.back_menu", L), "menu:main")])

    await q.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


@auth_cb
async def cb_macros(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = uid(update)
    page = int(q.data.split(":")[2]) if ":" in q.data else 0

    if await offline_guard(q, user_id):
        return

    await _show_macros(q, user_id, page=page)


@auth_cb
async def cb_macro_ask(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Ask for confirmation before running a macro."""
    q = update.callback_query
    await q.answer()
    user_id = uid(update)
    macro = q.data[len("macro:run_ask:"):]
    L = lang()
    cfg = get_cfg()
    aliases = cfg.get("macro_aliases", {})
    label = _macro_display(macro, aliases)

    keyboard = [
        [
            btn(t("macros.run_yes", L), f"macro:run:{macro}"),
            btn(t("macros.run_no", L), "macros:page:0"),
        ]
    ]
    await q.edit_message_text(
        t("macros.confirm", L).format(name=label),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


@auth_cb
async def cb_macro_run(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Run a macro."""
    q = update.callback_query
    await q.answer()
    user_id = uid(update)
    macro = q.data[len("macro:run:"):]
    L = lang()

    result = await api.gcode(macro, user_id=user_id)
    cfg = get_cfg()
    aliases = cfg.get("macro_aliases", {})
    label = _macro_display(macro, aliases)

    text = (
        t("macros.ran", L).format(name=label)
        if result
        else t("macros.failed", L).format(name=label)
    )
    keyboard = [[btn(t("btn.back_menu", L), "menu:main")]]
    await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
