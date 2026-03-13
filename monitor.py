"""
Background print monitor.
Polls Moonraker and sends notifications on state changes,
temperature alerts, and filament runout events.
"""

import asyncio
import logging
from telegram import InlineKeyboardMarkup
from telegram.ext import Application
from telegram.constants import ParseMode
from config import get as cfg, allowed_users, lang
from lang import t
from helpers import btn, fmt_duration

logger = logging.getLogger("PrinterBot.monitor")


class PrintMonitor:
    def __init__(self, app: Application):
        self.app = app
        self.last_state: str | None = None
        self.last_filename: str = ""
        self.last_filament_detected: bool | None = None  # For runout sensor
        self._running = False

    async def start(self):
        self._running = True
        logger.info("Monitor started")
        while self._running:
            try:
                await self._poll()
            except Exception as e:
                logger.error(f"Monitor error: {e}")
            interval = cfg().get("monitoring", {}).get("poll_interval", 10)
            await asyncio.sleep(interval)

    def stop(self):
        self._running = False

    async def _poll(self):
        import api

        # Main status query
        res = await api.printer_status()
        if not res:
            return

        stats = res.get("print_stats", {})
        state = stats.get("state", "unknown")
        filename = stats.get("filename", "")

        # ── State change notifications ───────────────────────────────────
        if self.last_state is not None and state != self.last_state:
            await self._on_state_change(self.last_state, state, filename, res)
        self.last_state = state
        self.last_filename = filename

        # ── Temperature alert ────────────────────────────────────────────
        threshold = cfg().get("notifications", {}).get("temp_alert_threshold", 0)
        if threshold > 0:
            ext = res.get("extruder", {})
            temp = ext.get("temperature", 0)
            if temp >= threshold:
                L = lang()
                await self._notify(
                    t("notif.temp_alert", L).format(temp=f"{temp:.1f}", threshold=threshold)
                )

        # ── Filament runout detection ────────────────────────────────────
        if cfg().get("notifications", {}).get("on_filament_runout", True):
            await self._check_filament_sensor()

    async def _check_filament_sensor(self):
        """
        Check filament sensor state via Moonraker.
        Klipper exposes filament sensors as 'filament_switch_sensor <name>'
        or 'filament_motion_sensor <name>' objects.
        """
        import api

        # Query known filament sensor object names
        objects = await api.printer_objects()
        sensor_names = [
            obj for obj in objects
            if obj.startswith("filament_switch_sensor") or obj.startswith("filament_motion_sensor")
        ]

        if not sensor_names:
            return  # No filament sensor configured in Klipper

        # Query sensor state
        query = "&".join(sensor_names)
        data = await api.get(f"/printer/objects/query?{query}")
        if not data:
            return

        status = data.get("result", {}).get("status", {})

        for sensor_name in sensor_names:
            sensor = status.get(sensor_name, {})
            filament_detected = sensor.get("filament_detected")

            if filament_detected is None:
                continue

            # Detect transition: filament was present → now gone
            if self.last_filament_detected is True and filament_detected is False:
                L = lang()
                await self._notify(t("notif.filament_runout", L))
                logger.warning(f"Filament runout detected via {sensor_name}")

            self.last_filament_detected = filament_detected

    async def _on_state_change(self, old: str, new: str, filename: str, res: dict):
        notif = cfg().get("notifications", {})
        L = lang()
        msg = None

        if new == "complete" and notif.get("on_print_complete", True):
            dur = res.get("print_stats", {}).get("print_duration", 0)
            fil = res.get("print_stats", {}).get("filament_used", 0) / 1000
            msg = t("notif.complete", L).format(
                filename=filename,
                duration=fmt_duration(dur),
                filament=f"{fil:.2f}",
            )

        elif new == "error" and notif.get("on_print_error", True):
            err = res.get("print_stats", {}).get("message", "Unknown")
            msg = t("notif.error", L).format(filename=filename, error=err)

        elif new == "printing" and old in ("ready", "standby") and notif.get("on_print_start", True):
            msg = t("notif.started", L).format(filename=filename)

        elif new == "cancelled" and notif.get("on_print_cancelled", True):
            msg = t("notif.cancelled", L).format(filename=filename)

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
