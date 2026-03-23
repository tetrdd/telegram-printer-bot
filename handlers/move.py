"""Move axes control — X, Y, Z movement with selectable steps."""
from __future__ import annotations

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import lang
from lang import t
from helpers import auth_cb, btn, uid, offline_guard
import api


@auth_cb
async def cb_move_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = uid(update)
    L = lang()

    if await offline_guard(q, user_id):
        return

    # Check if printing
    status = await api.printer_status(user_id=user_id)
    state = status.get("print_stats", {}).get("state", "unknown")
    if state == "printing":
        await q.answer("⛔ Cannot move axes while printing!", show_alert=True)
        return

    # Get current step from user_data or default to 10
    step = ctx.user_data.get("move_step", 10.0)

    kb = [
        # Y Axis
        [btn(" ", "noop"), btn("Y+", f"move:Y:{step}"), btn(" ", "noop")],
        # X Axis
        [btn("X-", f"move:X:-{step}"), btn("🏠", "ctrl:home"), btn("X+", f"move:X:{step}")],
        # Y Axis down
        [btn(" ", "noop"), btn("Y-", f"move:Y:-{step}"), btn(" ", "noop")],
        # Z Axis
        [btn("Z+", f"move:Z:{step}"), btn(" ", "noop"), btn("Z-", f"move:Z:-{step}")],
        # Step selection
        [
            btn(f"{'🔹' if step == 0.1 else ''}0.1", "move_step:0.1"),
            btn(f"{'🔹' if step == 1.0 else ''}1", "move_step:1"),
            btn(f"{'🔹' if step == 10.0 else ''}10", "move_step:10"),
            btn(f"{'🔹' if step == 50.0 else ''}50", "move_step:50"),
        ],
        [btn(t("btn.back_menu", L), "menu:main")],
    ]

    await q.edit_message_text(
        t("move.title", L),
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_move_step(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    step = float(q.data.split(":")[1])
    ctx.user_data["move_step"] = step
    await q.answer(f"Step: {step}mm")
    await cb_move_menu(update, ctx)


@auth_cb
async def cb_move_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    _, axis, dist = q.data.split(":")
    user_id = uid(update)

    # Send relative move command
    # G91: relative positioning
    # G1: linear move
    # G90: absolute positioning (to restore)
    cmd = f"G91\nG1 {axis}{dist} F3000\nG90"
    r = await api.gcode(cmd, user_id=user_id)

    await q.answer(f"Moving {axis} {dist}mm {'✓' if r else '✗'}")
