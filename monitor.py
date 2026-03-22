"""
Background print monitor.
Polls Moonraker for each configured printer and sends notifications on:
  - State changes (complete, error, start, cancel)
  - Progress milestones (25%, 50%, 75%)
  - Temperature alerts
  - Filament runout

Also tracks per-printer online/offline state and caches last known status
for the UI to display when a printer is unreachable.
"""
from __future__ import annotations

import asyncio
import logging
import time
import aiohttp
from telegram import InlineKeyboardMarkup
from telegram.ext import Application
from telegram.constants import ParseMode
from config import get as cfg, printers, allowed_users, lang, is_multi_printer, active_printer_for
from lang import t
from helpers import btn, fmt_duration, fmt_clock_eta

logger = logging.getLogger("PrinterBot.monitor")

_MILESTONES = [25, 50, 75]


class _PrinterState:
    """Tracks per-printer monitoring state."""

    def __init__(self, printer_cfg: dict):
        self.printer = printer_cfg
        self.printer_id: int = printer_cfg.get("id", 0)
        self.name = printer_cfg.get("name", "Printer")
        self.last_state: str | None = None
        self.last_filename: str = ""
        self.last_filament_detected: bool | None = None
        self.online: bool | None = None  # None = unknown (first poll)
        self.consecutive_failures: int = 0
        # Cached status for offline display
        self.cached_status: dict | None = None
        self.cached_at: float = 0  # time.time() when last cached
        # Progress milestone tracking (reset on new print)
        self.last_milestone: int = 0  # last reported milestone (0/25/50/75)


# ── Module-level state for handlers to query ─────────────────────────────────
_monitor: "PrintMonitor | None" = None


def is_printer_online(user_id: int) -> bool:
    """Check if the user's active printer is online. Returns True if unknown."""
    if _monitor is None:
        return True
    printer = active_printer_for(user_id)
    for ps in _monitor._printer_states:
        if ps.printer_id == printer["id"]:
            if ps.online is None:
                return True
            return ps.online
    return True


def cached_printer_status(user_id: int) -> tuple[dict | None, float]:
    """
    Get cached status for the user's active printer.
    Returns (status_dict, cached_timestamp). (None, 0) if no cache.
    """
    if _monitor is None:
        return None, 0
    printer = active_printer_for(user_id)
    for ps in _monitor._printer_states:
        if ps.printer_id == printer["id"]:
            return ps.cached_status, ps.cached_at
    return None, 0


def is_printer_online_by_id(printer_id: int) -> bool | None:
    """Check online status by printer ID. Returns None if unknown."""
    if _monitor is None:
        return None
    for ps in _monitor._printer_states:
        if ps.printer_id == printer_id:
            return ps.online
    return None


