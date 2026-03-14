"""Main menu — button grid entry point for all features."""
from __future__ import annotations

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import lang, is_multi_printer
from lang import t
from helpers import auth, auth_cb, btn, uid


def _main_menu_keyboard(L: str) -> list:
    rows = [
        [btn(t("menu.status", L), "menu:status"), btn(t("menu.temps", L), "menu:temps")],
        [btn(t("menu.files", L), "menu:files"), btn(t("menu.control", L), "menu:control")],
        [btn(t("menu.gcode", L), "menu:gcode"), btn(t("menu.macros", L), "menu:macros")],
        [btn(t("menu.camera", L), "menu:camera"), btn(t("menu.system", L), "menu:system")],
        [btn(t("menu.estop", L), "menu:estop"), btn(t("menu.settings", L), "menu:settings")],
        [btn(t("menu.adjust", L), "menu:adjust"), btn(t("menu.history", L), "menu:history")],
        [btn(t("menu.bed_mesh", L), "menu:bed_mesh")],
    ]
    if is_multi_printer():
        rows.append([btn(t("menu.printers", L), "menu:printers")])
    return rows


@auth
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    L = lang()
    await update.message.reply_text(
        t("menu.welcome", L),
        reply_markup=InlineKeyboardMarkup(_main_menu_keyboard(L)),
    )


@auth
async def cmd_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    L = lang()
    await update.message.reply_text(
        t("menu.title", L),
        reply_markup=InlineKeyboardMarkup(_main_menu_keyboard(L)),
    )


@auth_cb
async def cb_menu_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Route menu:* callbacks to the correct handler."""
    q = update.callback_query
    await q.answer()
    action = q.data.split(":")[1]
    user_id = uid(update)

    from handlers.status import cb_status
    from handlers.temps import cb_temps
    from handlers.files import cb_files
    from handlers.control import cb_print_ctrl
    from handlers.camera import cb_camera
    from handlers.macros import cb_macros
    from handlers.system import cb_system
    from handlers.estop import cb_estop
    from handlers.settings import cb_settings
    from handlers.printers import cb_printers
    from handlers.adjust import cb_adjust
    from handlers.bed_mesh import cb_bed_mesh
    from handlers.history import cb_history

    dispatch = {
        "main": lambda u, c: _back_to_main(q, user_id),
        "status": cb_status,
        "temps": cb_temps,
        "files": lambda u, c: cb_files_page(u, c),
        "control": cb_print_ctrl,
        "camera": cb_camera,
        "macros": lambda u, c: cb_macros_page(u, c),
        "system": cb_system,
        "estop": cb_estop,
        "settings": cb_settings,
        "printers": cb_printers,
        "adjust": cb_adjust,
        "bed_mesh": cb_bed_mesh,
        "history": cb_history,
    }

    handler = dispatch.get(action)
    if handler:
        await handler(update, ctx)
    else:
        L = lang()
        await q.edit_message_text(
            t("menu.title", L),
            reply_markup=InlineKeyboardMarkup(_main_menu_keyboard(L)),
        )


async def _back_to_main(q, user_id: int):
    L = lang()
    await q.edit_message_text(
        t("menu.title", L),
        reply_markup=InlineKeyboardMarkup(_main_menu_keyboard(L)),
    )


async def cb_files_page(update, ctx):
    """Wrapper: redirect menu:files → files:page:0:date"""
    update.callback_query.data = "files:page:0:date"
    from handlers.files import cb_files
    await cb_files(update, ctx)


async def cb_macros_page(update, ctx):
    """Wrapper: redirect menu:macros → macros:page:0"""
    update.callback_query.data = "macros:page:0"
    from handlers.macros import cb_macros
    await cb_macros(update, ctx)
