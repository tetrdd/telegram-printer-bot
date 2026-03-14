"""System info — versions, CPU, RAM, uptime, restart controls."""
from __future__ import annotations

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import lang
from lang import t
from helpers import auth_cb, btn, uid, offline_guard
import api


@auth_cb
async def cb_system(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = uid(update)
    L = lang()

    if await offline_guard(q, user_id):
        return

    srv = await api.server_info(user_id=user_id)
    sys_info = await api.system_info(user_id=user_id)
    proc = await api.proc_stats(user_id=user_id)

    lines = [f"{t('system.title', L)}\n"]

    if srv:
        klipper_v = srv.get("klippy_state", "?")
        moonraker_v = srv.get("moonraker_version", "?")
        lines.append(f"{t('system.klipper', L)}: `{klipper_v}`")
        lines.append(f"{t('system.moonraker', L)}: `{moonraker_v}`")

    if sys_info:
        cpu_info = sys_info.get("cpu_info", {})
        cpu_name = cpu_info.get("cpu_desc", "?")
        sd_info = sys_info.get("sd_info", {})
        total_mb = sd_info.get("total_bytes", 0) // (1024 * 1024)
        avail_mb = sd_info.get("available_bytes", 0) // (1024 * 1024)
        lines.append(f"{t('system.cpu', L)}: `{cpu_name}`")
        lines.append(f"{t('system.disk', L)}: `{avail_mb} MB free / {total_mb} MB`")

    if proc:
        moonraker_proc = proc.get("moonraker_stats", [{}])[-1] if proc.get("moonraker_stats") else {}
        cpu_pct = moonraker_proc.get("cpu_usage", 0)
        mem_mb = moonraker_proc.get("memory", 0) / 1024
        uptime = proc.get("system_uptime", 0)
        lines.append(f"{t('system.cpu_usage', L)}: `{cpu_pct:.1f}%`")
        lines.append(f"{t('system.mem', L)}: `{mem_mb:.0f} MB`")
        h = int(uptime // 3600)
        m = int((uptime % 3600) // 60)
        lines.append(f"{t('system.uptime', L)}: `{h}h {m}m`")

    keyboard = [
        [
            btn(t("system.fw_restart", L), "sys:fw_restart"),
            btn(t("system.host_restart", L), "sys:host_restart"),
        ],
        [btn(t("btn.refresh", L), "menu:system"), btn(t("btn.back_menu", L), "menu:main")],
    ]

    await q.edit_message_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_sys_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    action = q.data.split(":")[1]
    user_id = uid(update)
    L = lang()

    keyboard = [
        [
            btn(t("system.confirm_yes", L), f"sys_confirm:{action}"),
            btn(t("system.confirm_no", L), "menu:system"),
        ]
    ]
    await q.answer()
    await q.edit_message_text(
        t("system.confirm", L).format(action=action.replace("_", " ")),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


@auth_cb
async def cb_sys_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    action = q.data.split(":")[1]
    user_id = uid(update)
    await q.answer()

    if await offline_guard(q, user_id):
        return

    L = lang()
    if action == "fw_restart":
        await api.firmware_restart(user_id=user_id)
        msg = t("system.fw_restarted", L)
    elif action == "host_restart":
        await api.host_reboot(user_id=user_id)
        msg = t("system.host_restarted", L)
    else:
        msg = "?"

    keyboard = [[btn(t("btn.back_menu", L), "menu:main")]]
    await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
