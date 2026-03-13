"""Print history handler — shows last N completed prints from Moonraker."""

import math
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import lang
from lang import t
from helpers import auth_cb, btn, uid, fmt_duration, short_name, offline_guard
import api

_PER_PAGE = 10
_HISTORY_LIMIT = 50  # How many jobs to fetch from Moonraker


def _status_icon(status: str) -> str:
    icons = {
        "completed": "✅",
        "error": "❌",
        "cancelled": "🟠",
        "in_progress": "🖨️",
    }
    return icons.get(status, "❓")


def _format_date(timestamp: float) -> str:
    if not timestamp:
        return "—"
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%d.%m %H:%M")
    except Exception:
        return "—"


@auth_cb
async def cb_history(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = uid(update)
    L = lang()

    if await offline_guard(q, user_id):
        return

    jobs = await api.print_history(limit=_HISTORY_LIMIT, user_id=user_id)

    if not jobs:
        await q.edit_message_text(
            f"{t('history.title', L)}\n\n{t('history.empty', L)}",
            reply_markup=InlineKeyboardMarkup([
                [btn(t("menu.status", L), "menu:status"), btn(t("btn.back_menu", L), "menu:main")],
            ]),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    total_pages = math.ceil(len(jobs) / _PER_PAGE)
    await _show_history_page(q, jobs, page=0, total_pages=total_pages, L=L)


@auth_cb
async def cb_history_page(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = uid(update)
    L = lang()

    if await offline_guard(q, user_id):
        return

    # Pattern: history:page:N
    try:
        page = int(q.data.split(":")[2])
    except (IndexError, ValueError):
        page = 0

    jobs = await api.print_history(limit=_HISTORY_LIMIT, user_id=user_id)

    if not jobs:
        await q.edit_message_text(
            f"{t('history.title', L)}\n\n{t('history.empty', L)}",
            reply_markup=InlineKeyboardMarkup([
                [btn(t("menu.status", L), "menu:status"), btn(t("btn.back_menu", L), "menu:main")],
            ]),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    total_pages = math.ceil(len(jobs) / _PER_PAGE)
    page = max(0, min(page, total_pages - 1))
    await _show_history_page(q, jobs, page=page, total_pages=total_pages, L=L)


async def _show_history_page(q, jobs: list, page: int, total_pages: int, L: str):
    page_jobs = jobs[page * _PER_PAGE : (page + 1) * _PER_PAGE]

    lines = [t("history.title", L), ""]

    for job in page_jobs:
        status = job.get("status", "unknown")
        filename = job.get("filename", "—") or "—"
        duration = job.get("total_duration", 0)
        start_time = job.get("start_time", 0)

        icon = _status_icon(status)
        display_name = short_name(filename, 35)
        date_str = _format_date(start_time)
        dur_str = fmt_duration(duration)

        entry = t("history.entry", L).format(
            status=icon,
            filename=display_name,
            duration=dur_str,
            date=date_str,
        )
        lines.append(entry)
        lines.append("")  # spacing between entries

    text = "\n".join(lines).rstrip()

    # Pagination nav
    nav = []
    if page > 0:
        nav.append(btn(t("files.prev", L), f"history:page:{page - 1}"))
    if page < total_pages - 1:
        nav.append(btn(t("files.next", L), f"history:page:{page + 1}"))

    keyboard = []
    if nav:
        keyboard.append(nav)
    keyboard.append([
        btn(t("menu.status", L), "menu:status"),
        btn(t("btn.back_menu", L), "menu:main"),
    ])

    await q.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN,
    )
