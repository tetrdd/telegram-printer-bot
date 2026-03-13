"""Main menu — button grid entry point for all features."""

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import get as cfg, lang, is_multi_printer, active_printer_name
from lang import t
from helpers import auth, auth_cb, btn, uid


def main_menu_keyboard(user_id: int) -> InlineKeyboardMarkup:
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
    if is_multi_printer():
        name = active_printer_name(user_id)
        buttons.append([btn(f"🔀 {t('menu.switch_printer', L)} ({name})", "menu:printers")])
    return InlineKeyboardMarkup(buttons)


def main_menu_text(user_id: int) -> str:
    L = lang()
    text = t("menu.title", L)
    if is_multi_printer():
        name = active_printer_name(user_id)
        text = f"🖨️ *{name}*\n\n{text}"
    return text


@auth
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = uid(update)
    await update.message.reply_text(
        main_menu_text(user_id),
        reply_markup=main_menu_keyboard(user_id),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth
async def cmd_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await cmd_start(update, ctx)


async def show_menu(query, user_id: int = None):
    """Edit a callback query message back to the main menu."""
    if user_id is None:
        user_id = query.from_user.id
    await query.edit_message_text(
        main_menu_text(user_id),
        reply_markup=main_menu_keyboard(user_id),
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
    from handlers.printers import cb_printers

    routes = {
        "main": lambda: show_menu(q, uid(update)),
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
        "printers": lambda: cb_printers(update, ctx),
    }

    handler = routes.get(target)
    if handler:
        await handler()
    else:
        await q.answer("Unknown")
