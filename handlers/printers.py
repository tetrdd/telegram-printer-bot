"""Printer selector — switch between configured printers."""

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import (
    lang, printers, active_printer_for, set_active_printer,
    active_printer_name, active_moonraker_url,
)
from lang import t
from helpers import auth_cb, btn, uid
import api


@auth_cb
async def cb_printers(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show list of printers to switch between."""
    q = update.callback_query
    await q.answer()
    L = lang()
    user_id = uid(update)

    active = active_printer_for(user_id)
    all_printers = printers()

    buttons = []
    for p in all_printers:
        marker = "✅ " if p["id"] == active["id"] else ""
        buttons.append([btn(
            f"{marker}{p['name']}",
            f"printer:select:{p['id']}",
        )])
    buttons.append([btn(t("btn.back_menu", L), "menu:main")])

    await q.edit_message_text(
        t("printers.title", L),
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_printer_select(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Switch to the selected printer."""
    q = update.callback_query
    user_id = uid(update)
    printer_id = int(q.data.split(":")[2])

    set_active_printer(user_id, printer_id)
    name = active_printer_name(user_id)

    await q.answer(f"🖨️ {name}", show_alert=True)

    from handlers.menu import show_menu
    await show_menu(q, user_id)


@auth_cb
async def cb_printer_status_all(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show a quick status overview of all printers."""
    q = update.callback_query
    await q.answer()
    L = lang()
    user_id = uid(update)

    all_printers = printers()
    lines = [t("printers.overview", L), ""]

    for p in all_printers:
        # Quick status check for each printer
        res = await api.printer_status(user_id=None)
        # Use direct URL for each printer
        import aiohttp
        url = p["moonraker"].get("url", "").rstrip("/")
        key = p["moonraker"].get("api_key", "")
        headers = {"Content-Type": "application/json"}
        if key:
            headers["X-Api-Key"] = key

        state = "⚫ offline"
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(
                    f"{url}/printer/objects/query?print_stats&extruder&heater_bed",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as r:
                    if r.status == 200:
                        data = await r.json()
                        status = data.get("result", {}).get("status", {})
                        ps = status.get("print_stats", {})
                        ext = status.get("extruder", {})
                        bed = status.get("heater_bed", {})
                        s_state = ps.get("state", "unknown")

                        icons = {
                            "printing": "🟢", "paused": "🟡", "complete": "🔵",
                            "standby": "⚪", "error": "🔴", "ready": "⚪",
                        }
                        icon = icons.get(s_state, "❓")
                        state = (
                            f"{icon} {s_state}"
                            f" | 🌡️ {ext.get('temperature', 0):.0f}°C"
                            f" / {bed.get('temperature', 0):.0f}°C"
                        )
                        if s_state == "printing":
                            pct = status.get("display_status", {}).get("progress", 0) * 100
                            state += f" | {pct:.0f}%"
        except Exception:
            pass

        active = active_printer_for(user_id)
        marker = "→ " if p["id"] == active["id"] else "   "
        lines.append(f"{marker}*{p['name']}*: {state}")

    buttons = []
    for p in all_printers:
        buttons.append([btn(f"🔀 {p['name']}", f"printer:select:{p['id']}")])
    buttons.append([btn(t("btn.back_menu", L), "menu:main")])

    await q.edit_message_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.MARKDOWN,
    )
