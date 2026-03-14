"""
Shared helpers: auth decorators, formatting functions, button factory.
"""
from __future__ import annotations

import functools
from telegram import InlineKeyboardButton, Update
from telegram.ext import ContextTypes
from config import allowed_users, lang
from lang import t
import api


# ── Auth decorators ───────────────────────────────────────────────────────────

def auth(func):
    """Decorator: block non-allowed users from command handlers."""
    @functools.wraps(func)
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in allowed_users():
            await update.message.reply_text("⛔ Access denied.")
            return
        return await func(update, ctx)
    return wrapper


def auth_cb(func):
    """Decorator: block non-allowed users from callback query handlers."""
    @functools.wraps(func)
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in allowed_users():
            await update.callback_query.answer("⛔ Access denied.", show_alert=True)
            return
        return await func(update, ctx)
    return wrapper


def uid(update: Update) -> int:
    return update.effective_user.id


# ── Formatting ────────────────────────────────────────────────────────────────

def fmt_size(b: int) -> str:
    """Format byte count as human-readable string."""
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.0f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


def fmt_duration(s: float) -> str:
    """Format seconds as h:mm:ss."""
    s = int(s)
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    if h:
        return f"{h}h {m:02d}m {sec:02d}s"
    if m:
        return f"{m}m {sec:02d}s"
    return f"{sec}s"


# ── Keyboard helpers ──────────────────────────────────────────────────────────

def btn(text: str, callback_data: str) -> InlineKeyboardButton:
    """Shorthand for creating an InlineKeyboardButton."""
    return InlineKeyboardButton(text, callback_data=callback_data)


# ── Offline guard ─────────────────────────────────────────────────────────────

async def offline_guard(q, user_id: int) -> bool:
    """
    Check if the printer is online. If offline, edit the message and return True.
    Returns False if the printer is online.
    """
    status = await api.printer_status(user_id=user_id)
    if status is None:
        L = lang()
        from telegram import InlineKeyboardMarkup
        await q.edit_message_text(
            t("status.offline", L),
            reply_markup=InlineKeyboardMarkup([[btn(t("btn.back_menu", L), "menu:main")]]),
        )
        return True
    return False
