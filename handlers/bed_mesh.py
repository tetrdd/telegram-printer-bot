"""Bed mesh visualization handler."""

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import lang
from lang import t
from helpers import auth_cb, btn, uid, offline_guard
import api


def _visualize_mesh(matrix: list) -> str:
    """Render a 2D mesh matrix as a compact text heatmap."""
    if not matrix:
        return ""

    lines = []
    for row in matrix:
        row_str = "  ".join(f"{v:+.3f}" for v in row)
        lines.append(row_str)
    return "\n".join(lines)


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
            f"{t('mesh.title', L)}\n\n{t('mesh.no_data', L)}",
            reply_markup=InlineKeyboardMarkup([
                [btn(t("btn.refresh", L), "menu:bed_mesh"), btn(t("btn.back_menu", L), "menu:main")],
            ]),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    profile_name = mesh.get("profile_name", "default")
    probed_matrix = mesh.get("probed_matrix", [])

    # Calculate range
    all_values = []
    for row in probed_matrix:
        all_values.extend(row)

    mesh_info_lines = [
        t("mesh.title", L),
        "",
        t("mesh.name", L).format(name=profile_name),
    ]

    if all_values:
        min_val = min(all_values)
        max_val = max(all_values)
        mesh_info_lines.append(
            t("mesh.range", L).format(min=f"{min_val:.3f}", max=f"{max_val:.3f}")
        )

    if probed_matrix:
        rows = len(probed_matrix)
        cols = len(probed_matrix[0]) if probed_matrix else 0
        mesh_info_lines.append(f"Grid: {rows}×{cols}")
        mesh_info_lines.append("")
        mesh_info_lines.append("```")
        mesh_info_lines.append(_visualize_mesh(probed_matrix))
        mesh_info_lines.append("```")
    else:
        mesh_info_lines.append("")
        mesh_info_lines.append(t("mesh.no_data", L))

    text = "\n".join(mesh_info_lines)

    # Telegram message limit — truncate if needed
    if len(text) > 4000:
        text = text[:3990] + "\n[...]"

    await q.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [btn(t("btn.refresh", L), "menu:bed_mesh"), btn(t("btn.back_menu", L), "menu:main")],
        ]),
        parse_mode=ParseMode.MARKDOWN,
    )
