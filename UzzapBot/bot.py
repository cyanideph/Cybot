"""Pydroid 3 entry point for UzzapBot."""
from __future__ import annotations
import logging,time
from config import (
    BOT_NAME, ADMIN_IDS, POLL_SECONDS, DEFAULT_POINTS, DEFAULT_LIMIT, validate,
    AI_ENABLED, AI_IDLE_MINUTES, AI_INACTIVE_MINUTES, AI_COOLDOWN_MINUTES,
    AI_MAX_MESSAGES_PER_HOUR, AI_MAX_MESSAGES_PER_DAY, AI_DRY_RUN,
    AI_MAX_REQUESTS_PER_DAY, AI_MIN_CONFIDENCE, GEMINI_API_KEY, GEMINI_FLASH_MODEL,
    AI_EMBEDDING_DIMENSIONS,
)
from database import Database
from game_engine import GameEngine
from ai.activity_engine import ActivityEngine
from ai.gemini_decision import GeminiDecisionClient
from ai.decision_engine import DecisionEngine
from ai.room_context import RoomContextManager
from ai.embedding import GeminiEmbedding

logging.basicConfig(level=logging.INFO,format="%(asctime)s | %(levelname)s | %(message)s")
log=logging.getLogger("uzzapbot")

