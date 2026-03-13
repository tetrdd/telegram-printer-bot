"""Emergency stop handler."""

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import get as cfg, lang
from lang import t
from helpers import auth_cb, btn
import api


@auth_cb
async def cb_estop(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    L = lang()

    if cfg().get("safety", {}).get("emergency_stop_confirm", True):
        await q.edit_message_text(
            t("estop.confirm", L),
            reply_markup=InlineKeyboardMarkup([
                [btn(t("estop.yes", L), "estop:confirm")],
                [btn(t("btn.cancel", L), "menu:main")],
            ]),
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        ok = await api.emergency_stop()
        if ok:
            await q.edit_message_text(
                t("estop.done", L),
                reply_markup=InlineKeyboardMarkup([
                    [btn(t("system.fw_restart", L), "sys:fw_restart")],
                    [btn(t("btn.back_menu", L), "menu:main")],
                ]),
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await q.edit_message_text(
                t("estop.failed", L),
                reply_markup=InlineKeyboardMarkup([[btn(t("btn.back_menu", L), "menu:main")]]),
            )


@auth_cb
async def cb_estop_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    L = lang()

    ok = await api.emergency_stop()
    if ok:
        await q.answer("🚨", show_alert=True)
        await q.edit_message_text(
            t("estop.done", L),
            reply_markup=InlineKeyboardMarkup([
                [btn(t("system.fw_restart", L), "sys:fw_restart")],
                [btn(t("btn.back_menu", L), "menu:main")],
            ]),
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await q.answer(t("estop.failed", L), show_alert=True)
        from handlers.menu import show_menu
        await show_menu(q)
