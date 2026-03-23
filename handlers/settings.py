"""Settings menu — categorized settings for better UX."""
from __future__ import annotations

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import get as cfg, save as save_cfg, lang, set_lang
from lang import t
from helpers import auth_cb, btn


def _settings_main_keyboard() -> InlineKeyboardMarkup:
    L = lang()
    return InlineKeyboardMarkup([
        [btn(t("settings.cat_general", L), "set_cat:general")],
        [btn(t("settings.cat_notif", L), "set_cat:notif")],
        [btn(t("settings.cat_macros", L), "set_cat:macros")],
        [btn(t("settings.cat_temps", L), "set_cat:temps")],
        [btn(t("settings.cat_gcode", L), "set_cat:gcode")],
        [btn(t("settings.cat_camera", L), "set_cat:camera")],
        [btn(t("settings.cat_language", L), "set_cat:language")],
        [btn(t("btn.back_menu", L), "menu:main")],
    ])


@auth_cb
async def cb_settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        t("settings.title", lang()),
        reply_markup=_settings_main_keyboard(),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_settings_category(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    cat = q.data[len("set_cat:"):]
    await q.answer()
    L = lang()
    c = cfg()

    def tog(val: bool) -> str:
        return "✅" if val else "❌"

    kb = []
    title = t(f"settings.cat_{cat}", L)

    if cat == "general":
        monitoring = c.get("monitoring", {})
        safety = c.get("safety", {})
        files_cfg = c.get("files", {})
        kb = [
            [btn(f"⏱️ {t('settings.poll', L)}: {monitoring.get('poll_interval', 10)}s", "set:cycle_poll")],
            [btn(f"📄 {t('settings.files_per_page', L)}: {files_cfg.get('files_per_page', 5)}", "set:cycle_fpp")],
            [btn(f"{tog(safety.get('emergency_stop_enabled', True))} {t('settings.estop_menu', L)}", "set:safety.emergency_stop_enabled")],
            [btn(f"{tog(safety.get('emergency_stop_confirm', True))} {t('settings.estop_confirm', L)}", "set:safety.emergency_stop_confirm")],
        ]
    elif cat == "notif":
        notif = c.get("notifications", {})
        kb = [
            [btn(f"{tog(notif.get('on_print_complete', True))} {t('settings.print_complete', L)}", "set:notifications.on_print_complete")],
            [btn(f"{tog(notif.get('on_print_error', True))} {t('settings.print_error', L)}", "set:notifications.on_print_error")],
            [btn(f"{tog(notif.get('on_print_start', True))} {t('settings.print_start', L)}", "set:notifications.on_print_start")],
            [btn(f"{tog(notif.get('on_print_cancelled', True))} {t('settings.print_cancelled', L)}", "set:notifications.on_print_cancelled")],
            [btn(f"{tog(notif.get('on_filament_runout', True))} {t('settings.filament_runout', L)}", "set:notifications.on_filament_runout")],
            [btn(f"{tog(notif.get('on_progress_milestone', True))} {t('settings.progress_milestone', L)}", "set:notifications.on_progress_milestone")],
            [btn(f"🌡️ {t('settings.temp_alert', L)}: {notif.get('temp_alert_threshold', 0)}°C", "set:cycle_temp_alert")],
        ]
    elif cat == "language":
        options = ["en", "de", "ru", "pl", "fr", "es", "it"]
        labels = {
            "en": "English", "de": "Deutsch", "ru": "Русский", "pl": "Polski",
            "fr": "Français", "es": "Español", "it": "Italiano"
        }
        current = lang()
        for opt in options:
            label = f"{'🔹 ' if opt == current else ''}{labels[opt]}"
            kb.append([btn(label, f"set_lang:{opt}")])
    elif cat == "macros":
        # Handled by settings_macros.py but we can provide a stub or direct call
        from handlers.settings_macros import cb_settings_macros
        await cb_settings_macros(update, ctx)
        return
    elif cat == "temps":
        from handlers.settings_temps import cb_settings_temps
        await cb_settings_temps(update, ctx)
        return
    elif cat == "gcode":
        from handlers.settings_gcode import cb_settings_gcode
        await cb_settings_gcode(update, ctx)
        return
    elif cat == "camera":
        from handlers.settings_camera import cb_settings_camera
        await cb_settings_camera(update, ctx)
        return

    kb.append([btn(t("btn.back_menu", L), "menu:settings")])
    await q.edit_message_text(
        f"*{title}*",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_set_lang(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    new_lang = q.data[len("set_lang:"):]
    set_lang(new_lang)
    await q.answer(f"🌐 {new_lang}")
    # Stay in language menu
    update.callback_query.data = "set_cat:language"
    await cb_settings_category(update, ctx)


@auth_cb
async def cb_setting_toggle(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    key_path = q.data[len("set:"):]

    # Get current category to return to it
    # This is a bit tricky as we don't store it, but we can infer it
    category = "general"
    if key_path.startswith("notifications.") or key_path == "cycle_temp_alert":
        category = "notif"

    # ── Cycle-type settings ──────────────────────────────────────────────
    if key_path == "cycle_poll":
        options = [5, 10, 15, 30, 60]
        current = cfg().get("monitoring", {}).get("poll_interval", 10)
        try:
            idx = options.index(current)
            new = options[(idx + 1) % len(options)]
        except ValueError:
            new = 10
        cfg().setdefault("monitoring", {})["poll_interval"] = new
        save_cfg()
        await q.answer(f"⏱️ {new}s")
    elif key_path == "cycle_fpp":
        options = [3, 5, 8, 10, 15]
        current = cfg().get("files", {}).get("files_per_page", 5)
        try:
            idx = options.index(current)
            new = options[(idx + 1) % len(options)]
        except ValueError:
            new = 5
        cfg().setdefault("files", {})["files_per_page"] = new
        save_cfg()
        await q.answer(f"📄 {new}")
    elif key_path == "cycle_temp_alert":
        options = [0, 200, 220, 240, 260, 280, 300]
        current = cfg().get("notifications", {}).get("temp_alert_threshold", 0)
        try:
            idx = options.index(current)
            new = options[(idx + 1) % len(options)]
        except ValueError:
            new = 0
        cfg().setdefault("notifications", {})["temp_alert_threshold"] = new
        save_cfg()
        label = f"{new}°C" if new > 0 else "Off"
        await q.answer(f"🌡️ {label}")
    else:
        # ── Boolean toggle (dotted path) ─────────────────────────────────────
        parts = key_path.split(".")
        if len(parts) == 2:
            section, key = parts
            current = cfg().get(section, {}).get(key, True)
            cfg().setdefault(section, {})[key] = not current
            save_cfg()
            state = "ON" if not current else "OFF"
            await q.answer(f"{state}")

    # Return to the category
    update.callback_query.data = f"set_cat:{category}"
    await cb_settings_category(update, ctx)
