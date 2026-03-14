"""Print control — pause, resume, cancel, home, motors off."""
from __future__ import annotations

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import lang
from lang import t
from helpers import auth_cb, btn, uid, offline_guard
import api


async def _show_control(q, user_id: int, msg: str = ""):
    L = lang()
    status = await api.printer_status(user_id=user_id)
    if status is None:
        await q.edit_message_text(
            t("status.offline", L),
            reply_markup=InlineKeyboardMarkup([[btn(t("btn.back_menu", L), "menu:main")]]),
        )
        return

    ps = status.get("print_stats", {})
    state = ps.get("state", "unknown")
    fname = ps.get("filename", "-")
    ds = status.get("display_status", {})
    progress = ds.get("progress", 0) * 100

    text = (
        f"{t('control.title', L)}\n\n"
        f"{t('status.file', L)}: `{fname}`\n"
        f"{t('status.state', L)}: `{state}`\n"
        f"{t('status.progress', L)}: `{progress:.1f}%`"
    )
    if msg:
        text += f"\n\n✅ {msg}"

    printing = state == "printing"
    paused = state == "paused"

    keyboard = []
    if printing:
        keyboard.append([btn(t("control.pause", L), "ctrl:pause")])
    if paused:
        keyboard.append([btn(t("control.resume", L), "ctrl:resume")])
    if printing or paused:
        keyboard.append([btn(t("control.cancel", L), "ctrl:cancel")])

    keyboard.append([
        btn(t("control.home", L), "ctrl:home"),
        btn(t("control.motors_off", L), "ctrl:motors_off"),
    ])
    keyboard.append([btn(t("btn.refresh", L), "menu:control"), btn(t("btn.back_menu", L), "menu:main")])

    await q.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_print_ctrl(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = uid(update)

    if await offline_guard(q, user_id):
        return

    await _show_control(q, user_id)


@auth_cb
async def cb_ctrl_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    action = q.data.split(":")[1]
    user_id = uid(update)
    await q.answer()

    if await offline_guard(q, user_id):
        return

    L = lang()
    msg = ""
    if action == "pause":
        if await api.pause_print(user_id=user_id):
            msg = t("control.paused", L)
    elif action == "resume":
        if await api.resume_print(user_id=user_id):
            msg = t("control.resumed", L)
    elif action == "home":
        if await api.gcode("G28", user_id=user_id):
            msg = t("control.homed", L)
    elif action == "motors_off":
        if await api.gcode("M18", user_id=user_id):
            msg = t("control.motors_off_done", L)

    await _show_control(q, user_id, msg=msg)


@auth_cb
async def cb_ctrl_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Ask for confirmation before cancelling."""
    q = update.callback_query
    await q.answer()
    L = lang()
    keyboard = [
        [
            btn(t("control.cancel_yes", L), "ctrl_confirm:cancel"),
            btn(t("control.cancel_no", L), "menu:control"),
        ]
    ]
    await q.edit_message_text(
        t("control.cancel_confirm", L),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


@auth_cb
async def cb_ctrl_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    action = q.data.split(":")[1]
    user_id = uid(update)
    await q.answer()

    if await offline_guard(q, user_id):
        return

    L = lang()
    msg = ""
    if action == "cancel":
        if await api.cancel_print(user_id=user_id):
            msg = t("control.cancelled", L)

    await _show_control(q, user_id, msg=msg)
