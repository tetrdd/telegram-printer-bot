"""Klipper macro discovery and runner."""

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import lang
from lang import t
from helpers import auth_cb, btn, uid, grid
import api


@auth_cb
async def cb_macros(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    L = lang()
    user_id = uid(update)

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

    buttons = [btn(f"⚡ {m}", f"macro:run_ask:{m}") for m in macros[:30]]
    kb = grid(buttons, cols=2)
    kb.append([btn(t("btn.back_menu", L), "menu:main")])

    await q.edit_message_text(
        t("macros.title", L).format(count=len(macros)),
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_macro_ask(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    macro = q.data[len("macro:run_ask:"):]
    await q.answer()
    L = lang()

    await q.edit_message_text(
        t("macros.run_confirm", L).format(name=macro),
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
