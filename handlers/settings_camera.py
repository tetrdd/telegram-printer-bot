"""Camera settings and menu visibility — hide/show the Camera button in the main menu."""
from __future__ import annotations

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import get as cfg, save as save_cfg, lang
from lang import t
from helpers import auth_cb, btn


@auth_cb
async def cb_settings_camera(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    L = lang()
    c = cfg()
    camera_cfg = c.get("camera", {})
    show_menu = camera_cfg.get("show_in_menu", True)

    kb = [
        [btn(f"{'✅' if show_menu else '❌'} {t('settings.camera.show_menu', L)}", "camera_toggle_menu")],
        [btn(t("btn.back_menu", L), "menu:settings")],
    ]
    await q.edit_message_text(
        t("settings.camera.title", L),
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN,
    )


@auth_cb
async def cb_camera_toggle_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    c = cfg()
    camera_cfg = c.setdefault("camera", {})
    current = camera_cfg.get("show_in_menu", True)
    camera_cfg["show_in_menu"] = not current
    save_cfg()
    await q.answer("Done")
    await cb_settings_camera(update, ctx)
