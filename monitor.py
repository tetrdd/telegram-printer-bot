"""
Background print monitor.
Polls Moonraker for each configured printer and sends notifications on:
  - State changes (complete, error, start, cancel)
  - Temperature alerts
  - Filament runout
  - Printer going offline / coming back online
"""

import asyncio
import logging
import aiohttp
from telegram import InlineKeyboardMarkup
from telegram.ext import Application
from telegram.constants import ParseMode
from config import get as cfg, printers, allowed_users, lang, is_multi_printer
from lang import t
from helpers import btn, fmt_duration

logger = logging.getLogger("PrinterBot.monitor")


class _PrinterState:
    """Tracks per-printer monitoring state."""

    def __init__(self, printer_cfg: dict):
        self.printer = printer_cfg
        self.name = printer_cfg.get("name", "Printer")
        self.last_state: str | None = None
        self.last_filename: str = ""
        self.last_filament_detected: bool | None = None
        self.online: bool | None = None  # None = unknown (first poll)
        self.consecutive_failures: int = 0


class PrintMonitor:
    def __init__(self, app: Application):
        self.app = app
        self._running = False
        self._printer_states: list[_PrinterState] = []

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
        """Poll a single printer for status, temp alerts, filament, and connectivity."""
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
            # Only trigger offline after 3 consecutive failures (avoid flapping)
            if ps.online is not False and ps.consecutive_failures >= 3:
                ps.online = False
                if cfg().get("notifications", {}).get("on_printer_offline", True):
                    name = f" — {ps.name}" if is_multi_printer() else ""
                    await self._notify(
                        t("notif.offline", lang()).format(name=name)
                    )
                    logger.warning(f"Printer '{ps.name}' went offline")
            return

        # ── Printer is online ────────────────────────────────────────────
        was_offline = ps.online is False
        ps.online = True
        ps.consecutive_failures = 0

        if was_offline:
            if cfg().get("notifications", {}).get("on_printer_offline", True):
                name = f" — {ps.name}" if is_multi_printer() else ""
                await self._notify(
                    t("notif.online", lang()).format(name=name)
                )
                logger.info(f"Printer '{ps.name}' is back online")

        stats = res.get("print_stats", {})
        state = stats.get("state", "unknown")
        filename = stats.get("filename", "")

        # ── State change notifications ───────────────────────────────────
        if ps.last_state is not None and state != ps.last_state:
            await self._on_state_change(ps, ps.last_state, state, filename, res)
        ps.last_state = state
        ps.last_filename = filename

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

    async def _fetch_status(self, url: str, headers: dict) -> dict | None:
        """GET printer status with timeout. Returns None if offline."""
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(
                    f"{url}/printer/objects/query?print_stats&display_status&virtual_sdcard&extruder&heater_bed",
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
