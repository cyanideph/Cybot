"""Configuration for UzzapBot (Pydroid 3)."""
from __future__ import annotations
import os
from pathlib import Path
from dotenv import dotenv_values, load_dotenv

ROOT = Path(__file__).resolve().parent
_DOTENV_PATH = ROOT / ".env"
_ENV_KEYS_AT_IMPORT = set(os.environ)
_DOTENV_VALUES = dotenv_values(_DOTENV_PATH)
load_dotenv(_DOTENV_PATH)


def _env_source(name: str) -> str:
    """Report where a non-secret setting came from without exposing its value."""
    if name in _ENV_KEYS_AT_IMPORT:
        return "process_environment"
    if _DOTENV_VALUES.get(name) is not None:
        return "dotenv"
    return "default"


def _env_int(name: str, default: int, minimum: int = 0) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        value = int(raw.strip())
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc
    if value < minimum:
        raise RuntimeError(f"{name} must be >= {minimum}")
    return value


SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
# Server-side only. Never put this key in Android, GitHub source, or logs.
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
SUPABASE_KEY = SUPABASE_SERVICE_ROLE_KEY or os.getenv("SUPABASE_KEY", "").strip()
BOT_NAME = os.getenv("BOT_NAME", "uzzapbot").strip()
BOT_SENDER_ID = os.getenv("BOT_SENDER_ID", "").strip()
ADMIN_IDS = {x.strip() for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()}
POLL_SECONDS = float(os.getenv("POLL_SECONDS", "1.0"))
DEFAULT_POINTS = int(os.getenv("DEFAULT_POINTS", "10"))
DEFAULT_LIMIT = int(os.getenv("DEFAULT_LIMIT", "100"))
DATA_DIR = ROOT / "data"

# AI is deliberately opt-in. Phase 1 uses these values only for deterministic
# activity tracking; no model/API call is made by the activity engine.
AI_ENABLED = os.getenv("AI_ENABLED", "false").strip().casefold() == "true"
AI_DRY_RUN = os.getenv("AI_DRY_RUN", "true").strip().casefold() == "true"
# A second explicit global gate is required before any live AI response can be sent.
AI_LIVE_ENABLED = os.getenv("AI_LIVE_ENABLED", "false").strip().casefold() == "true"
AI_ROLLOUT_STAGE = os.getenv("AI_ROLLOUT_STAGE", "disabled").strip().casefold()


def _parse_canary_percent(value: str | None) -> int:
    """Parse the canary percentage with a fail-closed result.

    Canary rollout is intentionally limited to 1-10 percent by the rollout
    gate. Returning 0 for malformed/out-of-range values prevents configuration
    parsing from crashing bot startup and causes the canary gate to reject the
    rollout rather than accidentally enabling traffic.
    """
    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError):
        return 0
    return parsed if 1 <= parsed <= 10 else 0


AI_CANARY_PERCENT = _parse_canary_percent(os.getenv("AI_CANARY_PERCENT", "1"))
AI_IDLE_MINUTES = _env_int("AI_IDLE_MINUTES", 15, minimum=1)
AI_INACTIVE_MINUTES = _env_int("AI_INACTIVE_MINUTES", 60, minimum=1)
AI_COOLDOWN_MINUTES = _env_int("AI_COOLDOWN_MINUTES", 30, minimum=1)
AI_MAX_MESSAGES_PER_HOUR = _env_int("AI_MAX_MESSAGES_PER_HOUR", 3, minimum=1)
AI_MAX_MESSAGES_PER_DAY = _env_int("AI_MAX_MESSAGES_PER_DAY", 20, minimum=1)
AI_MAX_REQUESTS_PER_DAY = _env_int("AI_MAX_REQUESTS_PER_DAY", 100, minimum=1)
AI_MIN_CONFIDENCE = float(os.getenv("AI_MIN_CONFIDENCE", "0.75"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_FLASH_MODEL = os.getenv("GEMINI_FLASH_MODEL", "gemini-3.8-flash")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-2")
AI_EMBEDDING_DIMENSIONS = _env_int("AI_EMBEDDING_DIMENSIONS", 768, minimum=1)

# Non-secret diagnostics used by the AI pass gate. Values are intentionally
# limited to source labels so secrets and raw environment contents are never logged.
AI_CONFIG_SOURCES = {
    "AI_ENABLED": _env_source("AI_ENABLED"),
    "AI_IDLE_MINUTES": _env_source("AI_IDLE_MINUTES"),
    "AI_INACTIVE_MINUTES": _env_source("AI_INACTIVE_MINUTES"),
    "AI_COOLDOWN_MINUTES": _env_source("AI_COOLDOWN_MINUTES"),
    "AI_ROLLOUT_STAGE": _env_source("AI_ROLLOUT_STAGE"),
    "AI_CANARY_PERCENT": _env_source("AI_CANARY_PERCENT"),
    "AI_LIVE_ENABLED": _env_source("AI_LIVE_ENABLED"),
    "AI_DRY_RUN": _env_source("AI_DRY_RUN"),
}


def validate() -> None:
    missing = [
        n for n, v in (
            ("SUPABASE_URL", SUPABASE_URL),
            ("SUPABASE_SERVICE_ROLE_KEY", SUPABASE_SERVICE_ROLE_KEY),
            ("BOT_SENDER_ID", BOT_SENDER_ID),
        )
        if not v or v.startswith("YOUR_")
    ]
    if missing:
        raise RuntimeError("Missing configuration: " + ", ".join(missing))

    if AI_ENABLED and not GEMINI_API_KEY:
        raise RuntimeError("AI_ENABLED=true requires GEMINI_API_KEY")
