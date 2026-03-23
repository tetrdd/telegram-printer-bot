"""Axis movement controls — X, Y, Z homing and manual moves."""
from __future__ import annotations

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import lang
from lang import t
from helpers import auth_cb, btn, uid, printer_badge, offline_guard
import api

DEFAULT_STEP = 10.0


async def _show_move_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE, msg: str = ""):
    q = update.callback_query
    user_id = uid(update)
    L = lang()

    if await offline_guard(q, user_id):
        return

    step = ctx.user_data.get("move_step", DEFAULT_STEP)

    text = f"{printer_badge(user_id)}{t('move.title', L)}\n\n{t('move.step', L).format(val=step)}"
    if msg:
        text = f"{text}\n\n{msg}"

    # Navigation grid
    # Row 1: Y+
    # Row 2: X-, Home XY, X+
    # Row 3: Y-
    # Row 4: Z+, Home Z, Z-
    # Row 5: Steps
    # Row 6: Back

    keyboard = [
        [btn(" ", "move:none"), btn("Y+", f"move:move:Y:{step}"), btn(" ", "move:none")],
        [btn("X-", f"move:move:X:-{step}"), btn("🏠XY", "move:home:xy"), btn("X+", f"move:move:X:{step}")],
        [btn(" ", "move:none"), btn("Y-", f"move:move:Y:-{step}"), btn(" ", "move:none")],
        [btn("Z+", f"move:move:Z:{step}"), btn("🏠Z", "move:home:z"), btn("Z-", f"move:move:Z:-{step}")],
        [
            btn("0.1mm" + (" ✅" if step == 0.1 else ""), "move:step:0.1"),
            btn("1mm" + (" ✅" if step == 1.0 else ""), "move:step:1.0"),
            btn("10mm" + (" ✅" if step == 10.0 else ""), "move:step:10.0"),
            btn("50mm" + (" ✅" if step == 50.0 else ""), "move:step:50.0"),
        ],
        [btn(t("btn.back_menu", L), "menu:main")]
    ]

    await q.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_move(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await _show_move_menu(update, ctx)


@auth_cb
async def cb_move_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    user_id = uid(update)
    L = lang()

    data = q.data.split(":")
    action = data[1]

    if action == "none":
        await q.answer()
        return

    if action == "step":
        ctx.user_data["move_step"] = float(data[2])
        await q.answer()
        await _show_move_menu(update, ctx)
        return

    if await offline_guard(q, user_id):
        return

    msg = ""
    if action == "home":
        axis = data[2]
        if axis == "xy":
            await api.gcode("G28 X Y", user_id=user_id)
            msg = "🏠 Homing X Y..."
        elif axis == "z":
            await api.gcode("G28 Z", user_id=user_id)
            msg = "🏠 Homing Z..."
        await q.answer(msg)

    elif action == "move":
        axis = data[2]
        distance = float(data[3])
        # Ensure relative positioning for manual moves
        cmd = f"G91\nG1 {axis}{distance} F3000\nG90"
        await api.gcode(cmd, user_id=user_id)
        await q.answer(f"Moving {axis} {distance}mm")

    await _show_move_menu(update, ctx, msg=msg)
