"""Printer selector — switch between configured printers."""
from __future__ import annotations

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import lang, printers, set_active_printer, active_printer_for
from lang import t
from helpers import auth_cb, btn, uid
import api


@auth_cb
async def cb_printers(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = uid(update)
    L = lang()

    all_printers = printers()
    current = active_printer_for(user_id)

    keyboard = []
    for p in all_printers:
        label = p["name"]
        if p["id"] == current["id"]:
            label = f"✅ {label}"
        keyboard.append([btn(label, f"printer:select:{p['id']}]")])

    keyboard.append([
        btn(t("printers.status_all", L), "printer:status_all"),
        btn(t("btn.back_menu", L), "menu:main"),
    ])

    await q.edit_message_text(
        t("printers.title", L),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


@auth_cb
async def cb_printer_select(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = uid(update)
    # Pattern: printer:select:<id>
    printer_id = int(q.data.split(":")[2].rstrip("]"))
    set_active_printer(user_id, printer_id)
    L = lang()

    await q.edit_message_text(
        t("printers.switched", L).format(name=active_printer_for(user_id)["name"]),
        reply_markup=InlineKeyboardMarkup([[btn(t("btn.back_menu", L), "menu:main")]]),
    )


@auth_cb
async def cb_printer_status_all(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show a quick status overview for all configured printers."""
    q = update.callback_query
    await q.answer()
    L = lang()

    all_printers = printers()
    lines = [f"{t('printers.status_all', L)}\n"]
    for p in all_printers:
        status = await api.printer_status(user_id=None)
        if status:
            ps = status.get("print_stats", {})
            state = ps.get("state", "?")
            progress = status.get("display_status", {}).get("progress", 0) * 100
            lines.append(f"• *{p['name']}*: {state} ({progress:.0f}%)")
        else:
            lines.append(f"• *{p['name']}*: offline")

    await q.edit_message_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup([[btn(t("btn.back_menu", L), "menu:main")]]),
        parse_mode=ParseMode.MARKDOWN,
    )
