"""GCode quick button management — add or remove custom GCode buttons for the console."""
from __future__ import annotations

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from config import get as cfg, save as save_cfg, lang
from lang import t
from helpers import auth_cb, auth, btn, uid
import api

GCODE_BUTTON_INPUT = 500


@auth_cb
async def cb_settings_gcode(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    L = lang()
    c = cfg()
    buttons = c.get("gcode", {}).get("buttons", [])

    kb = []
    for i, b in enumerate(buttons):
        kb.append([btn(f"{b['label']} : {b['cmd']}", f"gcode_btn_edit:{i}")])

    kb.append([btn(t("settings.gcode.add_button", L), "gcode_btn_add")])
    kb.append([btn(t("btn.back_menu", L), "menu:settings")])

    await q.edit_message_text(
        t("settings.gcode.title", L),
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_gcode_btn_edit_ask(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    idx = int(q.data[len("gcode_btn_edit:"):])
    await q.answer()
    L = lang()

    ctx.user_data["editing_gcode_btn"] = {"idx": idx}

    await q.edit_message_text(
        t("settings.gcode.edit_button", L),
        reply_markup=InlineKeyboardMarkup([
            [btn("🗑️", f"gcode_btn_del:{idx}"), btn(t("btn.cancel", L), "gcode_btn_cancel")],
        ]),
        parse_mode=ParseMode.MARKDOWN,
    )
    return ConversationHandler.END


@auth_cb
async def cb_gcode_btn_del(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    idx = int(q.data[len("gcode_btn_del:"):])
    c = cfg()
    buttons = c.setdefault("gcode", {}).setdefault("buttons", [])
    if 0 <= idx < len(buttons):
        del buttons[idx]
    save_cfg()
    await q.answer("🗑️")
    ctx.user_data.pop("editing_gcode_btn", None)
    update.callback_query.data = "set_cat:gcode"
    await cb_settings_gcode(update, ctx)
    return ConversationHandler.END


@auth_cb
async def cb_gcode_btn_add_ask(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    L = lang()

    ctx.user_data["editing_gcode_btn"] = {"new": True}

    await q.edit_message_text(
        t("settings.gcode.prompt_label", L),
        reply_markup=InlineKeyboardMarkup([[btn(t("btn.cancel", L), "gcode_btn_cancel")]]),
        parse_mode=ParseMode.MARKDOWN,
    )
    return GCODE_BUTTON_INPUT


@auth_cb
async def cb_gcode_btn_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    ctx.user_data.pop("editing_gcode_btn", None)
    update.callback_query.data = "set_cat:gcode"
    await cb_settings_gcode(update, ctx)
    return ConversationHandler.END


@auth
async def handle_gcode_button_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    data = ctx.user_data.get("editing_gcode_btn")
    if not data:
        return ConversationHandler.END

    L = lang()

    if "label" not in data:
        # We got the label, now ask for command
        ctx.user_data["editing_gcode_btn"]["label"] = text
        await update.message.reply_text(
            t("settings.gcode.prompt_cmd", L).format(label=text),
            reply_markup=InlineKeyboardMarkup([[btn(t("btn.cancel", L), "gcode_btn_cancel")]]),
            parse_mode=ParseMode.MARKDOWN,
        )
        return GCODE_BUTTON_INPUT
    else:
        # We got the command
        label = data["label"]
        cmd = text
        c = cfg()
        buttons = c.setdefault("gcode", {}).setdefault("buttons", [])
        buttons.append({"label": label, "cmd": cmd})
        save_cfg()

        await update.message.reply_text(
            t("generic.done", L),
            reply_markup=InlineKeyboardMarkup([[btn(t("btn.back_menu", L), "set_cat:gcode")]]),
        )
        return ConversationHandler.END
