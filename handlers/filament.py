"""Filament change helper — Unload -> Wait -> Load wizard."""
from __future__ import annotations

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import get as cfg, lang
from lang import t
from helpers import auth_cb, btn, uid, offline_guard
import api


@auth_cb
async def cb_filament_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    L = lang()
    user_id = uid(update)

    if await offline_guard(q, user_id):
        return

    kb = [
        [btn(t("filament.unload", L), "filament:action:unload"), btn(t("filament.load", L), "filament:action:load")],
        [btn(t("btn.back_menu", L), "menu:main")],
    ]
    await q.edit_message_text(
        t("filament.title", L),
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_filament_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    action = q.data[len("filament:action:"):]
    user_id = uid(update)
    L = lang()

    # Simple logic for now: Heat to 200 and then run the command
    temp = 200
    if action == "unload":
        cmd = "UNLOAD_FILAMENT"
    else:
        cmd = "LOAD_FILAMENT"

    await q.answer(t("filament.heating", L).format(temp=temp))

    # We could do this in background or using a sequence of API calls
    # For now, let's just send the GCode (assuming the macro handles the heating or just runs)
    # Most Klipper users have these macros
    r = await api.gcode(f"M109 S{temp}\n{cmd}", user_id=user_id)

    if r:
        await q.answer(t("filament.done", L), show_alert=True)
    else:
        await q.answer(t("generic.failed", L), show_alert=True)

    await cb_filament_menu(update, ctx)
