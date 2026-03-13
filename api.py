"""
Moonraker API client.
All communication with the printer goes through here.
Supports multi-printer: pass user_id to route to the correct Moonraker instance.
"""

import logging
import urllib.parse
import aiohttp
from config import active_moonraker_url, active_api_key, active_camera, default_printer

logger = logging.getLogger("PrinterBot.api")

_TIMEOUT = aiohttp.ClientTimeout(total=10)


def _url_for(user_id: int | None) -> str:
    """Resolve Moonraker base URL for a user (or default)."""
    if user_id is not None:
        return active_moonraker_url(user_id)
    return default_printer()["moonraker"].get("url", "").rstrip("/")


def _headers(user_id: int | None) -> dict:
    h = {"Content-Type": "application/json"}
    if user_id is not None:
        key = active_api_key(user_id)
    else:
        key = default_printer()["moonraker"].get("api_key", "")
    if key:
        h["X-Api-Key"] = key
    return h


async def get(endpoint: str, user_id: int | None = None) -> dict | None:
    """GET request to Moonraker."""
    base = _url_for(user_id)
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(
                f"{base}{endpoint}",
                headers=_headers(user_id),
                timeout=_TIMEOUT,
            ) as r:
                return await r.json() if r.status == 200 else None
    except Exception as e:
        logger.error(f"GET {endpoint}: {e}")
        return None


async def post(endpoint: str, data: dict = None, user_id: int | None = None) -> dict | None:
    """POST request to Moonraker."""
    base = _url_for(user_id)
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(
                f"{base}{endpoint}",
                headers=_headers(user_id),
                json=data or {},
                timeout=_TIMEOUT,
            ) as r:
                return await r.json() if r.status == 200 else None
    except Exception as e:
        logger.error(f"POST {endpoint}: {e}")
        return None


async def delete(endpoint: str, user_id: int | None = None) -> dict | None:
    """DELETE request to Moonraker."""
    base = _url_for(user_id)
    try:
        async with aiohttp.ClientSession() as s:
            async with s.delete(
                f"{base}{endpoint}",
                headers=_headers(user_id),
                timeout=_TIMEOUT,
            ) as r:
                return await r.json() if r.status == 200 else None
    except Exception as e:
        logger.error(f"DELETE {endpoint}: {e}")
        return None


async def gcode(cmd: str, user_id: int | None = None) -> str | None:
    """Send a GCode command via Moonraker."""
    encoded = urllib.parse.quote(cmd)
    data = await post(f"/printer/gcode/script?script={encoded}", user_id=user_id)
    return "ok" if data else None


async def snapshot(user_id: int | None = None) -> bytes | None:
    """Fetch camera snapshot image bytes."""
    if user_id is not None:
        cam = active_camera(user_id)
    else:
        from config import get as get_cfg
        cam = get_cfg().get("camera", {})
    url = cam.get("snapshot_url", "")
    if not url:
        return None
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status == 200:
                    return await r.read()
    except Exception as e:
        logger.error(f"Snapshot: {e}")
    return None


# ── High-level queries ───────────────────────────────────────────────────────

async def printer_status(user_id: int | None = None) -> dict | None:
    """Get print stats, progress, and temperatures in one call."""
    data = await get(
        "/printer/objects/query?print_stats&display_status&virtual_sdcard&extruder&heater_bed",
        user_id=user_id,
    )
    if not data:
        return None
    return data.get("result", {}).get("status", {})


async def printer_objects(user_id: int | None = None) -> list[str]:
    """Get list of all printer objects (for macro discovery etc)."""
    data = await get("/printer/objects/list", user_id=user_id)
    if not data:
        return []
    return data.get("result", {}).get("objects", [])


async def file_list(user_id: int | None = None) -> list[dict]:
    """Get list of gcode files."""
    data = await get("/server/files/list?root=gcodes", user_id=user_id)
    if not data:
        return []
    return data.get("result", [])


async def file_metadata(filename: str, user_id: int | None = None) -> dict | None:
    """Get metadata for a specific gcode file."""
    encoded = urllib.parse.quote(filename, safe="")
    data = await get(f"/server/files/metadata?filename={encoded}", user_id=user_id)
    if not data:
        return None
    return data.get("result")


async def start_print(filename: str, user_id: int | None = None) -> bool:
    encoded = urllib.parse.quote(filename, safe="")
    r = await post(f"/printer/print/start?filename={encoded}", user_id=user_id)
    return r is not None


async def pause_print(user_id: int | None = None) -> bool:
    return (await post("/printer/print/pause", user_id=user_id)) is not None


async def resume_print(user_id: int | None = None) -> bool:
    return (await post("/printer/print/resume", user_id=user_id)) is not None


async def cancel_print(user_id: int | None = None) -> bool:
    return (await post("/printer/print/cancel", user_id=user_id)) is not None


async def emergency_stop(user_id: int | None = None) -> bool:
    return (await post("/printer/emergency_stop", user_id=user_id)) is not None


async def firmware_restart(user_id: int | None = None) -> bool:
    return (await post("/printer/firmware_restart", user_id=user_id)) is not None


async def host_reboot(user_id: int | None = None) -> bool:
    return (await post("/machine/reboot", user_id=user_id)) is not None


async def delete_file(filename: str, user_id: int | None = None) -> bool:
    encoded = urllib.parse.quote(filename, safe="")
    return (await delete(f"/server/files/gcodes/{encoded}", user_id=user_id)) is not None


async def server_info(user_id: int | None = None) -> dict | None:
    data = await get("/server/info", user_id=user_id)
    return data.get("result") if data else None


async def system_info(user_id: int | None = None) -> dict | None:
    data = await get("/machine/system_info", user_id=user_id)
    return data.get("result", {}).get("system_info") if data else None


async def proc_stats(user_id: int | None = None) -> dict | None:
    data = await get("/machine/proc_stats", user_id=user_id)
    return data.get("result") if data else None
