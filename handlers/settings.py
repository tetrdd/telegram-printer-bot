"""Settings menu — toggle notifications, change poll rate, language, etc."""

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import get as cfg, save as save_cfg, lang, set_lang
from lang import t
from helpers import auth_cb, btn


def _settings_keyboard() -> InlineKeyboardMarkup:
    c = cfg()
    L = lang()
    notif = c.get("notifications", {})
    safety = c.get("safety", {})
    monitoring = c.get("monitoring", {})
    files_cfg = c.get("files", {})

    def tog(val: bool) -> str:
        return "✅" if val else "❌"

    return InlineKeyboardMarkup([
        [btn(
            f"{tog(notif.get('on_print_complete', True))} {t('settings.print_complete', L)}",
            "set:notifications.on_print_complete",
        )],
        [btn(
            f"{tog(notif.get('on_print_error', True))} {t('settings.print_error', L)}",
            "set:notifications.on_print_error",
        )],
        [btn(
            f"{tog(notif.get('on_print_start', True))} {t('settings.print_start', L)}",
            "set:notifications.on_print_start",
        )],
        [btn(
            f"{tog(notif.get('on_print_cancelled', True))} {t('settings.print_cancelled', L)}",
            "set:notifications.on_print_cancelled",
        )],
        [btn(
            f"{tog(notif.get('on_filament_runout', True))} {t('settings.filament_runout', L)}",
            "set:notifications.on_filament_runout",
        )],
        [btn(
            f"{tog(notif.get('on_progress_milestone', True))} {t('settings.progress_milestone', L)}",
            "set:notifications.on_progress_milestone",
        )],
        [btn(
            f"🌡️ {t('settings.temp_alert', L)}: {notif.get('temp_alert_threshold', 0)}°C",
            "set:cycle_temp_alert",
        )],
        [btn(
            f"{tog(safety.get('emergency_stop_enabled', True))} {t('settings.estop_menu', L)}",
            "set:safety.emergency_stop_enabled",
        )],
        [btn(
            f"{tog(safety.get('emergency_stop_confirm', True))} {t('settings.estop_confirm', L)}",
            "set:safety.emergency_stop_confirm",
        )],
        [btn(
            f"⏱️ {t('settings.poll', L)}: {monitoring.get('poll_interval', 10)}s",
            "set:cycle_poll",
        )],
        [btn(
            f"📄 {t('settings.files_per_page', L)}: {files_cfg.get('files_per_page', 5)}",
            "set:cycle_fpp",
        )],
        [btn(t("settings.language", L), "set:cycle_lang")],
        [btn(t("btn.back_menu", L), "menu:main")],
    ])


@auth_cb
async def cb_settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    await q.edit_message_text(
        t("settings.title", lang()),
        reply_markup=_settings_keyboard(),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_setting_toggle(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    key_path = q.data[len("set:"):]

    # ── Cycle-type settings ─────────────────────────────────────────────────────────
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
        await cb_settings(update, ctx)
        return

    if key_path == "cycle_fpp":
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
        await cb_settings(update, ctx)
        return

    if key_path == "cycle_temp_alert":
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
        await cb_settings(update, ctx)
        return

    if key_path == "cycle_lang":
        options = ["en", "de", "ru", "pl"]
        current = lang()
        try:
            idx = options.index(current)
            new = options[(idx + 1) % len(options)]
        except ValueError:
            new = "en"
        set_lang(new)
        labels = {"en": "English", "de": "Deutsch", "ru": "Русский", "pl": "Polski"}
        await q.answer(f"🌐 {labels[new]}")
        await cb_settings(update, ctx)
        return

    # ── Boolean toggle (dotted path) ───────────────────────────────────────────────────
    parts = key_path.split(".")
    if len(parts) == 2:
        section, key = parts
        current = cfg().get(section, {}).get(key, True)
        cfg().setdefault(section, {})[key] = not current
        save_cfg()
        state = "ON" if not current else "OFF"
        await q.answer(f"{state}")
        await cb_settings(update, ctx)
