"""Paginated file browser — browse, info, print, delete."""

import math
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import get as cfg, lang, save as save_cfg
from lang import t
from helpers import auth_cb, btn, uid, fmt_size, fmt_duration, short_name, printer_badge, offline_guard
import api


@auth_cb
async def cb_files(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    L = lang()
    user_id = uid(update)

    if await offline_guard(q, user_id):
        return

    page = 0
    if q.data.startswith("files:page:"):
        page = int(q.data.split(":")[2])

    files = await api.file_list(user_id=user_id)
    if not files:
        await q.edit_message_text(
            t("files.empty", L),
            reply_markup=InlineKeyboardMarkup([[btn(t("btn.back_menu", L), "menu:main")]]),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Sort
    sort_by = cfg().get("files", {}).get("sort_by", "modified")
    sort_order = cfg().get("files", {}).get("sort_order", "desc")
    files.sort(key=lambda f: f.get(sort_by, 0), reverse=(sort_order == "desc"))

    per_page = cfg().get("files", {}).get("files_per_page", 5)
    total_pages = math.ceil(len(files) / per_page)
    page = max(0, min(page, total_pages - 1))
    page_files = files[page * per_page : (page + 1) * per_page]

    lines = [f"{printer_badge(user_id)}{t('files.title', L).format(page=page + 1, total=total_pages)}\n"]
    buttons = []
    for i, f in enumerate(page_files):
        name = f.get("path", "unknown")
        size = fmt_size(f.get("size", 0))
        display = short_name(name)
        lines.append(f"`{page * per_page + i + 1}.` `{display}` ({size})")
        buttons.append([
            btn(f"🖨️ {display}", f"file:print:{name}"),
            btn("ℹ️", f"file:info:{name}"),
        ])

    # Pagination
    nav = []
    if page > 0:
        nav.append(btn(t("files.prev", L), f"files:page:{page - 1}"))
    if page < total_pages - 1:
        nav.append(btn(t("files.next", L), f"files:page:{page + 1}"))
    if nav:
        buttons.append(nav)

    # Sort toggle + back
    sort_label = t("files.by_date", L) if sort_by == "name" else t("files.by_name", L)
    next_sort = "name" if sort_by == "modified" else "modified"
    buttons.append([btn(sort_label, f"files:sort:{next_sort}"), btn(t("btn.back_menu", L), "menu:main")])

    await q.edit_message_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_file_sort(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    sort_by = q.data.split(":")[2]
    cfg().setdefault("files", {})["sort_by"] = sort_by
    save_cfg()
    await q.answer(f"{'\ud83d\udcc5' if sort_by == 'modified' else '\ud83d\udd24'}")
    q.data = "files:page:0"
    await cb_files(update, ctx)


@auth_cb
async def cb_file_info(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    filename = q.data[len("file:info:"):]
    await q.answer()
    L = lang()
    user_id = uid(update)

    meta = await api.file_metadata(filename, user_id=user_id)
    if not meta:
        await q.edit_message_text(
            f"❌ `{filename}`",
            reply_markup=InlineKeyboardMarkup([[btn(t("files.back", L), "menu:files")]]),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    size = fmt_size(meta.get("size", 0))
    est = fmt_duration(meta.get("estimated_time", 0))
    slicer = meta.get("slicer", "—")
    slicer_ver = meta.get("slicer_version", "")
    lh = meta.get("layer_height", "—")
    flh = meta.get("first_layer_height", "—")
    fil_m = meta.get("filament_total", 0) / 1000
    fil_g = meta.get("filament_weight_total", 0)
    obj_h = meta.get("object_height", "—")

    text = (
        f"{t('files.info_title', L)}\n\n"
        f"{t('files.name', L)}: `{filename}`\n"
        f"{t('files.size', L)}: {size}\n"
        f"{t('files.est_time', L)}: {est}\n"
        f"{t('files.slicer', L)}: {slicer} {slicer_ver}\n"
        f"{t('files.layer_height', L)}: {lh} mm\n"
        f"{t('files.first_layer', L)}: {flh} mm\n"
        f"{t('files.obj_height', L)}: {obj_h} mm\n"
        f"{t('files.filament_usage', L)}: {fil_m:.1f} m ({fil_g:.0f} g)"
    )

    kb = InlineKeyboardMarkup([
        [btn(t("files.print_this", L), f"file:print:{filename}")],
        [btn(t("files.delete", L), f"file:delete_ask:{filename}")],
        [btn(t("files.back", L), "menu:files"), btn(t("btn.back_menu", L), "menu:main")],
    ])
    await q.edit_message_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)


@auth_cb
async def cb_file_print(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    filename = q.data[len("file:print:"):]
    await q.answer()
    L = lang()

    await q.edit_message_text(
        t("files.start_confirm", L).format(filename=short_name(filename, 35)),
        reply_markup=InlineKeyboardMarkup([
            [btn(t("files.start_btn", L), f"file:start:{filename}"), btn(t("btn.cancel", L), "menu:files")],
        ]),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_file_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    filename = q.data[len("file:start:"):]
    L = lang()
    user_id = uid(update)

    ok = await api.start_print(filename, user_id=user_id)
    await q.answer(t("files.started", L) if ok else t("generic.failed", L), show_alert=True)

    from handlers.menu import show_menu
    await show_menu(q, user_id)


@auth_cb
async def cb_file_delete_ask(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    filename = q.data[len("file:delete_ask:"):]
    await q.answer()
    L = lang()

    await q.edit_message_text(
        t("files.delete_confirm", L).format(filename=filename),
        reply_markup=InlineKeyboardMarkup([
            [btn(t("files.delete_btn", L), f"file:delete:{filename}"), btn(t("files.keep_btn", L), f"file:info:{filename}")],
        ]),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_file_delete(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    filename = q.data[len("file:delete:"):]
    L = lang()
    user_id = uid(update)

    ok = await api.delete_file(filename, user_id=user_id)
    await q.answer(t("files.deleted", L) if ok else t("generic.failed", L), show_alert=True)
    q.data = "menu:files"
    await cb_files(update, ctx)
