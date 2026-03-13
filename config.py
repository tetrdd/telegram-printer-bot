"""
Configuration loader and saver.
Reads config.yaml on startup, provides live save for settings changes.
Supports single-printer (legacy) and multi-printer configs.
"""

import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.yaml"

_cfg: dict = {}
_printers: list[dict] = []


def load() -> dict:
    """Load config from disk. Called once at startup."""
    global _cfg, _printers
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            "config.yaml not found! Copy the template and fill in your values."
        )
    with open(CONFIG_PATH, encoding="utf-8") as f:
        _cfg = yaml.safe_load(f)
    _printers = _build_printer_list()
    return _cfg


def save():
    """Persist current config to disk."""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(_cfg, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def get() -> dict:
    """Return the live config dict (mutable)."""
    return _cfg


# ── Printer list ─────────────────────────────────────────────────────────────

def _build_printer_list() -> list[dict]:
    """
    Build a normalized list of printers from config.
    Supports both single-printer (moonraker: ...) and multi-printer (printers: [...]).
    """
    if "printers" in _cfg:
        printers = []
        for i, p in enumerate(_cfg["printers"]):
            printers.append({
                "id": i,
                "name": p.get("name", f"Printer {i + 1}"),
                "moonraker": p.get("moonraker", {}),
                "camera": p.get("camera", {}),
            })
        return printers

    # Legacy single-printer config
    return [{
        "id": 0,
        "name": _cfg.get("printer_name", "Printer"),
        "moonraker": _cfg.get("moonraker", {}),
        "camera": _cfg.get("camera", {}),
    }]


def printers() -> list[dict]:
    """Return the list of configured printers."""
    return _printers


def is_multi_printer() -> bool:
    """True if more than one printer is configured."""
    return len(_printers) > 1


def get_printer(printer_id: int) -> dict | None:
    """Get a printer config by its ID."""
    for p in _printers:
        if p["id"] == printer_id:
            return p
    return None


def default_printer() -> dict:
    """Return the first printer (fallback)."""
    return _printers[0]


# ── Active printer per user ──────────────────────────────────────────────────

# {user_id: printer_id}
_active_printer: dict[int, int] = {}


def active_printer_for(user_id: int) -> dict:
    """Get the active printer config for a user."""
    pid = _active_printer.get(user_id, 0)
    p = get_printer(pid)
    return p if p else default_printer()


def set_active_printer(user_id: int, printer_id: int):
    """Set which printer a user is controlling."""
    _active_printer[user_id] = printer_id


def active_moonraker_url(user_id: int) -> str:
    """Moonraker URL for the user's active printer."""
    p = active_printer_for(user_id)
    return p["moonraker"].get("url", "").rstrip("/")


def active_api_key(user_id: int) -> str:
    """API key for the user's active printer."""
    p = active_printer_for(user_id)
    return p["moonraker"].get("api_key", "")


def active_camera(user_id: int) -> dict:
    """Camera config for the user's active printer."""
    p = active_printer_for(user_id)
    return p.get("camera", {})


def active_printer_name(user_id: int) -> str:
    """Display name for the user's active printer."""
    p = active_printer_for(user_id)
    return p.get("name", "Printer")


# ── Legacy convenience accessors (backward-compatible, use printer 0) ────────

def moonraker_url() -> str:
    return default_printer()["moonraker"].get("url", "").rstrip("/")


def api_key() -> str:
    return default_printer()["moonraker"].get("api_key", "")


def allowed_users() -> set[int]:
    return set(_cfg["telegram"]["allowed_user_ids"])


def lang() -> str:
    return _cfg.get("language", "en")


def set_lang(language: str):
    _cfg["language"] = language
    save()
