"""
Moonraker API client.
All communication with the printer goes through here.
"""

import logging
import urllib.parse
import aiohttp
from config import moonraker_url, api_key

logger = logging.getLogger("PrinterBot.api")

_TIMEOUT = aiohttp.ClientTimeout(total=10)


def _headers() -> dict:
    h = {"Content-Type": "application/json"}
    key = api_key()
    if key:
        h["X-Api-Key"] = key
    return h


async def get(endpoint: str) -> dict | None:
    """GET request to Moonraker."""
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(
                f"{moonraker_url()}{endpoint}",
                headers=_headers(),
                timeout=_TIMEOUT,
            ) as r:
                return await r.json() if r.status == 200 else None
    except Exception as e:
        logger.error(f"GET {endpoint}: {e}")
        return None


async def post(endpoint: str, data: dict = None) -> dict | None:
    """POST request to Moonraker."""
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(
                f"{moonraker_url()}{endpoint}",
                headers=_headers(),
                json=data or {},
                timeout=_TIMEOUT,
            ) as r:
                return await r.json() if r.status == 200 else None
    except Exception as e:
        logger.error(f"POST {endpoint}: {e}")
        return None


async def delete(endpoint: str) -> dict | None:
    """DELETE request to Moonraker."""
    try:
        async with aiohttp.ClientSession() as s:
            async with s.delete(
                f"{moonraker_url()}{endpoint}",
                headers=_headers(),
                timeout=_TIMEOUT,
            ) as r:
                return await r.json() if r.status == 200 else None
    except Exception as e:
        logger.error(f"DELETE {endpoint}: {e}")
        return None


async def gcode(cmd: str) -> str | None:
    """Send a GCode command via Moonraker."""
    encoded = urllib.parse.quote(cmd)
    data = await post(f"/printer/gcode/script?script={encoded}")
    return "ok" if data else None


async def snapshot() -> bytes | None:
    """Fetch camera snapshot image bytes."""
    from config import get as get_cfg
    url = get_cfg().get("camera", {}).get("snapshot_url", "")
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

async def printer_status() -> dict | None:
    """Get print stats, progress, and temperatures in one call."""
    data = await get(
        "/printer/objects/query?print_stats&display_status&virtual_sdcard&extruder&heater_bed"
    )
    if not data:
        return None
    return data.get("result", {}).get("status", {})


async def printer_objects() -> list[str]:
    """Get list of all printer objects (for macro discovery etc)."""
    data = await get("/printer/objects/list")
    if not data:
        return []
    return data.get("result", {}).get("objects", [])


async def file_list() -> list[dict]:
    """Get list of gcode files."""
    data = await get("/server/files/list?root=gcodes")
    if not data:
        return []
    return data.get("result", [])


async def file_metadata(filename: str) -> dict | None:
    """Get metadata for a specific gcode file."""
    encoded = urllib.parse.quote(filename, safe="")
    data = await get(f"/server/files/metadata?filename={encoded}")
    if not data:
        return None
    return data.get("result")


async def start_print(filename: str) -> bool:
    encoded = urllib.parse.quote(filename, safe="")
    r = await post(f"/printer/print/start?filename={encoded}")
    return r is not None


async def pause_print() -> bool:
    return (await post("/printer/print/pause")) is not None


async def resume_print() -> bool:
    return (await post("/printer/print/resume")) is not None


async def cancel_print() -> bool:
    return (await post("/printer/print/cancel")) is not None


async def emergency_stop() -> bool:
    return (await post("/printer/emergency_stop")) is not None


async def firmware_restart() -> bool:
    return (await post("/printer/firmware_restart")) is not None


async def host_reboot() -> bool:
    return (await post("/machine/reboot")) is not None


async def delete_file(filename: str) -> bool:
    encoded = urllib.parse.quote(filename, safe="")
    return (await delete(f"/server/files/gcodes/{encoded}")) is not None


async def server_info() -> dict | None:
    data = await get("/server/info")
    return data.get("result") if data else None


async def system_info() -> dict | None:
    data = await get("/machine/system_info")
    return data.get("result", {}).get("system_info") if data else None


async def proc_stats() -> dict | None:
    data = await get("/machine/proc_stats")
    return data.get("result") if data else None
