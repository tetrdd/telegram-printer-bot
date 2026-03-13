"""Status dashboard with auto-refresh support."""

import asyncio
import logging
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram.error import BadRequest, TimedOut
from config import lang
from lang import t
from helpers import auth_cb, btn, uid, progress_bar, fmt_duration, state_icon, printer_badge
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

    state = stats.get("state", "unknown")
    filename = stats.get("filename", "—") or "—"
    pct = vsd.get("progress", 0) * 100
    duration = stats.get("print_duration", 0)
    filament = stats.get("filament_used", 0) / 1000  # mm → m

    eta_str = "—"
    if pct > 1 and state == "printing":
        remaining = (duration / (pct / 100)) - duration
        eta_str = f"~{fmt_duration(remaining)}"

    bar = progress_bar(pct)

    return (
        f"{printer_badge(user_id)}"
        f"{t('status.title', L)}\n\n"
        f"{t('status.state', L)}: {state_icon(state)}\n"
        f"{t('status.file', L)}: `{filename}`\n\n"
        f"{t('status.progress', L)}: `[{bar}]` {pct:.1f}%\n"
        f"{t('status.duration', L)}: {fmt_duration(duration)}\n"
        f"{t('status.eta', L)}: {eta_str}\n"
        f"{t('status.filament', L)}: {filament:.2f} m\n\n"
        f"🌡️ {t('status.hotend', L)}: {ext.get('temperature', 0):.1f}°C → {ext.get('target', 0):.0f}°C\n"
        f"🌡️ {t('status.bed', L)}: {bed.get('temperature', 0):.1f}°C → {bed.get('target', 0):.0f}°C"
    )


def _status_keyboard(auto_active: bool) -> InlineKeyboardMarkup:
    L = lang()
    toggle_key = "status.auto_on" if auto_active else "status.auto_off"
    return InlineKeyboardMarkup([
        [btn(t("btn.refresh", L), "menu:status"), btn(t("btn.snapshot", L), "action:snapshot_inline")],
        [btn(t(toggle_key, L), "status:toggle_auto")],
        [btn(t("btn.back_menu", L), "menu:main")],
    ])


@auth_cb
async def cb_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = uid(update)

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
            res = await api.printer_status(user_id=user_id)
            if not res:
                continue

            text = _build_status_text(res, user_id)

            # Only edit if content actually changed (avoid Telegram API errors)
            if text == last_text:
                continue
            last_text = text

            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=msg_id,
                    text=text,
                    reply_markup=_status_keyboard(True),
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
