"""Print control — pause, resume, cancel, home, motors off."""

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import lang
from lang import t
from helpers import auth_cb, btn, uid, state_icon, printer_badge, offline_guard
import api


@auth_cb
async def cb_print_ctrl(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    L = lang()
    user_id = uid(update)

    if await offline_guard(q, user_id):
        return

    data = await api.get("/printer/objects/query?print_stats", user_id=user_id)
    state = "unknown"
    if data:
        state = data.get("result", {}).get("status", {}).get("print_stats", {}).get("state", "unknown")

    buttons = []
    if state == "printing":
        buttons.append([btn(t("ctrl.pause", L), "ctrl:pause")])
        buttons.append([btn(t("ctrl.cancel", L), "ctrl:cancel")])
    elif state == "paused":
        buttons.append([btn(t("ctrl.resume", L), "ctrl:resume")])
        buttons.append([btn(t("ctrl.cancel", L), "ctrl:cancel")])
    else:
        buttons.append([btn(t("ctrl.browse", L), "menu:files")])

    buttons.append([btn(t("ctrl.home", L), "ctrl:home"), btn(t("ctrl.motors_off", L), "ctrl:motors_off")])
    buttons.append([btn(t("btn.back_menu", L), "menu:main")])

    await q.edit_message_text(
        f"{printer_badge(user_id)}{t('ctrl.title', L)}\n\n{t('status.state', L)}: {state_icon(state)}",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_ctrl_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    action = q.data.split(":")[1]
    L = lang()
    user_id = uid(update)

    actions = {
        "pause": (api.pause_print, t("ctrl.paused", L)),
        "resume": (api.resume_print, t("ctrl.resumed", L)),
        "home": (api.gcode, t("ctrl.homing", L)),
        "motors_off": (api.gcode, t("ctrl.motors_disabled", L)),
    }

    func, msg = actions.get(action, (None, None))
    if func:
        if action == "home":
            r = await func("G28", user_id=user_id)
        elif action == "motors_off":
            r = await func("M84", user_id=user_id)
        else:
            r = await func(user_id=user_id)
        await q.answer(msg if r else t("generic.failed", L), show_alert=True)

    await cb_print_ctrl(update, ctx)


@auth_cb
async def cb_ctrl_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    L = lang()

    await q.edit_message_text(
        t("ctrl.cancel_confirm", L),
        reply_markup=InlineKeyboardMarkup([
            [btn(t("ctrl.yes_cancel", L), "ctrl_confirm:cancel"), btn(t("ctrl.no_keep", L), "ctrl_confirm:keep")],
        ]),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_ctrl_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    action = q.data.split(":")[1]
    L = lang()
    user_id = uid(update)

    if action == "cancel":
        r = await api.cancel_print(user_id=user_id)
        await q.answer(t("ctrl.cancelled", L) if r else t("generic.failed", L), show_alert=True)
    else:
        await q.answer("👍")

    await cb_print_ctrl(update, ctx)
