"""Status dashboard with auto-refresh support."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram.error import BadRequest, TimedOut
from config import lang
from lang import t
from helpers import (
    auth_cb, btn, uid, progress_bar, fmt_duration, state_icon,
    printer_badge, fmt_clock_eta, fmt_time_ago,
)
from monitor import is_printer_online, cached_printer_status
import api

logger = logging.getLogger("PrinterBot.status")

# Track active auto-refresh tasks: {(chat_id, message_id): asyncio.Task}
_auto_refresh_tasks: dict[tuple[int, int], asyncio.Task] = {}


def _build_status_text(res: dict, user_id: int) -> str:
    L = lang()
    stats = res.get("print_stats", {})
    vsd = res.get("virtual_sdcard", {})
    ext = res.get("extruder", {})
    bed = res.get("heater_bed", {})
    gcode_move = res.get("gcode_move", {})
    fan = res.get("fan", {})

    display = res.get("display_status", {})

    state = stats.get("state", "unknown")
    filename = stats.get("filename", "—") or "—"
    # display_status.progress = slicer-estimated (M73), much more accurate
    # virtual_sdcard.progress = file-position based (unreliable)
    pct = display.get("progress", vsd.get("progress", 0)) * 100
    duration = stats.get("print_duration", 0)
    filament = stats.get("filament_used", 0) / 1000  # mm → m

    # Speed / flow override
    speed_factor = gcode_move.get("speed_factor", 1.0)
    extrude_factor = gcode_move.get("extrude_factor", 1.0)
    speed_pct = round(speed_factor * 100)
    flow_pct = round(extrude_factor * 100)

    # Fan speed
    fan_pct = round(fan.get("speed", 0) * 100)

    # Z-offset from homing_origin
    homing_origin = gcode_move.get("homing_origin", [0, 0, 0, 0])
    z_offset = homing_origin[2] if len(homing_origin) > 2 else 0.0

    eta_str = "—"
    clock_eta_str = "—"
    if pct > 1 and state == "printing":
        remaining = (duration / (pct / 100)) - duration
        eta_str = f"~{fmt_duration(remaining)}"
        clock_eta_str = fmt_clock_eta(remaining)

    # Layers
    info = stats.get("info", {})
    current_layer = info.get("current_layer")
    total_layer = info.get("total_layer")

    bar = progress_bar(pct)

    lines = [
        f"{printer_badge(user_id)}",
        f"{t('status.title', L)}\n",
        f"{t('status.state', L)}: {state_icon(state)}",
        f"{t('status.file', L)}: `{filename}`\n",
        f"{t('status.progress', L)}: `[{bar}]` {pct:.1f}%",
        f"{t('status.duration', L)}: {fmt_duration(duration)}",
        f"{t('status.eta', L)}: {eta_str}",
    ]

    if clock_eta_str != "—":
        lines.append(f"{t('status.clock_eta', L)}: {clock_eta_str}")

    if current_layer is not None and total_layer is not None:
        lines.append(f"{t('status.layers', L)}: {current_layer}/{total_layer}")

    lines.append(f"{t('status.filament', L)}: {filament:.2f} m\n")
    lines.append(
        f"🌡️ {t('status.hotend', L)}: {ext.get('temperature', 0):.1f}°C → {ext.get('target', 0):.0f}°C"
    )
    lines.append(
        f"🌡️ {t('status.bed', L)}: {bed.get('temperature', 0):.1f}°C → {bed.get('target', 0):.0f}°C"
    )

    # Only show overrides if they differ from 100%
    overrides = []
    if speed_pct != 100:
        overrides.append(f"{t('status.speed', L)}: {speed_pct}%")
    if flow_pct != 100:
        overrides.append(f"{t('status.flow', L)}: {flow_pct}%")
    if fan_pct > 0:
        overrides.append(f"{t('status.fan', L)}: {fan_pct}%")
    if z_offset != 0.0:
        overrides.append(f"Z: {z_offset:+.3f}mm")
    if overrides:
        lines.append("\n" + " | ".join(overrides))

    return "\n".join(lines)


def _build_offline_status_text(cached: dict, cached_at: float, user_id: int) -> str:
    L = lang()
    lines = [
        f"{printer_badge(user_id)}",
        f"{t('offline.title', L)}\n",
        f"{t('offline.cached', L)}",
        f"{t('offline.last_seen', L).format(time=fmt_time_ago(cached_at))}\n",
    ]

    if cached:
        stats = cached.get("print_stats", {})
        vsd = cached.get("virtual_sdcard", {})
        ext = cached.get("extruder", {})
        bed = cached.get("heater_bed", {})

        state = stats.get("state", "unknown")
        filename = stats.get("filename", "—") or "—"
        display = cached.get("display_status", {})
        pct = display.get("progress", vsd.get("progress", 0)) * 100

        lines.append(f"{t('status.state', L)}: {state_icon(state)}")
        lines.append(f"{t('status.file', L)}: `{filename}`")
        lines.append(f"{t('status.progress', L)}: {pct:.1f}%")
        lines.append(
            f"🌡️ {t('status.hotend', L)}: {ext.get('temperature', 0):.1f}°C"
        )
        lines.append(
            f"🌡️ {t('status.bed', L)}: {bed.get('temperature', 0):.1f}°C"
        )

    return "\n".join(lines)


def _status_keyboard(auto_active: bool) -> InlineKeyboardMarkup:
    L = lang()
    toggle_key = "status.auto_on" if auto_active else "status.auto_off"
    return InlineKeyboardMarkup([
        [btn(t("btn.refresh", L), "menu:status"), btn(t("btn.snapshot", L), "action:snapshot_inline")],
        [btn(t("adjust.btn", L), "menu:adjust"), btn(t("history.btn", L), "menu:history")],
        [btn(t("mesh.btn", L), "menu:bed_mesh")],
        [btn(t(toggle_key, L), "status:toggle_auto")],
        [btn(t("btn.back_menu", L), "menu:main")],
    ])


def _status_keyboard_offline() -> InlineKeyboardMarkup:
    L = lang()
    return InlineKeyboardMarkup([
        [btn(t("btn.refresh", L), "menu:status")],
        [btn(t("btn.back_menu", L), "menu:main")],
    ])


@auth_cb
async def cb_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = uid(update)

    # Check if printer is offline
    if not is_printer_online(user_id):
        L = lang()
        cached, cached_at = cached_printer_status(user_id)
        text = _build_offline_status_text(cached, cached_at, user_id)
        await q.edit_message_text(
            text,
            reply_markup=_status_keyboard_offline(),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    res = await api.printer_status(user_id=user_id)
    if not res:
        L = lang()
        await q.edit_message_text(
            t("err.no_connect", L),
            reply_markup=InlineKeyboardMarkup([[btn(t("btn.back_menu", L), "menu:main")]]),
        )
        return

    key = (q.message.chat_id, q.message.message_id)
    auto_active = key in _auto_refresh_tasks

    text = _build_status_text(res, user_id)
    await q.edit_message_text(
        text,
        reply_markup=_status_keyboard(auto_active),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_toggle_auto(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = uid(update)

    chat_id = q.message.chat_id
    msg_id = q.message.message_id
    key = (chat_id, msg_id)

    if key in _auto_refresh_tasks:
        # Stop auto-refresh
        _auto_refresh_tasks[key].cancel()
        del _auto_refresh_tasks[key]
        # Refresh once to update the button label
        res = await api.printer_status(user_id=user_id)
        if res:
            await q.edit_message_text(
                _build_status_text(res, user_id),
                reply_markup=_status_keyboard(False),
                parse_mode=ParseMode.MARKDOWN,
            )
    else:
        # Start auto-refresh
        task = asyncio.create_task(_auto_refresh_loop(ctx.bot, chat_id, msg_id, user_id))
        _auto_refresh_tasks[key] = task


async def _auto_refresh_loop(bot, chat_id: int, msg_id: int, user_id: int):
    """Edits the status message every 5 seconds until stopped."""
    key = (chat_id, msg_id)
    last_text = ""
    try:
        while True:
            await asyncio.sleep(5)

            if not is_printer_online(user_id):
                cached, cached_at = cached_printer_status(user_id)
                text = _build_offline_status_text(cached, cached_at, user_id)
                markup = _status_keyboard_offline()
            else:
                res = await api.printer_status(user_id=user_id)
                if not res:
                    continue
                text = _build_status_text(res, user_id)
                markup = _status_keyboard(True)

            # Only edit if content actually changed (avoid Telegram API errors)
            if text == last_text:
                continue
            last_text = text

            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=msg_id,
                    text=text,
                    reply_markup=markup,
                    parse_mode=ParseMode.MARKDOWN,
                )
            except BadRequest as e:
                if "message is not modified" in str(e).lower():
                    continue
                logger.warning(f"Auto-refresh edit failed: {e}")
                break
            except TimedOut:
                continue
            except Exception as e:
                logger.warning(f"Auto-refresh error: {e}")
                break
    except asyncio.CancelledError:
        pass
    finally:
        _auto_refresh_tasks.pop(key, None)
