"""Supabase adapter used by the Pydroid bot."""
from __future__ import annotations
import logging
from typing import Any
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY, BOT_SENDER_ID, BOT_NAME

log = logging.getLogger("uzzapbot.database")


class Database:
    def __init__(self) -> None:
        self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.last_id = self._load_cursor()
        log.info("Polling starts after durable room_messages cursor=%s", self.last_id)

    def _load_cursor(self) -> int:
        """Load the durable bot cursor, initializing it once at the current tail."""
        r = self.client.rpc("uzzapbot_get_cursor", {}).execute()
        if r.data is None:
            raise RuntimeError("UzzapBot cursor RPC returned no value")
        return int(r.data)

    def _advance_cursor(self, previous_id: int, message_id: int) -> None:
        """Persist one successful cursor step; never skip over an unprocessed id."""
        r = self.client.rpc(
            "uzzapbot_advance_cursor",
            {
                "p_previous_id": int(previous_id),
                "p_message_id": int(message_id),
            },
        ).execute()
        if not bool(r.data):
            raise RuntimeError(
                f"UzzapBot cursor advance rejected: expected {previous_id}, message {message_id}"
            )
        self.last_id = int(message_id)

    def claim_message(self, message_id: int) -> bool:
        """Atomically claim a message so multiple bot workers cannot process it twice."""
        r = self.client.rpc(
            "uzzapbot_claim_message",
            {"p_message_id": int(message_id)},
        ).execute()
        return bool(r.data)

    def poll_messages(self) -> list[dict[str, Any]]:
        """Drain messages without advancing past a failed claim.

        The durable cursor is advanced only after a row is either successfully
        claimed, already claimed by another worker, or explicitly identified as
        a bot-authored message. If claim/advance raises, processing stops and
        the cursor remains immediately before the failed row so the next poll
        can retry it.
        """
        result: list[dict[str, Any]] = []
        while True:
            r = (
                self.client.table("room_messages")
                .select("id,room_name,sender,body,is_system,created_at,sender_id")
                .gt("id", self.last_id)
                .order("id")
                .limit(100)
                .execute()
            )
            rows = r.data or []
            if not rows:
                break

            for x in rows:
                message_id = int(x["id"])
                sender = str(x.get("sender") or "")
                is_bot_message = (
                    str(x.get("sender_id") or "") == BOT_SENDER_ID
                    or sender.casefold() == BOT_NAME.casefold()
                )

                if not is_bot_message and self.claim_message(message_id):
                    result.append(x)

                self._advance_cursor(self.last_id, message_id)

            if len(rows) < 100:
                break
        return result

    def send(self, room_name: str, body: str) -> None:
        """Store bot output unchanged; Android owns all emoticon rendering."""
        body = str(body)
        log.info('SEND room="%s" body=%r', room_name, body)
        self.client.rpc(
            "room_bot_message",
            {"p_room": room_name, "p_body": body, "p_is_system": False},
        ).execute()

    def load_room_activity(self) -> list[dict[str, Any]]:
        return self.client.table("uzzapbot_room_activity").select(
            "room_name,enabled,idle_threshold_seconds,inactive_threshold_seconds,cooldown_seconds,"
            "max_messages_per_hour,max_messages_per_day,last_human_activity_at,last_bot_activity_at,"
            "activity_state,human_message_count_hour,human_message_count_day"
        ).execute().data or []

    def save_room_activity(self, state: dict[str, Any]) -> None:
        payload = {
            "room_name": str(state["room_name"]),
            "enabled": bool(state.get("enabled", False)),
            "idle_threshold_seconds": int(state.get("idle_threshold_seconds", 900)),
            "inactive_threshold_seconds": int(state.get("inactive_threshold_seconds", 3600)),
            "cooldown_seconds": int(state.get("cooldown_seconds", 1800)),
            "max_messages_per_hour": int(state.get("max_messages_per_hour", 3)),
            "max_messages_per_day": int(state.get("max_messages_per_day", 20)),
            "last_human_activity_at": state.get("last_human_activity_at"),
            "last_bot_activity_at": state.get("last_bot_activity_at"),
            "activity_state": str(state.get("activity_state", "INACTIVE")),
            "human_message_count_hour": int(state.get("human_message_count_hour", 0)),
            "human_message_count_day": int(state.get("human_message_count_day", 0)),
        }
        self.client.table("uzzapbot_room_activity").upsert(payload, on_conflict="room_name").execute()

    def get_room_settings(self, room: str) -> dict[str, Any]:
        defaults = {"activated": False, "locked": False, "wcbot": False,
                    "welcome_message": "welcome to {room} {nickname}", "challenge_room": ""}
        rows = self.client.table("uzzapbot_room_settings").select(
            "room_name,activated,locked,wcbot,welcome_message,challenge_room"
        ).eq("room_name", room).limit(1).execute().data or []
        if not rows:
            return defaults
        row = rows[0]
        return {k: row.get(k, v) for k, v in defaults.items()}

    def save_room_settings(self, room: str, settings: dict[str, Any]) -> None:
        payload = {
            "room_name": room,
            "activated": bool(settings.get("activated")),
            "locked": bool(settings.get("locked")),
            "wcbot": bool(settings.get("wcbot")),
            "welcome_message": str(settings.get("welcome_message") or "welcome to {room} {nickname}"),
            "challenge_room": str(settings.get("challenge_room") or ""),
        }
        self.client.table("uzzapbot_room_settings").upsert(payload, on_conflict="room_name").execute()

    def claim_welcome(self, room: str, username: str) -> bool:
        """Durably claim a welcome so restarts cannot send it twice."""
        r = self.client.rpc(
            "uzzapbot_claim_welcome",
            {"p_room_name": room, "p_username": username},
        ).execute()
        return bool(r.data)

    def poll_new_participants(self, seen: set[str]) -> list[dict[str, Any]]:
        from datetime import datetime, timedelta, timezone
        cutoff = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
        rows = self.client.table("room_participants").select(
            "room_name,username,last_ping"
        ).gt("last_ping", cutoff).execute().data or []
        new = []
        for row in rows:
            room = str(row.get("room_name") or "").strip()
            username = str(row.get("username") or "").strip()
            if not room or not username:
                continue
            key = room + "\x00" + username.casefold()
            if key in seen:
                continue

            # Only consume the durable welcome token when WCBOT is actually
            # enabled. This preserves the ability to enable WCBOT for a recent
            # joiner while preventing duplicate welcomes after a restart.
            settings = self.get_room_settings(room)
            if not bool(settings.get("wcbot")):
                continue
            if not self.claim_welcome(room, username):
                seen.add(key)
                continue

            seen.add(key)
            new.append(row)
        return new

    def profile(self, user_id: str | None, username: str | None) -> dict[str, Any] | None:
        if user_id:
            r = self.client.table("profiles").select("id,username,nickname").eq("id", user_id).limit(1).execute()
            if r.data:
                return r.data[0]
        if username:
            r = self.client.table("profiles").select("id,username,nickname").eq("username", username).limit(1).execute()
            if r.data:
                return r.data[0]
        return None

    def load_game_state(self) -> list[dict[str, Any]]:
        sessions = self.client.table("game_sessions").select(
            "id,room_name,game,mode,current_game,points,limit_count,endless,paused,question_number,question,answer,clue_text,used_questions,state_json"
        ).order("id").execute().data or []
        if not sessions:
            return []
        players = self.client.table("game_players").select(
            "session_id,user_id,username,nickname,score,correct,attempts"
        ).order("id").execute().data or []
        by_session = {}
        for p in players:
            by_session.setdefault(int(p["session_id"]), []).append(p)
        states = []
        for s in sessions:
            state = s.get("state_json")
            if isinstance(state, dict) and state:
                state = dict(state)
            else:
                state = {
                    "room": s["room_name"],
                    "game": s["game"],
                    "mode": s.get("mode") or s["game"],
                    "current_game": s.get("current_game") or s["game"],
                    "points": s["points"],
                    "limit": s["limit_count"],
                    "endless": s["endless"],
                    "paused": s["paused"],
                    "number": s["question_number"],
                    "question": s["question"],
                    "answer": s["answer"],
                    "clue_text": s["clue_text"],
                    "used_questions": s.get("used_questions") or [],
                }
            state["players"] = by_session.get(int(s["id"]), [])
            states.append(state)
        return states

    def save_game_state(self, state: dict[str, Any]) -> int:
        result = self.client.rpc(
            "uzzapbot_save_game_state",
            {"p_state": state},
        ).execute()
        if not result.data:
            raise RuntimeError("Game state save returned no session id")
        return int(result.data)

    def delete_game_state(self, room: str) -> None:
        self.client.table("game_sessions").delete().eq("room_name", room).execute()
