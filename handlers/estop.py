"""Emergency stop handler."""
from __future__ import annotations

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import lang
from lang import t
from helpers import auth_cb, btn, uid
import api


@auth_cb
async def cb_estop(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    L = lang()
    keyboard = [
        [
            btn(t("estop.confirm_yes", L), "estop:confirm"),
            btn(t("estop.confirm_no", L), "menu:main"),
        ]
    ]
    await q.edit_message_text(
        t("estop.confirm", L),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


@auth_cb
async def cb_estop_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer(t("estop.executing", lang()), show_alert=True)
    user_id = uid(update)
    await api.emergency_stop(user_id=user_id)
    L = lang()
    keyboard = [[btn(t("btn.back_menu", L), "menu:main")]]
    await q.edit_message_text(
        t("estop.done", L),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
