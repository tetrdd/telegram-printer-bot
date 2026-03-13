"""
Configuration loader and saver.
Reads config.yaml on startup, provides live save for settings changes.
"""

import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.yaml"

_cfg: dict = {}


def load() -> dict:
    """Load config from disk. Called once at startup."""
    global _cfg
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            "config.yaml not found! Copy the template and fill in your values."
        )
    with open(CONFIG_PATH, encoding="utf-8") as f:
        _cfg = yaml.safe_load(f)
    return _cfg


def save():
    """Persist current config to disk."""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(_cfg, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def get() -> dict:
    """Return the live config dict (mutable)."""
    return _cfg


# ── Convenience accessors ────────────────────────────────────────────────────

def moonraker_url() -> str:
    return _cfg["moonraker"]["url"].rstrip("/")


def api_key() -> str:
    return _cfg["moonraker"].get("api_key", "")


def allowed_users() -> set[int]:
    return set(_cfg["telegram"]["allowed_user_ids"])


def lang() -> str:
    return _cfg.get("language", "en")


def set_lang(language: str):
    _cfg["language"] = language
    save()
