"""Bed mesh visualization handler."""
from __future__ import annotations

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import lang
from lang import t
from helpers import auth_cb, btn, uid, offline_guard
import api


@auth_cb
async def cb_bed_mesh(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = uid(update)
    L = lang()

    if await offline_guard(q, user_id):
        return

    mesh = await api.bed_mesh_status(user_id=user_id)

    if not mesh:
        await q.edit_message_text(
            t("bed_mesh.no_data", L),
            reply_markup=InlineKeyboardMarkup([[btn(t("btn.back_menu", L), "menu:main")]]),
        )
        return

    profile_name = mesh.get("profile_name", "?")
    mesh_matrix = mesh.get("probed_matrix") or mesh.get("mesh_matrix", [])

    if not mesh_matrix:
        await q.edit_message_text(
            t("bed_mesh.no_matrix", L),
            reply_markup=InlineKeyboardMarkup([[btn(t("btn.back_menu", L), "menu:main")]]),
        )
        return

    # Build ASCII heat map
    # Find min/max for normalization
    all_vals = [v for row in mesh_matrix for v in row]
    min_v = min(all_vals)
    max_v = max(all_vals)
    rng = max_v - min_v if max_v != min_v else 1.0

    SYMBOLS = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

    lines = []
    for row in reversed(mesh_matrix):  # top = back of bed
        line = ""
        for v in row:
            idx = int((v - min_v) / rng * (len(SYMBOLS) - 1))
            line += SYMBOLS[idx]
        lines.append(line)

    grid_str = "\n".join(lines)
    text = (
        f"{t('bed_mesh.title', L)}\n"
        f"Profile: `{profile_name}`\n"
        f"Min: `{min_v:+.3f}` Max: `{max_v:+.3f}` Range: `{rng:.3f}`\n\n"
        f"```\n{grid_str}\n```"
    )

    keyboard = [
        [btn(t("btn.refresh", L), "menu:bed_mesh"), btn(t("btn.back_menu", L), "menu:main")]
    ]

    await q.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN,
    )
