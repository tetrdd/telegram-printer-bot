"""Temperature control — view, presets, custom input."""
from __future__ import annotations

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from config import lang, get as get_cfg
from lang import t
from helpers import auth_cb, btn, uid, offline_guard
import api

TEMP_CUSTOM_HOTEND = 10
TEMP_CUSTOM_BED = 11


async def _show_temps(q, user_id: int, msg: str = ""):
    L = lang()
    status = await api.printer_status(user_id=user_id)
    if status is None:
        await q.edit_message_text(
            t("status.offline", L),
            reply_markup=InlineKeyboardMarkup([[btn(t("btn.back_menu", L), "menu:main")]]),
        )
        return

    extruder = status.get("extruder", {})
    heater_bed = status.get("heater_bed", {})
    hotend_t = extruder.get("temperature", 0)
    hotend_target = extruder.get("target", 0)
    bed_t = heater_bed.get("temperature", 0)
    bed_target = heater_bed.get("target", 0)

    cfg = get_cfg()
    hotend_presets = cfg.get("temp_presets", {}).get("hotend", [200, 210, 220, 230, 240])
    bed_presets = cfg.get("temp_presets", {}).get("bed", [50, 60, 70, 80])

    text = (
        f"{t('temps.title', L)}\n\n"
        f"{t('status.hotend', L)}: `{hotend_t:.1f}°C / {hotend_target:.0f}°C`\n"
        f"{t('status.bed', L)}: `{bed_t:.1f}°C / {bed_target:.0f}°C`"
    )
    if msg:
        text += f"\n\n✅ {msg}"

    hotend_row = [btn(f"{p}°", f"set_temp:hotend:{p}") for p in hotend_presets]
    hotend_row.append(btn(t("temps.custom", L), "temp_custom:hotend"))

    bed_row = [btn(f"{p}°", f"set_temp:bed:{p}") for p in bed_presets]
    bed_row.append(btn(t("temps.custom", L), "temp_custom:bed"))

    keyboard = [
        hotend_row,
        bed_row,
        [btn(t("temps.cool_all", L), "temp:cool_all")],
        [btn(t("btn.refresh", L), "menu:temps"), btn(t("btn.back_menu", L), "menu:main")],
    ]

    await q.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_temps(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = uid(update)

    if await offline_guard(q, user_id):
        return

    await _show_temps(q, user_id)


@auth_cb
async def cb_temp_presets(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show presets for hotend or bed (pattern: temp:(hotend|bed))."""
    q = update.callback_query
    await q.answer()
    user_id = uid(update)

    if await offline_guard(q, user_id):
        return

    await _show_temps(q, user_id)


@auth_cb
async def cb_set_temp(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Pattern: set_temp:<hotend|bed>:<value>"""
    q = update.callback_query
    parts = q.data.split(":")
    heater = parts[1]
    target = int(parts[2])
    user_id = uid(update)
    await q.answer()

    if await offline_guard(q, user_id):
        return

    L = lang()
    if heater == "hotend":
        await api.gcode(f"M104 S{target}", user_id=user_id)
        msg = t("temps.set_hotend", L).format(val=target)
    else:
        await api.gcode(f"M140 S{target}", user_id=user_id)
        msg = t("temps.set_bed", L).format(val=target)

    await _show_temps(q, user_id, msg=msg)


@auth_cb
async def cb_cool_all(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = uid(update)

    if await offline_guard(q, user_id):
        return

    await api.gcode("M104 S0", user_id=user_id)
    await api.gcode("M140 S0", user_id=user_id)
    L = lang()
    await _show_temps(q, user_id, msg=t("temps.cooled", L))


@auth_cb
async def cb_temp_custom_hotend(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Entry point for custom hotend temp conversation."""
    q = update.callback_query
    await q.answer()
    L = lang()
    await q.edit_message_text(t("temps.enter_hotend", L))
    return TEMP_CUSTOM_HOTEND


@auth_cb
async def cb_temp_custom_bed(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Entry point for custom bed temp conversation."""
    q = update.callback_query
    await q.answer()
    L = lang()
    await q.edit_message_text(t("temps.enter_bed", L))
    return TEMP_CUSTOM_BED


async def handle_custom_hotend(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    from config import allowed_users
    if user_id not in allowed_users():
        return ConversationHandler.END
    try:
        target = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("Invalid temperature.")
        return TEMP_CUSTOM_HOTEND
    await api.gcode(f"M104 S{target}", user_id=user_id)
    L = lang()
    await update.message.reply_text(t("temps.set_hotend", L).format(val=target))
    return ConversationHandler.END


async def handle_custom_bed(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    from config import allowed_users
    if user_id not in allowed_users():
        return ConversationHandler.END
    try:
        target = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("Invalid temperature.")
        return TEMP_CUSTOM_BED
    await api.gcode(f"M140 S{target}", user_id=user_id)
    L = lang()
    await update.message.reply_text(t("temps.set_bed", L).format(val=target))
    return ConversationHandler.END
