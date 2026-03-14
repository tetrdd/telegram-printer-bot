"""Camera — snapshot and live stream."""
from __future__ import annotations

from io import BytesIO
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import lang
from lang import t
from helpers import auth_cb, btn, uid, btn_url, offline_guard
from config import active_camera
import api


@auth_cb
async def cb_camera(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    L = lang()
    user_id = uid(update)

    if await offline_guard(q, user_id):
        return

    cam = active_camera(user_id)
    snap_url = cam.get("snapshot_url", "")
    stream_url = cam.get("stream_url", "")

    if not snap_url and not stream_url:
        await q.edit_message_text(
            t("camera.no_config", L),
            reply_markup=InlineKeyboardMarkup([[btn(t("btn.back_menu", L), "menu:main")]]),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    img = await api.snapshot(user_id=user_id)
    if img:
        kb_rows = [[btn(t("camera.new_snapshot", L), "action:snapshot")]]
        if stream_url:
            kb_rows.append([btn_url(t("camera.stream", L), stream_url)])
        kb_rows.append([btn(t("btn.back_menu", L), "menu:main")])

        await q.message.reply_photo(
            photo=BytesIO(img),
            caption=t("camera.snapshot", L),
            reply_markup=InlineKeyboardMarkup(kb_rows),
        )
        try:
            await q.delete_message()
        except Exception:
            pass
    else:
        kb = [[btn(t("camera.retry", L), "menu:camera"), btn(t("btn.back_menu", L), "menu:main")]]
        if stream_url:
            kb.insert(0, [btn_url(t("camera.stream", L), stream_url)])
        await q.edit_message_text(
            f"{t('camera.title', L)}\n\n{t('camera.failed', L)}",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode=ParseMode.MARKDOWN,
        )


@auth_cb
async def cb_snapshot_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """New snapshot from a photo message button."""
    q = update.callback_query
    await q.answer(t("camera.capturing", lang()))
    L = lang()
    user_id = uid(update)

    img = await api.snapshot(user_id=user_id)
    if img:
        cam = active_camera(user_id)
        stream_url = cam.get("stream_url", "")
        kb_rows = [[btn(t("camera.new_snapshot", L), "action:snapshot")]]
        if stream_url:
            kb_rows.append([btn_url(t("camera.stream", L), stream_url)])
        kb_rows.append([btn(t("btn.back_menu", L), "menu:main")])

        await q.message.reply_photo(
            photo=BytesIO(img),
            caption=t("camera.snapshot", L),
            reply_markup=InlineKeyboardMarkup(kb_rows),
        )
    else:
        await q.message.reply_text(t("camera.failed", L))


@auth_cb
async def cb_snapshot_inline(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Quick snapshot from status dashboard."""
    q = update.callback_query
    await q.answer(t("camera.capturing", lang()))
    user_id = uid(update)

    img = await api.snapshot(user_id=user_id)
    if img:
        await q.message.reply_photo(photo=BytesIO(img), caption=t("camera.snapshot", lang()))
    else:
        await q.message.reply_text(t("camera.failed", lang()))
