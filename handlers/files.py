"""Paginated file browser — browse, info, print, delete."""
from __future__ import annotations

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import lang
from lang import t
from helpers import auth_cb, btn, uid, fmt_size, fmt_duration, offline_guard
import api

PAGE_SIZE = 8


def _sort_files(files: list[dict], sort: str) -> list[dict]:
    if sort == "name":
        return sorted(files, key=lambda f: f.get("filename", "").lower())
    if sort == "size":
        return sorted(files, key=lambda f: f.get("size", 0), reverse=True)
    # default: date
    return sorted(files, key=lambda f: f.get("modified", 0), reverse=True)


async def _show_files(q, user_id: int, page: int = 0, sort: str = "date"):
    L = lang()
    files = await api.file_list(user_id=user_id)
    files = _sort_files(files, sort)

    total = len(files)
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(0, min(page, pages - 1))
    chunk = files[page * PAGE_SIZE: (page + 1) * PAGE_SIZE]

    text = f"{t('files.title', L)} ({total} {t('files.files', L)}, {t('files.page', L)} {page+1}/{pages})"

    keyboard = []
    for f in chunk:
        name = f.get("filename", "?")
        size = fmt_size(f.get("size", 0))
        keyboard.append([btn(f"📄 {name} ({size})", f"file:info:{name}")])

    # Pagination
    nav = []
    if page > 0:
        nav.append(btn(t("btn.prev", L), f"files:page:{page-1}:{sort}"))
    nav.append(btn(f"{t('files.sort', L)}: {sort}", f"files:sort:{sort}"))
    if page < pages - 1:
        nav.append(btn(t("btn.next", L), f"files:page:{page+1}:{sort}"))
    if nav:
        keyboard.append(nav)

    keyboard.append([btn(t("btn.refresh", L), f"files:page:{page}:{sort}"), btn(t("btn.back_menu", L), "menu:main")])

    await q.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


@auth_cb
async def cb_files(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = uid(update)
    # Pattern: files:page:<page>:<sort>
    parts = q.data.split(":")
    page = int(parts[2]) if len(parts) > 2 else 0
    sort = parts[3] if len(parts) > 3 else "date"

    if await offline_guard(q, user_id):
        return

    await _show_files(q, user_id, page=page, sort=sort)


@auth_cb
async def cb_file_sort(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Cycle through sort modes."""
    q = update.callback_query
    await q.answer()
    user_id = uid(update)
    parts = q.data.split(":")
    current = parts[2] if len(parts) > 2 else "date"
    sorts = ["date", "name", "size"]
    next_sort = sorts[(sorts.index(current) + 1) % len(sorts)]

    if await offline_guard(q, user_id):
        return

    await _show_files(q, user_id, page=0, sort=next_sort)


@auth_cb
async def cb_file_info(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show file metadata with print/delete options."""
    q = update.callback_query
    await q.answer()
    user_id = uid(update)
    filename = q.data[len("file:info:"):]
    L = lang()

    meta = await api.file_metadata(filename, user_id=user_id)

    if meta:
        size = fmt_size(meta.get("size", 0))
        filament = meta.get("filament_total", 0)
        est = meta.get("estimated_time", 0)
        layer_h = meta.get("layer_height", "-")
        slicer = meta.get("slicer", "-")

        text = (
            f"📄 `{filename}`\n\n"
            f"{t('files.size', L)}: {size}\n"
            f"{t('files.filament', L)}: {filament:.0f} mm\n"
            f"{t('files.time', L)}: {fmt_duration(est)}\n"
            f"{t('files.layer', L)}: {layer_h} mm\n"
            f"{t('files.slicer', L)}: {slicer}"
        )
    else:
        text = f"📄 `{filename}`"

    keyboard = [
        [btn(t("files.print", L), f"file:print:{filename}")],
        [btn(t("files.delete", L), f"file:delete_ask:{filename}")],
        [btn(t("btn.back", L), "files:page:0:date")],
    ]

    await q.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_file_print(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Confirm before starting a print."""
    q = update.callback_query
    await q.answer()
    user_id = uid(update)
    filename = q.data[len("file:print:"):]
    L = lang()

    keyboard = [
        [
            btn(t("files.print_yes", L), f"file:start:{filename}"),
            btn(t("files.print_no", L), f"file:info:{filename}"),
        ]
    ]
    await q.edit_message_text(
        t("files.print_confirm", L).format(name=filename),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


@auth_cb
async def cb_file_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Start a print job."""
    q = update.callback_query
    await q.answer()
    user_id = uid(update)
    filename = q.data[len("file:start:"):]
    L = lang()

    ok = await api.start_print(filename, user_id=user_id)
    text = (
        t("files.print_started", L).format(name=filename)
        if ok
        else t("files.print_failed", L).format(name=filename)
    )
    keyboard = [[btn(t("btn.back_menu", L), "menu:main")]]
    await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


@auth_cb
async def cb_file_delete_ask(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Ask for confirmation before deleting."""
    q = update.callback_query
    await q.answer()
    user_id = uid(update)
    filename = q.data[len("file:delete_ask:"):]
    L = lang()

    keyboard = [
        [
            btn(t("files.delete_yes", L), f"file:delete:{filename}"),
            btn(t("files.delete_no", L), f"file:info:{filename}"),
        ]
    ]
    await q.edit_message_text(
        t("files.delete_confirm", L).format(name=filename),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


@auth_cb
async def cb_file_delete(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Delete a file."""
    q = update.callback_query
    await q.answer()
    user_id = uid(update)
    filename = q.data[len("file:delete:"):]
    L = lang()

    ok = await api.delete_file(filename, user_id=user_id)
    text = (
        t("files.deleted", L).format(name=filename)
        if ok
        else t("files.delete_failed", L).format(name=filename)
    )
    keyboard = [[btn(t("btn.back", L), "files:page:0:date")]]
    await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
