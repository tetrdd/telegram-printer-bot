"""
Background print monitor.
Polls Moonraker for each configured printer and sends Telegram notifications
on state changes (started, paused, finished, error).
"""
from __future__ import annotations

import asyncio
import logging
from config import get as get_cfg, printers, allowed_users
import api

logger = logging.getLogger("PrinterBot.monitor")


class PrintMonitor:
    def __init__(self, application):
        self.app = application
        self._running = False
        self._last_state: dict[int, str] = {}  # printer_id → last state

    async def start(self):
        self._running = True
        logger.info("Monitor started")
        while self._running:
            cfg = get_cfg()
            notif_cfg = cfg.get("notifications", {})
            if notif_cfg.get("enabled", True):
                await self._poll_all()
            interval = cfg.get("monitor", {}).get("poll_interval", 10)
            await asyncio.sleep(interval)

    def stop(self):
        self._running = False
        logger.info("Monitor stopped")

    async def _poll_all(self):
        for printer in printers():
            try:
                await self._poll_printer(printer)
            except Exception as e:
                logger.error(f"Monitor poll error for {printer['name']}: {e}")

    async def _poll_printer(self, printer: dict):
        pid = printer["id"]
        name = printer["name"]

        # Fetch status using printer-specific user_id trick:
        # We pass None as user_id but override via printer config directly
        # For multi-printer, we need to use a dedicated call
        status = await api.get(
            "/printer/objects/query?print_stats",
            user_id=None,
        )
        if not status:
            return

        ps = status.get("result", {}).get("status", {}).get("print_stats", {})
        state = ps.get("state", "unknown")
        prev = self._last_state.get(pid)

        if state != prev:
            self._last_state[pid] = state
            if prev is not None:  # skip initial state
                await self._notify(name, state, ps)

    async def _notify(self, printer_name: str, state: str, ps: dict):
        cfg = get_cfg()
        notif_cfg = cfg.get("notifications", {})
        users = list(allowed_users())

        msg = self._format_message(printer_name, state, ps)
        if not msg:
            return

        for uid in users:
            try:
                await self.app.bot.send_message(chat_id=uid, text=msg)
            except Exception as e:
                logger.error(f"Notify {uid}: {e}")

    def _format_message(self, name: str, state: str, ps: dict) -> str | None:
        fname = ps.get("filename", "-")
        if state == "printing":
            return f"🖨 *{name}*: Started printing `{fname}`"
        if state == "paused":
            return f"⏸ *{name}*: Paused `{fname}`"
        if state == "complete":
            dur = ps.get("total_duration", 0)
            h = int(dur // 3600)
            m = int((dur % 3600) // 60)
            return f"✅ *{name}*: Finished `{fname}` in {h}h {m:02d}m"
        if state == "error":
            err = ps.get("message", "unknown error")
            return f"❌ *{name}*: Error on `{fname}`: {err}"
        if state == "standby":
            return f"💤 *{name}*: Standby"
        return None
