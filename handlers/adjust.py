"""Adjustment controls — speed, flow, fan, Z-offset."""

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import lang
from lang import t
from helpers import auth_cb, btn, uid, offline_guard
import api


async def _show_adjust(q, user_id: int, msg: str = ""):
    """Fetch current values and show the adjustment panel."""
    L = lang()

    data = await api.get(
        "/printer/objects/query?gcode_move&fan",
        user_id=user_id,
    )

    speed_pct = 100
    flow_pct = 100
    fan_pct = 0
    z_offset = 0.0

    if data:
        status = data.get("result", {}).get("status", {})
        gcode_move = status.get("gcode_move", {})
        fan = status.get("fan", {})

        speed_pct = round(gcode_move.get("speed_factor", 1.0) * 100)
        flow_pct = round(gcode_move.get("extrude_factor", 1.0) * 100)
        fan_pct = round(fan.get("speed", 0) * 100)
        homing_origin = gcode_move.get("homing_origin", [0, 0, 0, 0])
        z_offset = homing_origin[2] if len(homing_origin) > 2 else 0.0

    text = (
        f"{t('adjust.title', L)}\n\n"
        f"{t('adjust.speed', L).format(val=speed_pct)}\n"
        f"{t('adjust.flow', L).format(val=flow_pct)}\n"
        f"{t('adjust.fan', L).format(val=fan_pct)}\n"
        f"{t('adjust.z_offset', L).format(val=f'{z_offset:+.3f}')}"
    )
    if msg:
        text = f"{text}\n\n✅ {msg}"

    keyboard = [
        # Speed presets
        [
            btn("50%", "adjust:speed:50"),
            btn("75%", "adjust:speed:75"),
            btn("100%", "adjust:speed:100"),
            btn("125%", "adjust:speed:125"),
            btn("150%", "adjust:speed:150"),
        ],
        # Flow presets
        [
            btn("💧75%", "adjust:flow:75"),
            btn("💧100%", "adjust:flow:100"),
            btn("💧110%", "adjust:flow:110"),
            btn("💧120%", "adjust:flow:120"),
        ],
        # Fan presets
        [
            btn("🌀0%", "adjust:fan:0"),
            btn("🌀25%", "adjust:fan:25"),
            btn("🌀50%", "adjust:fan:50"),
            btn("🌀75%", "adjust:fan:75"),
            btn("🌀100%", "adjust:fan:100"),
        ],
        # Z-offset adjustment
        [
            btn(t("adjust.z_up", L).format(step="0.05"), "adjust:z:+0.05"),
            btn(t("adjust.z_up", L).format(step="0.01"), "adjust:z:+0.01"),
            btn(t("adjust.z_down", L).format(step="0.01"), "adjust:z:-0.01"),
            btn(t("adjust.z_down", L).format(step="0.05"), "adjust:z:-0.05"),
        ],
        [btn(t("adjust.z_reset", L), "adjust:z:reset")],
        [btn(t("btn.refresh", L), "menu:adjust"), btn(t("btn.back_menu", L), "menu:main")],
    ]

    await q.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_adjust(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = uid(update)

    if await offline_guard(q, user_id):
        return

    await _show_adjust(q, user_id)


@auth_cb
async def cb_adjust_speed(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    # Pattern: adjust:speed:<pct>
    parts = q.data.split(":")
    pct = int(parts[2])
    user_id = uid(update)
    await q.answer()

    if await offline_guard(q, user_id):
        return

    L = lang()
    r = await api.set_speed_factor(pct, user_id=user_id)
    msg = t("adjust.speed_set", L).format(val=pct) if r else ""
    await _show_adjust(q, user_id, msg=msg)


@auth_cb
async def cb_adjust_flow(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    # Pattern: adjust:flow:<pct>
    parts = q.data.split(":")
    pct = int(parts[2])
    user_id = uid(update)
    await q.answer()

    if await offline_guard(q, user_id):
        return

    L = lang()
    r = await api.set_flow_factor(pct, user_id=user_id)
    msg = t("adjust.flow_set", L).format(val=pct) if r else ""
    await _show_adjust(q, user_id, msg=msg)


@auth_cb
async def cb_adjust_fan(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    # Pattern: adjust:fan:<pct>
    parts = q.data.split(":")
    pct = int(parts[2])
    user_id = uid(update)
    await q.answer()

    if await offline_guard(q, user_id):
        return

    L = lang()
    r = await api.set_fan_speed(pct, user_id=user_id)
    msg = t("adjust.fan_set", L).format(val=pct) if r else ""
    await _show_adjust(q, user_id, msg=msg)


@auth_cb
async def cb_adjust_z(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    # Pattern: adjust:z:<value>  where value is +0.01, -0.01, +0.05, -0.05, or "reset"
    parts = q.data.split(":")
    value = parts[2]
    user_id = uid(update)
    await q.answer()

    if await offline_guard(q, user_id):
        return

    L = lang()
    if value == "reset":
        r = await api.reset_z_offset(user_id=user_id)
        msg = t("adjust.z_reset", L) if r else ""
    else:
        offset = float(value)
        r = await api.adjust_z_offset(offset, user_id=user_id)
        sign = "+" if offset > 0 else ""
        msg = f"Z {sign}{offset:.3f}mm" if r else ""

    await _show_adjust(q, user_id, msg=msg)
