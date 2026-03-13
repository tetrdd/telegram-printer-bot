"""
Shared helpers: auth decorators, formatting functions, button builders.
"""

import logging
from functools import wraps
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import allowed_users, lang
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