class PrintMonitor:
    def __init__(self, app: Application):
        global _monitor
        self.app = app
        self._running = False
        self._printer_states: list[_PrinterState] = []
        _monitor = self

    async def start(self):
        self._running = True
        self._printer_states = [_PrinterState(p) for p in printers()]
        logger.info(f"Monitor started — tracking {len(self._printer_states)} printer(s)")

        while self._running:
            try:
                for ps in self._printer_states:
                    await self._poll_printer(ps)
            except Exception as e:
                logger.error(f"Monitor error: {e}")
            interval = cfg().get("monitoring", {}).get("poll_interval", 10)
            await asyncio.sleep(interval)

    def stop(self):
        self._running = False

    async def _poll_printer(self, ps: _PrinterState):
        """Poll a single printer for status, temp alerts, filament, progress, and connectivity."""
        mr = ps.printer.get("moonraker", {})
        url = mr.get("url", "").rstrip("/")
        key = mr.get("api_key", "")
        if not url:
            return

        headers = {"Content-Type": "application/json"}
        if key:
            headers["X-Api-Key"] = key

        # ── Connectivity check + status query ────────────────────────────
        res = await self._fetch_status(url, headers)

        if res is None:
            ps.consecutive_failures += 1
            if ps.online is not False and ps.consecutive_failures >= 3:
                ps.online = False
                logger.warning(f"Printer '{ps.name}' went offline")
            return

        # ── Printer is online ────────────────────────────────────────────
        was_offline = ps.online is False
        ps.online = True
        ps.consecutive_failures = 0

        # Cache status for offline display
        ps.cached_status = res
        ps.cached_at = time.time()

        if was_offline:
            logger.info(f"Printer '{ps.name}' is back online")

        stats = res.get("print_stats", {})
        state = stats.get("state", "unknown")
        filename = stats.get("filename", "")

        # ── State change notifications ───────────────────────────────────
        if ps.last_state is not None and state != ps.last_state:
            await self._on_state_change(ps, ps.last_state, state, filename, res)
            # Reset milestone tracker when a new print starts
            if state == "printing" and ps.last_state in ("ready", "standby"):
                ps.last_milestone = 0

        ps.last_state = state
        ps.last_filename = filename

        # ── Progress milestones ──────────────────────────────────────────
        if state == "printing" and cfg().get("notifications", {}).get("on_progress_milestone", True):
            display = res.get("display_status", {})
            vsd = res.get("virtual_sdcard", {})
            pct = display.get("progress", vsd.get("progress", 0)) * 100
            await self._check_milestone(ps, pct, filename, res)

        # ── Temperature alert ────────────────────────────────────────────
        threshold = cfg().get("notifications", {}).get("temp_alert_threshold", 0)
        if threshold > 0:
            ext = res.get("extruder", {})
            temp = ext.get("temperature", 0)
            if temp >= threshold:
                L = lang()
                prefix = f"🖨️ *{ps.name}*\n" if is_multi_printer() else ""
                await self._notify(
                    f"{prefix}{t('notif.temp_alert', L).format(temp=f'{temp:.1f}', threshold=threshold)}"
                )

        # ── Filament runout detection ────────────────────────────────────
        if cfg().get("notifications", {}).get("on_filament_runout", True):
            await self._check_filament_sensor(ps, url, headers)

    async def _check_milestone(self, ps: _PrinterState, pct: float, filename: str, res: dict):
        """Send a notification when print crosses 25/50/75% milestones."""
        for ms in _MILESTONES:
            if pct >= ms and ps.last_milestone < ms:
                ps.last_milestone = ms
                L = lang()
                prefix = f"🖨️ *{ps.name}*\n" if is_multi_printer() else ""
                # Calculate ETA
                dur = res.get("print_stats", {}).get("print_duration", 0)
                eta_str = ""
                if pct > 1:
                    remaining = (dur / (pct / 100)) - dur
                    eta_str = f"\nETA: {fmt_clock_eta(remaining)} ({fmt_duration(remaining)})"
                await self._notify(
                    f"{prefix}{t('notif.milestone', L).format(pct=ms, filename=filename)}{eta_str}"
                )
                break  # Only one milestone per poll cycle

    async def _fetch_status(self, url: str, headers: dict) -> dict | None:
        """GET printer status with timeout. Returns None if offline."""
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(
                    f"{url}/printer/objects/query?print_stats&display_status&virtual_sdcard&extruder&heater_bed&gcode_move",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=8),
                ) as r:
                    if r.status == 200:
                        data = await r.json()
                        return data.get("result", {}).get("status")
        except Exception:
            pass
        return None

    async def _check_filament_sensor(self, ps: _PrinterState, url: str, headers: dict):
        """Check filament sensor for a specific printer."""
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(
                    f"{url}/printer/objects/list",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as r:
                    if r.status != 200:
                        return
                    data = await r.json()

            objects = data.get("result", {}).get("objects", [])
            sensor_names = [
                obj for obj in objects
                if obj.startswith("filament_switch_sensor") or obj.startswith("filament_motion_sensor")
            ]

            if not sensor_names:
                return

            query = "&".join(sensor_names)
            async with aiohttp.ClientSession() as s:
                async with s.get(
                    f"{url}/printer/objects/query?{query}",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as r:
                    if r.status != 200:
                        return
                    data = await r.json()

            status = data.get("result", {}).get("status", {})

            for sensor_name in sensor_names:
                sensor = status.get(sensor_name, {})
                filament_detected = sensor.get("filament_detected")
                if filament_detected is None:
                    continue

                if ps.last_filament_detected is True and filament_detected is False:
                    L = lang()
                    prefix = f"🖨️ *{ps.name}*\n" if is_multi_printer() else ""
                    await self._notify(f"{prefix}{t('notif.filament_runout', L)}")
                    logger.warning(f"Filament runout on '{ps.name}' via {sensor_name}")

                ps.last_filament_detected = filament_detected

        except Exception as e:
            logger.debug(f"Filament check error for '{ps.name}': {e}")

    async def _on_state_change(self, ps: _PrinterState, old: str, new: str, filename: str, res: dict):
        notif = cfg().get("notifications", {})
        L = lang()
        msg = None
        prefix = f"🖨️ *{ps.name}*\n" if is_multi_printer() else ""

        if new == "complete" and notif.get("on_print_complete", True):
            dur = res.get("print_stats", {}).get("print_duration", 0)
            fil = res.get("print_stats", {}).get("filament_used", 0) / 1000
            msg = f"{prefix}{t('notif.complete', L).format(filename=filename, duration=fmt_duration(dur), filament=f'{fil:.2f}')}"

        elif new == "error" and notif.get("on_print_error", True):
            err = res.get("print_stats", {}).get("message", "Unknown")
            msg = f"{prefix}{t('notif.error', L).format(filename=filename, error=err)}"

        elif new == "printing" and old in ("ready", "standby") and notif.get("on_print_start", True):
            msg = f"{prefix}{t('notif.started', L).format(filename=filename)}"

        elif new == "cancelled" and notif.get("on_print_cancelled", True):
            msg = f"{prefix}{t('notif.cancelled', L).format(filename=filename)}"

        if msg:
            await self._notify(msg)

    async def _notify(self, text: str):
        L = lang()
        for uid in allowed_users():
            try:
                await self.app.bot.send_message(
                    chat_id=uid,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup([
                        [btn(t("menu.status", L), "menu:status"), btn(t("btn.snapshot", L), "action:snapshot")],
                    ]),
                )
            except Exception as e:
                logger.error(f"Notify {uid}: {e}")
