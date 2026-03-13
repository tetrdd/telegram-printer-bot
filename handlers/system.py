"""System info — versions, CPU, RAM, uptime, restart controls."""

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import lang
from lang import t
from helpers import auth_cb, btn, fmt_size, fmt_duration
import api


@auth_cb
async def cb_system(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    L = lang()

    info = await api.system_info()
    proc = await api.proc_stats()
    server = await api.server_info()

    text = t("system.title", L) + "\n"

    if server:
        text += f"\nMoonraker: v{server.get('moonraker_version', '?')}"
        text += f"\nKlipper: {server.get('klippy_state', '?')}"
        text += f"\nAPI: {server.get('api_version_string', '?')}"

    if info:
        cpu = info.get("cpu_info", {})
        if cpu:
            text += f"\n\nCPU: {cpu.get('model', '?')}"
            text += f"\nCores: {cpu.get('cpu_count', '?')}"

    if proc:
        cpu_pct = proc.get("system_cpu_usage", {}).get("cpu", 0)
        mem_used = proc.get("system_memory", {}).get("used", 0)
        mem_total = proc.get("system_memory", {}).get("total", 0)
        uptime = proc.get("system_uptime", 0)

        text += f"\n\n📈 CPU: {cpu_pct:.1f}%"
        if mem_total:
            text += f"\n💾 RAM: {fmt_size(mem_used)} / {fmt_size(mem_total)}"
        text += f"\n⏱️ Uptime: {fmt_duration(uptime)}"

        throttle = proc.get("throttled_state", {})
        if throttle:
            flags = throttle.get("flags", [])
            if flags:
                text += f"\n⚠️ Throttle: {', '.join(flags)}"

    kb = InlineKeyboardMarkup([
        [btn(t("btn.refresh", L), "menu:system")],
        [btn(t("system.fw_restart", L), "sys:fw_restart"), btn(t("system.host_restart", L), "sys:host_restart")],
        [btn(t("btn.back_menu", L), "menu:main")],
    ])
    await q.edit_message_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)


@auth_cb
async def cb_sys_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    action = q.data.split(":")[1]
    await q.answer()
    L = lang()

    confirm_texts = {
        "fw_restart": t("system.fw_confirm", L),
        "host_restart": t("system.host_confirm", L),
    }
    labels = {
        "fw_restart": t("system.fw_restart", L),
        "host_restart": t("system.host_restart", L),
    }

    await q.edit_message_text(
        confirm_texts.get(action, "?"),
        reply_markup=InlineKeyboardMarkup([
            [btn(labels.get(action, "?"), f"sys_confirm:{action}"), btn(t("btn.cancel", L), "menu:system")],
        ]),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_sys_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    action = q.data.split(":")[1]
    L = lang()

    funcs = {"fw_restart": api.firmware_restart, "host_restart": api.host_reboot}
    func = funcs.get(action)
    if func:
        r = await func()
        await q.answer(t("generic.done", L) if r else t("generic.failed", L), show_alert=True)

    from handlers.menu import show_menu
    await show_menu(q)
