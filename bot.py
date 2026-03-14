#!/usr/bin/env python3
"""
Telegram Printer Bot — Main entry point.
Registers all handlers and starts polling.
"""
from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path so imports work
sys.path.insert(0, str(Path(__file__).parent))

from telegram import BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

import config
from monitor import PrintMonitor

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("PrinterBot")


def main():
    # Load config
    cfg = config.load()
    token = cfg["telegram"]["bot_token"]

    app = Application.builder().token(token).build()

    # ── Import handlers ──────────────────────────────────────────────────────
    from handlers.menu import cmd_start, cmd_menu, cb_menu_router
    from handlers.status import cb_status, cb_toggle_auto
    from handlers.temps import (
        cb_temps, cb_temp_presets, cb_set_temp, cb_cool_all,
        cb_temp_custom_hotend, cb_temp_custom_bed,
        handle_custom_hotend, handle_custom_bed,
        TEMP_CUSTOM_HOTEND, TEMP_CUSTOM_BED,
    )
    from handlers.files import (
        cb_files, cb_file_sort, cb_file_info, cb_file_print,
        cb_file_start, cb_file_delete_ask, cb_file_delete,
    )
    from handlers.control import cb_print_ctrl, cb_ctrl_action, cb_ctrl_cancel, cb_ctrl_confirm
    from handlers.gcode import cb_gcode_entry, cb_gcode_quick, handle_gcode_input, cancel_gcode, GCODE_INPUT
    from handlers.macros import cb_macros, cb_macro_ask, cb_macro_run
    from handlers.camera import cb_camera, cb_snapshot_action, cb_snapshot_inline
    from handlers.system import cb_system, cb_sys_action, cb_sys_confirm
    from handlers.estop import cb_estop, cb_estop_confirm
    from handlers.settings import cb_settings, cb_setting_toggle
    from handlers.printers import cb_printers, cb_printer_select, cb_printer_status_all
    from handlers.adjust import cb_adjust, cb_adjust_speed, cb_adjust_flow, cb_adjust_fan, cb_adjust_z
    from handlers.bed_mesh import cb_bed_mesh
    from handlers.history import cb_history, cb_history_page

    # ── Conversation handlers (registered first for priority) ────────────────
    gcode_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_gcode_entry, pattern=r"^menu:gcode$")],
        states={
            GCODE_INPUT: [
                CallbackQueryHandler(cb_gcode_quick, pattern=r"^gcode_quick:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gcode_input),
            ],
        },
        fallbacks=[
            CommandHandler("menu", cancel_gcode),
            CommandHandler("cancel", cancel_gcode),
            CallbackQueryHandler(cb_menu_router, pattern=r"^menu:"),
        ],
        per_message=False,
    )

    temp_hotend_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_temp_custom_hotend, pattern=r"^temp_custom:hotend$")],
        states={
            TEMP_CUSTOM_HOTEND: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_hotend),
            ],
        },
        fallbacks=[
            CommandHandler("menu", cancel_gcode),
            CommandHandler("cancel", cancel_gcode),
            CallbackQueryHandler(cb_menu_router, pattern=r"^menu:"),
        ],
        per_message=False,
    )

    temp_bed_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_temp_custom_bed, pattern=r"^temp_custom:bed$")],
        states={
            TEMP_CUSTOM_BED: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_bed),
            ],
        },
        fallbacks=[
            CommandHandler("menu", cancel_gcode),
            CommandHandler("cancel", cancel_gcode),
            CallbackQueryHandler(cb_menu_router, pattern=r"^menu:"),
        ],
        per_message=False,
    )

    app.add_handler(gcode_conv)
    app.add_handler(temp_hotend_conv)
    app.add_handler(temp_bed_conv)

    # ── Commands ─────────────────────────────────────────────────────────────
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("menu", cmd_menu))
    app.add_handler(CommandHandler("help", cmd_start))

    # ── Callback queries ──────────────────────────────────────────────────────
    # Menu router (catches all menu:* except gcode which is handled by conv)
    app.add_handler(CallbackQueryHandler(cb_menu_router, pattern=r"^menu:"))

    # Status
    app.add_handler(CallbackQueryHandler(cb_toggle_auto, pattern=r"^status:toggle_auto$"))

    # Temperatures
    app.add_handler(CallbackQueryHandler(cb_temp_presets, pattern=r"^temp:(hotend|bed)$"))
    app.add_handler(CallbackQueryHandler(cb_set_temp, pattern=r"^set_temp:"))
    app.add_handler(CallbackQueryHandler(cb_cool_all, pattern=r"^temp:cool_all$"))

    # Print control
    app.add_handler(CallbackQueryHandler(cb_ctrl_action, pattern=r"^ctrl:(pause|resume|home|motors_off)$"))
    app.add_handler(CallbackQueryHandler(cb_ctrl_cancel, pattern=r"^ctrl:cancel$"))
    app.add_handler(CallbackQueryHandler(cb_ctrl_confirm, pattern=r"^ctrl_confirm:"))

    # Files
    app.add_handler(CallbackQueryHandler(cb_files, pattern=r"^files:page:"))
    app.add_handler(CallbackQueryHandler(cb_file_sort, pattern=r"^files:sort:"))
    app.add_handler(CallbackQueryHandler(cb_file_print, pattern=r"^file:print:"))
    app.add_handler(CallbackQueryHandler(cb_file_start, pattern=r"^file:start:"))
    app.add_handler(CallbackQueryHandler(cb_file_info, pattern=r"^file:info:"))
    app.add_handler(CallbackQueryHandler(cb_file_delete_ask, pattern=r"^file:delete_ask:"))
    app.add_handler(CallbackQueryHandler(cb_file_delete, pattern=r"^file:delete:"))

    # Camera
    app.add_handler(CallbackQueryHandler(cb_snapshot_action, pattern=r"^action:snapshot$"))
    app.add_handler(CallbackQueryHandler(cb_snapshot_inline, pattern=r"^action:snapshot_inline$"))

    # Macros
    app.add_handler(CallbackQueryHandler(cb_macro_ask, pattern=r"^macro:run_ask:"))
    app.add_handler(CallbackQueryHandler(cb_macro_run, pattern=r"^macro:run:"))
    app.add_handler(CallbackQueryHandler(cb_macros, pattern=r"^macros:page:"))

    # System
    app.add_handler(CallbackQueryHandler(cb_sys_action, pattern=r"^sys:(fw_restart|host_restart)$"))
    app.add_handler(CallbackQueryHandler(cb_sys_confirm, pattern=r"^sys_confirm:"))

    # Emergency stop
    app.add_handler(CallbackQueryHandler(cb_estop_confirm, pattern=r"^estop:confirm$"))

    # Printers
    app.add_handler(CallbackQueryHandler(cb_printer_select, pattern=r"^printer:select:"))
    app.add_handler(CallbackQueryHandler(cb_printer_status_all, pattern=r"^printer:status_all$"))

    # Adjust
    app.add_handler(CallbackQueryHandler(cb_adjust_speed, pattern=r"^adjust:speed:"))
    app.add_handler(CallbackQueryHandler(cb_adjust_flow, pattern=r"^adjust:flow:"))
    app.add_handler(CallbackQueryHandler(cb_adjust_fan, pattern=r"^adjust:fan:"))
    app.add_handler(CallbackQueryHandler(cb_adjust_z, pattern=r"^adjust:z:"))

    # History
    app.add_handler(CallbackQueryHandler(cb_history_page, pattern=r"^history:page:"))

    # Settings (must be last — catches all set:* patterns)
    app.add_handler(CallbackQueryHandler(cb_setting_toggle, pattern=r"^set:"))

    # ── Lifecycle hooks ───────────────────────────────────────────────────────
    async def post_init(application: Application):
        # Set bot command menu
        await application.bot.set_my_commands([
            BotCommand("menu", "Open main menu"),
            BotCommand("start", "Start / restart"),
            BotCommand("help", "Show help"),
            BotCommand("cancel", "Cancel current action"),
        ])
        # Start background monitor
        monitor = PrintMonitor(application)
        asyncio.create_task(monitor.start())
        application.bot_data["monitor"] = monitor

    async def pre_shutdown(application: Application):
        monitor = application.bot_data.get("monitor")
        if monitor:
            monitor.stop()

    app.post_init = post_init
    app.post_shutdown = pre_shutdown

    logger.info("Bot starting...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
