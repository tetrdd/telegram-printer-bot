"""Status dashboard with auto-refresh support."""
from __future__ import annotations

import time
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import lang, get as get_cfg
from lang import t
from helpers import auth_cb, btn, uid, fmt_duration, offline_guard
import api

_AUTO_REFRESH: dict[int, bool] = {}


async def _show_status(q, user_id: int):
    L = lang()
    status = await api.printer_status(user_id=user_id)
    if status is None:
        await q.edit_message_text(
            t("status.offline", L),
            reply_markup=InlineKeyboardMarkup([[btn(t("btn.back_menu", L), "menu:main")]]),
        )
        return

    ps = status.get("print_stats", {})
    ds = status.get("display_status", {})
    vs = status.get("virtual_sdcard", {})
    extruder = status.get("extruder", {})
    heater_bed = status.get("heater_bed", {})
    fan = status.get("fan", {})
    gm = status.get("gcode_move", {})

    state = ps.get("state", "unknown")
    fname = ps.get("filename", "-")
    progress = ds.get("progress", 0) * 100
    print_dur = ps.get("print_duration", 0)
    total_dur = ps.get("total_duration", 0)

    hotend_t = extruder.get("temperature", 0)
    hotend_target = extruder.get("target", 0)
    bed_t = heater_bed.get("temperature", 0)
    bed_target = heater_bed.get("target", 0)
    fan_pct = round(fan.get("speed", 0) * 100)
    speed_factor = round(gm.get("speed_factor", 1.0) * 100)

    auto = _AUTO_REFRESH.get(user_id, False)

    text = (
        f"{t('status.title', L)}\n\n"
        f"{t('status.file', L)}: `{fname}`\n"
        f"{t('status.state', L)}: `{state}`\n"
        f"{t('status.progress', L)}: `{progress:.1f}%`\n"
        f"{t('status.hotend', L)}: `{hotend_t:.1f}°C / {hotend_target:.0f}°C`\n"
        f"{t('status.bed', L)}: `{bed_t:.1f}°C / {bed_target:.0f}°C`\n"
        f"{t('status.fan', L)}: `{fan_pct}%`\n"
        f"{t('status.speed', L)}: `{speed_factor}%`\n"
        f"{t('status.print_time', L)}: `{fmt_duration(print_dur)}`\n"
        f"{t('status.total_time', L)}: `{fmt_duration(total_dur)}`"
    )

    keyboard = [
        [btn(t("status.snapshot", L), "action:snapshot_inline")],
        [
            btn(t("btn.refresh", L), "menu:status"),
            btn(
                t("status.auto_on", L) if auto else t("status.auto_off", L),
                "status:toggle_auto"
            ),
        ],
        [btn(t("btn.back_menu", L), "menu:main")],
    ]

    await q.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = uid(update)

    if await offline_guard(q, user_id):
        return

    await _show_status(q, user_id)


@auth_cb
async def cb_toggle_auto(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = uid(update)
    _AUTO_REFRESH[user_id] = not _AUTO_REFRESH.get(user_id, False)
    await _show_status(q, user_id)
