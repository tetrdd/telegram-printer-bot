"""Main menu — button grid entry point for all features."""

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import get as cfg, lang
from lang import t
from helpers import auth, auth_cb, btn


def main_menu_keyboard() -> InlineKeyboardMarkup:
    L = lang()
    buttons = [
        [btn(t("menu.status", L), "menu:status"), btn(t("menu.temps", L), "menu:temps")],
        [btn(t("menu.files", L), "menu:files"), btn(t("menu.print_ctrl", L), "menu:print_ctrl")],
        [btn(t("menu.macros", L), "menu:macros"), btn(t("menu.gcode", L), "menu:gcode")],
        [btn(t("menu.camera", L), "menu:camera"), btn(t("menu.system", L), "menu:system")],
        [btn(t("menu.settings", L), "menu:settings")],
    ]
    if cfg().get("safety", {}).get("emergency_stop_enabled", True):
        buttons.append([btn(t("menu.estop", L), "menu:estop")])
    return InlineKeyboardMarkup(buttons)


def main_menu_text() -> str:
    return t("menu.title", lang())


@auth
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        main_menu_text(),
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth
async def cmd_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await cmd_start(update, ctx)


async def show_menu(query):
    """Edit a callback query message back to the main menu."""
    await query.edit_message_text(
        main_menu_text(),
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_menu_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Routes all menu:* callbacks to the correct handler."""
    q = update.callback_query
    target = q.data.split(":")[1]

    # Lazy imports to avoid circular dependencies
    from handlers.status import cb_status
    from handlers.temps import cb_temps
    from handlers.files import cb_files
    from handlers.control import cb_print_ctrl
    from handlers.macros import cb_macros
    from handlers.gcode import cb_gcode_entry
    from handlers.camera import cb_camera
    from handlers.system import cb_system
    from handlers.settings import cb_settings
    from handlers.estop import cb_estop

    routes = {
        "main": lambda: show_menu(q),
        "status": lambda: cb_status(update, ctx),
        "temps": lambda: cb_temps(update, ctx),
        "files": lambda: cb_files(update, ctx),
        "print_ctrl": lambda: cb_print_ctrl(update, ctx),
        "macros": lambda: cb_macros(update, ctx),
        "gcode": lambda: cb_gcode_entry(update, ctx),
        "camera": lambda: cb_camera(update, ctx),
        "system": lambda: cb_system(update, ctx),
        "settings": lambda: cb_settings(update, ctx),
        "estop": lambda: cb_estop(update, ctx),
    }

    handler = routes.get(target)
    if handler:
        await handler()
    else:
        await q.answer("Unknown")
