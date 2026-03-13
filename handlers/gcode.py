"""GCode console — quick buttons + free text input."""

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from config import lang
from lang import t
from helpers import auth, auth_cb, btn, uid, offline_guard
import api

GCODE_INPUT = 200


@auth_cb
async def cb_gcode_entry(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = uid(update)
    L = lang()

    if await offline_guard(q, user_id):
        return GCODE_INPUT

    quick = [
        [btn("G28 Home", "gcode_quick:G28"), btn("G90 Absolute", "gcode_quick:G90")],
        [btn("G91 Relative", "gcode_quick:G91"), btn("M84 Motors Off", "gcode_quick:M84")],
        [btn("M106 S255 Fan 100%", "gcode_quick:M106 S255")],
        [btn("M107 Fan Off", "gcode_quick:M107")],
        [btn(t("btn.back_menu", L), "menu:main")],
    ]

    await q.edit_message_text(
        t("gcode.title", L),
        reply_markup=InlineKeyboardMarkup(quick),
        parse_mode=ParseMode.MARKDOWN,
    )
    return GCODE_INPUT


@auth_cb
async def cb_gcode_quick(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    cmd = q.data[len("gcode_quick:"):]
    user_id = uid(update)
    r = await api.gcode(cmd, user_id=user_id)
    await q.answer(f"{'\u2713' if r else '\u2717'} {cmd}", show_alert=True)


@auth
async def handle_gcode_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cmd = update.message.text.strip()
    L = lang()
    user_id = uid(update)
    r = await api.gcode(cmd, user_id=user_id)

    if r:
        text = t("gcode.ok", L).format(cmd=cmd)
    else:
        text = t("gcode.fail", L).format(cmd=cmd)

    await update.message.reply_text(
        f"{text}\n\n{t('gcode.another', L)}",
        reply_markup=InlineKeyboardMarkup([[btn(t("btn.back_menu", L), "menu:main")]]),
        parse_mode=ParseMode.MARKDOWN,
    )
    return GCODE_INPUT


async def cancel_gcode(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    from handlers.menu import cmd_start
    await cmd_start(update, ctx)
    return ConversationHandler.END
