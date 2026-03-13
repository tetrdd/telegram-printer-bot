"""Temperature control — view, presets, custom input."""

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from config import get as cfg, lang
from lang import t
from helpers import auth, auth_cb, btn, uid, grid, printer_badge
import api

# Conversation states
TEMP_CUSTOM_HOTEND = 100
TEMP_CUSTOM_BED = 101


@auth_cb
async def cb_temps(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    L = lang()
    user_id = uid(update)

    data = await api.get("/printer/objects/query?extruder&heater_bed", user_id=user_id)
    if not data:
        await q.edit_message_text(
            t("err.no_connect", L),
            reply_markup=InlineKeyboardMarkup([[btn(t("btn.back_menu", L), "menu:main")]]),
        )
        return

    res = data.get("result", {}).get("status", {})
    ext = res.get("extruder", {})
    bed = res.get("heater_bed", {})

    text = (
        f"{printer_badge(user_id)}"
        f"{t('temps.title', L)}\n\n"
        f"{t('status.hotend', L)}: *{ext.get('temperature', 0):.1f}°C* → {ext.get('target', 0):.0f}°C\n"
        f"  {t('temps.power', L)}: {ext.get('power', 0) * 100:.0f}%\n\n"
        f"{t('status.bed', L)}: *{bed.get('temperature', 0):.1f}°C* → {bed.get('target', 0):.0f}°C\n"
        f"  {t('temps.power', L)}: {bed.get('power', 0) * 100:.0f}%"
    )

    kb = InlineKeyboardMarkup([
        [btn(t("temps.set_hotend", L), "temp:hotend"), btn(t("temps.set_bed", L), "temp:bed")],
        [btn(t("temps.cool_all", L), "temp:cool_all")],
        [btn(t("btn.refresh", L), "menu:temps"), btn(t("btn.back_menu", L), "menu:main")],
    ])
    await q.edit_message_text(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)


@auth_cb
async def cb_temp_presets(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show preset buttons for hotend or bed."""
    q = update.callback_query
    heater = q.data.split(":")[1]  # "hotend" or "bed"
    await q.answer()
    L = lang()

    presets = cfg().get("temp_presets", {}).get(heater, {})
    buttons = [btn(f"{name} ({temp}°C)", f"set_temp:{heater}:{temp}") for name, temp in presets.items()]
    buttons.append(btn(t("temps.custom", L), f"temp_custom:{heater}"))

    kb = grid(buttons, cols=2)
    kb.append([btn(t("temps.back", L), "menu:temps")])

    title_key = "temps.hotend_title" if heater == "hotend" else "temps.bed_title"
    await q.edit_message_text(
        t(title_key, L),
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_set_temp(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    _, heater, temp_str = q.data.split(":")
    temp = int(temp_str)
    user_id = uid(update)

    if heater == "hotend":
        r = await api.gcode(f"SET_HEATER_TEMPERATURE HEATER=extruder TARGET={temp}", user_id=user_id)
    else:
        r = await api.gcode(f"SET_HEATER_TEMPERATURE HEATER=heater_bed TARGET={temp}", user_id=user_id)

    label = t("status.hotend", lang()) if heater == "hotend" else t("status.bed", lang())
    await q.answer(f"{label} → {temp}°C {'✓' if r else '✗'}", show_alert=True)
    await cb_temps(update, ctx)


@auth_cb
async def cb_cool_all(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    user_id = uid(update)
    await api.gcode("SET_HEATER_TEMPERATURE HEATER=extruder TARGET=0", user_id=user_id)
    await api.gcode("SET_HEATER_TEMPERATURE HEATER=heater_bed TARGET=0", user_id=user_id)
    await q.answer(t("temps.cooled", lang()), show_alert=True)
    await cb_temps(update, ctx)


# ── Custom temperature input (conversation handlers) ────────────────────────

@auth_cb
async def cb_temp_custom_hotend(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(t("temps.custom_hotend_prompt", lang()), parse_mode=ParseMode.MARKDOWN)
    return TEMP_CUSTOM_HOTEND


@auth_cb
async def cb_temp_custom_bed(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(t("temps.custom_bed_prompt", lang()), parse_mode=ParseMode.MARKDOWN)
    return TEMP_CUSTOM_BED


@auth
async def handle_custom_hotend(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    L = lang()
    user_id = uid(update)
    try:
        temp = int(update.message.text.strip())
        if not 0 <= temp <= 300:
            raise ValueError
    except ValueError:
        await update.message.reply_text(t("temps.invalid_hotend", L))
        return TEMP_CUSTOM_HOTEND

    r = await api.gcode(f"SET_HEATER_TEMPERATURE HEATER=extruder TARGET={temp}", user_id=user_id)
    msg = f"🔥 {t('status.hotend', L)} → {temp}°C {'✓' if r else '✗'}"
    await update.message.reply_text(
        msg,
        reply_markup=InlineKeyboardMarkup([[btn(t("temps.back", L), "menu:temps"), btn(t("btn.back_menu", L), "menu:main")]]),
    )
    return ConversationHandler.END


@auth
async def handle_custom_bed(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    L = lang()
    user_id = uid(update)
    try:
        temp = int(update.message.text.strip())
        if not 0 <= temp <= 120:
            raise ValueError
    except ValueError:
        await update.message.reply_text(t("temps.invalid_bed", L))
        return TEMP_CUSTOM_BED

    r = await api.gcode(f"SET_HEATER_TEMPERATURE HEATER=heater_bed TARGET={temp}", user_id=user_id)
    msg = f"🛏️ {t('status.bed', L)} → {temp}°C {'✓' if r else '✗'}"
    await update.message.reply_text(
        msg,
        reply_markup=InlineKeyboardMarkup([[btn(t("temps.back", L), "menu:temps"), btn(t("btn.back_menu", L), "menu:main")]]),
    )
    return ConversationHandler.END
