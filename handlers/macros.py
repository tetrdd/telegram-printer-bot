"""Klipper macro discovery and runner with aliases, pagination, offline guard."""
from __future__ import annotations

import math
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import get as cfg, lang
from lang import t
from helpers import auth_cb, btn, uid, grid, offline_guard
import api


@auth_cb
async def cb_macros(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    L = lang()
    user_id = uid(update)

    if await offline_guard(q, user_id):
        return

    # Parse page from callback data: macros:page:N or menu:macros
    page = 0
    if q.data.startswith("macros:page:"):
        try:
            page = int(q.data.split(":")[2])
        except (IndexError, ValueError):
            page = 0

    objects = await api.printer_objects(user_id=user_id)
    macros = sorted([
        obj.replace("gcode_macro ", "")
        for obj in objects
        if obj.startswith("gcode_macro ") and not obj.startswith("gcode_macro _")
    ])

    if not macros:
        await q.edit_message_text(
            t("macros.empty", L),
            reply_markup=InlineKeyboardMarkup([[btn(t("btn.back_menu", L), "menu:main")]]),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Read config: aliases and per_page
    macro_cfg = cfg().get("macros", {})
    aliases = macro_cfg.get("aliases", {})
    per_page = macro_cfg.get("per_page", 8)

    total_pages = math.ceil(len(macros) / per_page)
    page = max(0, min(page, total_pages - 1))
    page_macros = macros[page * per_page : (page + 1) * per_page]

    # Build buttons using aliases when available
    buttons = []
    for m in page_macros:
        label = aliases.get(m, m)
        # Keep button label reasonably short
        if len(label) > 30:
            label = label[:27] + "..."
        buttons.append(btn(label, f"macro:run_ask:{m}"))

    kb = grid(buttons, cols=2)

    # Pagination navigation
    nav = []
    if page > 0:
        nav.append(btn(t("files.prev", L), f"macros:page:{page - 1}"))
    if page < total_pages - 1:
        nav.append(btn(t("files.next", L), f"macros:page:{page + 1}"))
    if nav:
        kb.append(nav)

    kb.append([btn(t("btn.back_menu", L), "menu:main")])

    if total_pages > 1:
        title = t("macros.page", L).format(
            page=page + 1, total=total_pages, count=len(macros)
        )
    else:
        title = t("macros.title", L).format(count=len(macros))

    await q.edit_message_text(
        title,
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_macro_ask(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    macro = q.data[len("macro:run_ask:"):]
    await q.answer()
    L = lang()

    # Get alias for display
    aliases = cfg().get("macros", {}).get("aliases", {})
    display_name = aliases.get(macro, macro)

    await q.edit_message_text(
        t("macros.run_confirm", L).format(name=display_name),
        reply_markup=InlineKeyboardMarkup([
            [btn(t("macros.run_btn", L), f"macro:run:{macro}"), btn(t("btn.cancel", L), "menu:macros")],
        ]),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_macro_run(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    macro = q.data[len("macro:run:"):]
    user_id = uid(update)

    r = await api.gcode(macro, user_id=user_id)
    await q.answer(f"{'✅' if r else '❌'} {macro}", show_alert=True)
    await cb_macros(update, ctx)
