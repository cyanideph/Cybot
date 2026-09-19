"""Supabase adapter used by the Pydroid bot."""
from __future__ import annotations
import logging
import re
from typing import Any
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY, BOT_SENDER_ID, BOT_NAME

log = logging.getLogger("uzzapbot.database")


class Database:
    def __init__(self) -> None:
        self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.last_id = self._latest_id()
        log.info("Polling starts after room_messages id=%s", self.last_id)

    def _latest_id(self) -> int:
        r = self.client.table("room_messages").select("id").order("id", desc=True).limit(1).execute()
        rows = r.data or []
        return int(rows[0]["id"]) if rows else 0

    def poll_messages(self) -> list[dict[str, Any]]:
        # Drain in pages so a busy interval (>100 new messages) is never
        # skipped: last_id only advances after each page is fully read.
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
            self.last_id = max(int(x["id"]) for x in rows)
            for x in rows:
                sender = str(x.get("sender") or "")
                if str(x.get("sender_id") or "") == BOT_SENDER_ID or sender.casefold() == BOT_NAME.casefold():
                    continue
                result.append(x)
            if len(rows) < 100:
                break
        return result

    def random_emoticon(self) -> str:
        r = self.client.rpc("uzzapbot_random_emoticon", {}).execute()
        return str(r.data or "")

    def send(self, room_name: str, body: str) -> None:
        # Keep bot output compatible with the legacy Uzzap client: replace
        # ordinary Unicode emoji with an app-picker emoticon token.
        body = re.sub(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", lambda _: self.random_emoticon(), str(body))
        log.info('SEND room="%s" body=%r', room_name, body)
        self.client.rpc(
            "room_bot_message",
            {"p_room": room_name, "p_body": body, "p_is_system": False},
        ).execute()

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

    def poll_new_participants(self, seen: set[str]) -> list[dict[str, Any]]:
        # Only consider recently active participants; avoids a full table
        # scan as membership grows.
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
            if key not in seen:
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
        # Persist the complete exported state in one SECURITY DEFINER RPC.
        # This makes session + players atomic and preserves newer fields
        # (clues, cycle state, reply history, etc.) across restarts.
        result = self.client.rpc(
            "uzzapbot_save_game_state",
            {"p_state": state},
        ).execute()
        if not result.data:
            raise RuntimeError("Game state save returned no session id")
        return int(result.data)

    def delete_game_state(self, room: str) -> None:
        self.client.table("game_sessions").delete().eq("room_name", room).execute()
