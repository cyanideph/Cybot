"""Configuration for UzzapBot (Pydroid 3)."""
from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

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
AI_IDLE_MINUTES = int(os.getenv("AI_IDLE_MINUTES", "15"))
AI_INACTIVE_MINUTES = int(os.getenv("AI_INACTIVE_MINUTES", "60"))
AI_COOLDOWN_MINUTES = int(os.getenv("AI_COOLDOWN_MINUTES", "30"))
AI_MAX_MESSAGES_PER_HOUR = int(os.getenv("AI_MAX_MESSAGES_PER_HOUR", "3"))
AI_MAX_MESSAGES_PER_DAY = int(os.getenv("AI_MAX_MESSAGES_PER_DAY", "20"))
AI_MAX_REQUESTS_PER_DAY = int(os.getenv("AI_MAX_REQUESTS_PER_DAY", "100"))
AI_MIN_CONFIDENCE = float(os.getenv("AI_MIN_CONFIDENCE", "0.75"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_FLASH_MODEL = os.getenv("GEMINI_FLASH_MODEL", "gemini-3-flash-preview")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-2")
AI_EMBEDDING_DIMENSIONS = int(os.getenv("AI_EMBEDDING_DIMENSIONS", "768")).strip()

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
