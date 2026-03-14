"""Print history handler — shows last N completed prints from Moonraker."""
from __future__ import annotations

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import lang
from lang import t
from helpers import auth_cb, btn, uid, fmt_duration, offline_guard
import api

HISTORY_PAGE_SIZE = 5


async def _show_history(q, user_id: int, page: int = 0):
    L = lang()

    limit = HISTORY_PAGE_SIZE * 10  # fetch more, paginate client-side
    jobs = await api.print_history(limit=limit, user_id=user_id)

    total = len(jobs)
    pages = max(1, (total + HISTORY_PAGE_SIZE - 1) // HISTORY_PAGE_SIZE)
    page = max(0, min(page, pages - 1))
    chunk = jobs[page * HISTORY_PAGE_SIZE: (page + 1) * HISTORY_PAGE_SIZE]

    lines = [f"{t('history.title', L)} ({total} {t('history.total', L)})\n"]
    for job in chunk:
        fname = job.get("filename", "?")
        status = job.get("status", "?")
        dur = fmt_duration(job.get("total_duration", 0))
        lines.append(f"• `{fname}` — {status} ({dur})")

    text = "\n".join(lines)
    nav = []
    if page > 0:
        nav.append(btn(t("btn.prev", L), f"history:page:{page-1}"))
    if page < pages - 1:
        nav.append(btn(t("btn.next", L), f"history:page:{page+1}"))

    keyboard = []
    if nav:
        keyboard.append(nav)
    keyboard.append([btn(t("btn.refresh", L), f"history:page:{page}"), btn(t("btn.back_menu", L), "menu:main")])

    await q.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_history(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = uid(update)

    if await offline_guard(q, user_id):
        return

    await _show_history(q, user_id, page=0)


@auth_cb
async def cb_history_page(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = uid(update)
    page = int(q.data.split(":")[2])

    if await offline_guard(q, user_id):
        return

    await _show_history(q, user_id, page=page)
