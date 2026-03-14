"""Camera — snapshot and live stream."""
from __future__ import annotations

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import lang, active_camera
from lang import t
from helpers import auth_cb, btn, uid, offline_guard
import api


@auth_cb
async def cb_camera(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show camera options (snapshot / stream link)."""
    q = update.callback_query
    await q.answer()
    user_id = uid(update)
    L = lang()

    cam = active_camera(user_id)
    stream_url = cam.get("stream_url", "")

    keyboard = [
        [btn(t("camera.snapshot", L), "action:snapshot")],
    ]
    if stream_url:
        keyboard.append([btn(t("camera.stream", L), f"noop")])

    keyboard.append([btn(t("btn.back_menu", L), "menu:main")])

    await q.edit_message_text(
        t("camera.title", L),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


@auth_cb
async def cb_snapshot_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Send a camera snapshot."""
    q = update.callback_query
    await q.answer(t("camera.fetching", lang()))
    user_id = uid(update)

    if await offline_guard(q, user_id):
        return

    img = await api.snapshot(user_id=user_id)
    if img:
        await update.effective_chat.send_photo(
            photo=img,
            caption=t("camera.caption", lang()),
        )
    else:
        await q.edit_message_text(
            t("camera.error", lang()),
            reply_markup=InlineKeyboardMarkup(
                [[btn(t("btn.back_menu", lang()), "menu:main")]]
            ),
        )


@auth_cb
async def cb_snapshot_inline(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Send a camera snapshot inline (from status menu)."""
    q = update.callback_query
    await q.answer(t("camera.fetching", lang()))
    user_id = uid(update)

    if await offline_guard(q, user_id):
        return

    img = await api.snapshot(user_id=user_id)
    if img:
        await update.effective_chat.send_photo(
            photo=img,
            caption=t("camera.caption", lang()),
        )
    else:
        await q.answer(t("camera.error", lang()), show_alert=True)
