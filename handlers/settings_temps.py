"""Temperature preset management settings — add, edit, or remove hotend and bed presets."""
from __future__ import annotations

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from config import get as cfg, save as save_cfg, lang
from lang import t
from helpers import auth_cb, auth, btn, uid
import api

TEMP_VALUE_INPUT = 400


@auth_cb
async def cb_settings_temps(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    L = lang()
    kb = [
        [btn(t("settings.temps.hotend", L), "set_temps:hotend")],
        [btn(t("settings.temps.bed", L), "set_temps:bed")],
        [btn(t("btn.back_menu", L), "menu:settings")],
    ]
    await q.edit_message_text(
        t("settings.temps.title", L),
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_temp_presets_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    category = q.data[len("set_temps:"):]
    await q.answer()
    L = lang()
    c = cfg()
    presets = c.get("temp_presets", {}).get(category, {})

    kb = []
    for name, val in presets.items():
        kb.append([btn(f"{name}: {val}°C", f"temp_preset_edit:{category}:{name}")])

    kb.append([btn(t("settings.temps.add_preset", L), f"temp_preset_add:{category}")])
    kb.append([btn(t("btn.back_menu", L), "set_cat:temps")])

    title = t(f"settings.temps.{category}", L)
    await q.edit_message_text(
        f"*{title}*",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_temp_preset_edit_ask(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    _, category, name = q.data.split(":")
    await q.answer()
    L = lang()

    ctx.user_data["editing_temp"] = {"cat": category, "name": name}

    await q.edit_message_text(
        t("settings.temps.prompt_val", L).format(name=name),
        reply_markup=InlineKeyboardMarkup([
            [btn(t("btn.cancel", L), "temp_preset_cancel"), btn("🗑️", f"temp_preset_del:{category}:{name}")],
        ]),
        parse_mode=ParseMode.MARKDOWN,
    )
    return TEMP_VALUE_INPUT


@auth_cb
async def cb_temp_preset_del(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    _, category, name = q.data.split(":")
    c = cfg()
    presets = c.get("temp_presets", {}).get(category, {})
    if name in presets:
        del presets[name]
    save_cfg()
    await q.answer(f"🗑️ {name}")
    ctx.user_data.pop("editing_temp", None)
    update.callback_query.data = f"set_temps:{category}"
    await cb_temp_presets_list(update, ctx)
    return ConversationHandler.END


@auth_cb
async def cb_temp_preset_add_ask(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    category = q.data[len("temp_preset_add:"):]
    await q.answer()
    L = lang()

    ctx.user_data["editing_temp"] = {"cat": category, "new": True}

    await q.edit_message_text(
        t("settings.temps.new_preset_name", L),
        reply_markup=InlineKeyboardMarkup([[btn(t("btn.cancel", L), "temp_preset_cancel")]]),
        parse_mode=ParseMode.MARKDOWN,
    )
    return TEMP_VALUE_INPUT


@auth_cb
async def cb_temp_preset_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    cat = ctx.user_data.get("editing_temp", {}).get("cat", "hotend")
    ctx.user_data.pop("editing_temp", None)
    update.callback_query.data = f"set_temps:{cat}"
    await cb_temp_presets_list(update, ctx)
    return ConversationHandler.END


@auth
async def handle_temp_value_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    data = ctx.user_data.get("editing_temp")
    if not data:
        return ConversationHandler.END

    category = data["cat"]
    c = cfg()
    presets = c.setdefault("temp_presets", {}).setdefault(category, {})
    L = lang()

    if data.get("new"):
        # We got the name, now ask for value
        ctx.user_data["editing_temp"]["name"] = text
        ctx.user_data["editing_temp"]["new"] = False
        await update.message.reply_text(
            t("settings.temps.prompt_val", L).format(name=text),
            reply_markup=InlineKeyboardMarkup([[btn(t("btn.cancel", L), "temp_preset_cancel")]]),
            parse_mode=ParseMode.MARKDOWN,
        )
        return TEMP_VALUE_INPUT
    else:
        # We got the value
        try:
            val = int(text)
            presets[data["name"]] = val
            save_cfg()
            await update.message.reply_text(
                t("generic.done", L),
                reply_markup=InlineKeyboardMarkup([[btn(t("btn.back_menu", L), f"set_temps:{category}")]]),
            )
            return ConversationHandler.END
        except ValueError:
            await update.message.reply_text(
                t("temps.invalid_hotend" if category == "hotend" else "temps.invalid_bed", L)
            )
            return TEMP_VALUE_INPUT
