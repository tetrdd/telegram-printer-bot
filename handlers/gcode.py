"""GCode console — quick buttons + free text input."""
from __future__ import annotations

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from config import lang
from lang import t
from helpers import auth_cb, btn, uid, offline_guard
import api

GCODE_INPUT = 1

QUICK_GCODES = [
    ("G28", "Home All"),
    ("G28 Z", "Home Z"),
    ("G29", "Bed Level"),
    ("M84", "Motors Off"),
    ("M112", "E-Stop"),
    ("FIRMWARE_RESTART", "FW Restart"),
    ("CANCEL_PRINT", "Cancel"),
    ("BED_MESH_CALIBRATE", "Mesh Cal."),
]


async def _show_gcode_menu(q, user_id: int, result: str = ""):
    L = lang()
    text = t("gcode.title", L)
    if result:
        text += f"\n\n`{result}`"

    # 2 per row
    rows = []
    for i in range(0, len(QUICK_GCODES), 2):
        row = [btn(QUICK_GCODES[i][1], f"gcode_quick:{QUICK_GCODES[i][0]}")]
        if i + 1 < len(QUICK_GCODES):
            row.append(btn(QUICK_GCODES[i + 1][1], f"gcode_quick:{QUICK_GCODES[i + 1][0]}"))
        rows.append(row)

    rows.append([btn(t("btn.back_menu", L), "menu:main")])

    await q.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_gcode_entry(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Entry point for gcode conversation."""
    q = update.callback_query
    await q.answer()
    user_id = uid(update)

    if await offline_guard(q, user_id):
        return ConversationHandler.END

    await _show_gcode_menu(q, user_id)
    return GCODE_INPUT


@auth_cb
async def cb_gcode_quick(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle quick gcode button press."""
    q = update.callback_query
    cmd = q.data[len("gcode_quick:"):]
    user_id = uid(update)
    await q.answer()

    if await offline_guard(q, user_id):
        return ConversationHandler.END

    result = await api.gcode(cmd, user_id=user_id)
    await _show_gcode_menu(q, user_id, result=result or "error")
    return GCODE_INPUT


async def handle_gcode_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle free-text gcode input."""
    user_id = update.effective_user.id
    from config import allowed_users
    if user_id not in allowed_users():
        return ConversationHandler.END

    cmd = update.message.text.strip()
    result = await api.gcode(cmd, user_id=user_id)
    L = lang()

    keyboard = [[btn(t("btn.back_menu", L), "menu:main")]]
    await update.message.reply_text(
        f"`{cmd}` → `{result or 'error'}`",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN,
    )
    return ConversationHandler.END


async def cancel_gcode(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END
