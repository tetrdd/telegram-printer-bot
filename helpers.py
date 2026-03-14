"""
Shared helpers: auth decorators, formatting functions, button builders.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta, timezone
from functools import wraps
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import allowed_users, lang, is_multi_printer, active_printer_name
from lang import t

logger = logging.getLogger("PrinterBot.helpers")


# ══════════════════════════════════════════════════════════════════════════════
#  AUTH DECORATORS
# ══════════════════════════════════════════════════════════════════════════════

def auth(func):
    """Authorize command handlers (messages)."""
    @wraps(func)
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in allowed_users():
            await update.message.reply_text("⛔ Not authorized.")
            return
        return await func(update, ctx)
    return wrapper


def auth_cb(func):
    """Authorize callback query handlers (button presses)."""
    @wraps(func)
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in allowed_users():
            await update.callback_query.answer("⛔ Not authorized.", show_alert=True)
            return
        return await func(update, ctx)
    return wrapper


# ══════════════════════════════════════════════════════════════════════════════
#  USER ID HELPER
# ══════════════════════════════════════════════════════════════════════════════

def uid(update: Update) -> int:
    """Extract user ID from any update type."""
    return update.effective_user.id


# ══════════════════════════════════════════════════════════════════════════════
#  FORMATTING
# ══════════════════════════════════════════════════════════════════════════════

def progress_bar(pct: float, length: int = 20) -> str:
    filled = int(length * pct / 100)
    return "█" * filled + "░" * (length - filled)


def fmt_duration(seconds: float) -> str:
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    if h > 0:
        return f"{h}h {m}m {s}s"
    if m > 0:
        return f"{m}m {s}s"
    return f"{s}s"


def fmt_size(bytes_val: float) -> str:
    if bytes_val >= 1024 ** 3:
        return f"{bytes_val / 1024**3:.1f} GB"
    if bytes_val >= 1024 ** 2:
        return f"{bytes_val / 1024**2:.1f} MB"
    if bytes_val >= 1024:
        return f"{bytes_val / 1024:.1f} KB"
    return f"{bytes_val:.0f} B"


def state_icon(state: str) -> str:
    """Get localized printer state string."""
    key = f"state.{state}"
    result = t(key, lang())
    if result == f"[{key}]":
        return f"❓ {state}"
    return result


def short_name(name: str, max_len: int = 30) -> str:
    """Truncate filename for display."""
    if len(name) <= max_len:
        return name
    return "..." + name[-(max_len - 3):]


def printer_badge(user_id: int) -> str:
    """Return a printer name badge if multi-printer is enabled."""
    if is_multi_printer():
        name = active_printer_name(user_id)
        return f"🖨️ *{name}*\n"
    return ""


def fmt_clock_eta(remaining_seconds: float) -> str:
    """Format ETA as a wall-clock time, e.g. '~15:30'."""
    if remaining_seconds <= 0:
        return "—"
    eta = datetime.now() + timedelta(seconds=remaining_seconds)
    return f"~{eta.strftime('%H:%M')}"


def fmt_time_ago(timestamp: float) -> str:
    """Format a Unix timestamp as '3m ago', '2h ago', etc."""
    if timestamp <= 0:
        return "—"
    delta = time.time() - timestamp
    if delta < 60:
        return f"{int(delta)}s ago"
    if delta < 3600:
        return f"{int(delta / 60)}m ago"
    if delta < 86400:
        return f"{int(delta / 3600)}h ago"
    return f"{int(delta / 86400)}d ago"


async def offline_guard(query, user_id: int) -> bool:
    """
    Check if the user's active printer is offline.
    If offline, shows an offline message and returns True (= blocked).
    If online, returns False (= proceed).
    """
    from monitor import is_printer_online
    if is_printer_online(user_id):
        return False

    L = lang()
    await query.edit_message_text(
        t("offline.blocked", L),
        reply_markup=InlineKeyboardMarkup([
            [btn(t("menu.status", L), "menu:status")],
            [btn(t("btn.back_menu", L), "menu:main")],
        ]),
        parse_mode="Markdown",
    )
    return True


# ══════════════════════════════════════════════════════════════════════════════
#  BUTTON BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

def btn(text: str, data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text, callback_data=data)


def btn_url(text: str, url: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text, url=url)


def grid(buttons: list[InlineKeyboardButton], cols: int = 2) -> list[list[InlineKeyboardButton]]:
    """Arrange flat list of buttons into a grid."""
    return [buttons[i : i + cols] for i in range(0, len(buttons), cols)]


def back_menu_btn() -> InlineKeyboardButton:
    return btn(t("btn.back_menu", lang()), "menu:main")


def refresh_btn(target: str) -> InlineKeyboardButton:
    return btn(t("btn.refresh", lang()), target)
