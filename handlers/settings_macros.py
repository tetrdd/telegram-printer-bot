"""Macro management settings — renaming, hiding, confirmation toggles."""
from __future__ import annotations

import math
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from config import get as cfg, save as save_cfg, lang
from lang import t
from helpers import auth_cb, auth, btn, uid, grid
import api

MACRO_ALIAS_INPUT = 300


@auth_cb
async def cb_settings_macros(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    L = lang()
    kb = [
        [btn(t("settings.macros.aliases", L), "set_macros:aliases:0")],
        [btn(t("settings.macros.visibility", L), "set_macros:visibility:0")],
        [btn(t("settings.macros.confirm", L), "set_macros:confirm:0")],
        [btn(f"📄 {t('settings.files_per_page', L)}: {cfg().get('macros', {}).get('per_page', 8)}", "set_macros:cycle_per_page")],
        [btn(t("btn.back_menu", L), "menu:settings")],
    ]
    await q.edit_message_text(
        t("settings.macros.title", L),
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_macro_settings_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data[len("set_macros:"):]
    L = lang()

    if data == "cycle_per_page":
        options = [4, 6, 8, 10, 12, 16]
        current = cfg().get("macros", {}).get("per_page", 8)
        try:
            idx = options.index(current)
            new = options[(idx + 1) % len(options)]
        except ValueError:
            new = 8
        cfg().setdefault("macros", {})["per_page"] = new
        save_cfg()
        await q.answer(f"📄 {new}")
        await cb_settings_macros(update, ctx)
        return

    parts = data.split(":")
    action = parts[0]
    page = int(parts[1]) if len(parts) > 1 else 0

    user_id = uid(update)
    objects = await api.printer_objects(user_id=user_id)
    macros = sorted([
        obj.replace("gcode_macro ", "")
        for obj in objects
        if obj.startswith("gcode_macro ") and not obj.startswith("gcode_macro _")
    ])

    if not macros:
        await q.answer(t("macros.empty", L), show_alert=True)
        return

    macro_cfg = cfg().get("macros", {})
    per_page = 10
    total_pages = math.ceil(len(macros) / per_page)
    page = max(0, min(page, total_pages - 1))
    page_macros = macros[page * per_page : (page + 1) * per_page]

    buttons = []
    if action == "aliases":
        aliases = macro_cfg.get("aliases", {})
        for m in page_macros:
            alias = aliases.get(m, m)
            buttons.append(btn(f"{m} → {alias}", f"macro_edit_alias:{m}"))
    elif action == "visibility":
        hidden = macro_cfg.get("hidden", [])
        for m in page_macros:
            is_hidden = m in hidden
            label = f"{'❌' if is_hidden else '✅'} {m}"
            buttons.append(btn(label, f"macro_toggle_hide:{m}:{page}"))
    elif action == "confirm":
        no_confirm = macro_cfg.get("no_confirm", [])
        for m in page_macros:
            needs_confirm = m not in no_confirm
            label = f"{'🛡️' if needs_confirm else '⚡'} {m}"
            buttons.append(btn(label, f"macro_toggle_confirm:{m}:{page}"))

    kb = [[b] for b in buttons]

    # Nav
    nav = []
    if page > 0:
        nav.append(btn(t("files.prev", L), f"set_macros:{action}:{page - 1}"))
    if page < total_pages - 1:
        nav.append(btn(t("files.next", L), f"set_macros:{action}:{page + 1}"))
    if nav:
        kb.append(nav)

    kb.append([btn(t("btn.back_menu", L), "set_cat:macros")])

    title_key = f"settings.macros.{action}_title"
    if action == "visibility":
        title_key = "settings.macros.hide_title"
    title = t(title_key, L) if action != "aliases" else t("settings.macros.aliases", L)

    await q.edit_message_text(
        title,
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_macro_toggle_hide(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    _, macro, page = q.data.split(":")
    macro_cfg = cfg().setdefault("macros", {})
    hidden = macro_cfg.get("hidden", [])
    if macro in hidden:
        hidden.remove(macro)
    else:
        hidden.append(macro)
    macro_cfg["hidden"] = hidden
    save_cfg()
    update.callback_query.data = f"set_macros:visibility:{page}"
    await cb_macro_settings_router(update, ctx)


@auth_cb
async def cb_macro_toggle_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    _, macro, page = q.data.split(":")
    macro_cfg = cfg().setdefault("macros", {})
    no_confirm = macro_cfg.get("no_confirm", [])
    if macro in no_confirm:
        no_confirm.remove(macro)
    else:
        no_confirm.append(macro)
    macro_cfg["no_confirm"] = no_confirm
    save_cfg()
    update.callback_query.data = f"set_macros:confirm:{page}"
    await cb_macro_settings_router(update, ctx)


@auth_cb
async def cb_macro_edit_alias(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    macro = q.data[len("macro_edit_alias:"):]
    L = lang()
    alias = cfg().get("macros", {}).get("aliases", {}).get(macro, macro)

    ctx.user_data["editing_macro_alias"] = macro

    kb = [
        [btn(t("btn.cancel", L), "macro_alias_cancel"), btn(t("settings.macros.reset_name", L), f"macro_alias_reset:{macro}")]
    ]

    await q.edit_message_text(
        t("settings.macros.alias_prompt", L).format(macro=macro, alias=alias),
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN,
    )
    return MACRO_ALIAS_INPUT


@auth_cb
async def cb_macro_alias_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    ctx.user_data.pop("editing_macro_alias", None)
    update.callback_query.data = "set_macros:aliases:0"
    await cb_macro_settings_router(update, ctx)
    return ConversationHandler.END


@auth_cb
async def cb_macro_alias_reset(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    macro = q.data[len("macro_alias_reset:"):]
    macro_cfg = cfg().setdefault("macros", {})
    aliases = macro_cfg.setdefault("aliases", {})
    if macro in aliases:
        del aliases[macro]
    save_cfg()
    await q.answer(t("generic.done", lang()))
    ctx.user_data.pop("editing_macro_alias", None)
    update.callback_query.data = "set_macros:aliases:0"
    await cb_macro_settings_router(update, ctx)
    return ConversationHandler.END


@auth
async def handle_macro_alias_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    new_alias = update.message.text.strip()
    macro = ctx.user_data.get("editing_macro_alias")
    if not macro:
        return ConversationHandler.END

    macro_cfg = cfg().setdefault("macros", {})
    aliases = macro_cfg.setdefault("aliases", {})
    aliases[macro] = new_alias
    save_cfg()

    L = lang()
    await update.message.reply_text(
        t("generic.done", L),
        reply_markup=InlineKeyboardMarkup([[btn(t("btn.back_menu", L), "set_macros:aliases:0")]]),
    )
    return ConversationHandler.END
