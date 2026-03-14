"""Settings menu — toggle notifications, change poll rate, language select."""
from __future__ import annotations

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import lang, get as get_cfg, save as save_cfg, set_lang
from lang import t, LANGUAGES
from helpers import auth_cb, btn, uid


@auth_cb
async def cb_settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    L = lang()
    cfg = get_cfg()
    notif = cfg.get("notifications", {}).get("enabled", True)
    poll = cfg.get("monitor", {}).get("poll_interval", 10)

    text = (
        f"{t('settings.title', L)}\n\n"
        f"{t('settings.notifications', L)}: {'✅' if notif else '❌'}\n"
        f"{t('settings.poll', L)}: {poll}s\n"
        f"{t('settings.language', L)}: {L}"
    )

    keyboard = [
        [btn(t("settings.toggle_notif", L), "set:notif")],
        [
            btn("5s", "set:poll:5"),
            btn("10s", "set:poll:10"),
            btn("30s", "set:poll:30"),
            btn("60s", "set:poll:60"),
        ],
    ]
    # Language buttons
    lang_row = [btn(lname, f"set:lang:{lcode}") for lcode, lname in LANGUAGES.items()]
    keyboard.append(lang_row)
    keyboard.append([btn(t("btn.back_menu", L), "menu:main")])

    await q.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


@auth_cb
async def cb_setting_toggle(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    parts = q.data.split(":")
    setting = parts[1]
    cfg = get_cfg()

    if setting == "notif":
        notif = cfg.setdefault("notifications", {})
        notif["enabled"] = not notif.get("enabled", True)
        save_cfg()

    elif setting == "poll" and len(parts) > 2:
        val = int(parts[2])
        cfg.setdefault("monitor", {})["poll_interval"] = val
        save_cfg()

    elif setting == "lang" and len(parts) > 2:
        set_lang(parts[2])

    # Refresh settings menu
    await cb_settings(update, ctx)
