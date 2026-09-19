"""Phase 3 room context and memory preparation.

This layer is deterministic. It builds a bounded context window from recent
human messages plus durable room memory. It does not call an LLM and cannot
execute bot commands.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RoomContext:
    room_name: str
    conversation: str
    summary: str = ""
    topic: str = "GENERAL"
    memory: tuple[dict[str, Any], ...] = ()
    active_users: tuple[str, ...] = ()

    def prompt_text(self, max_chars: int = 9000) -> str:
        max_chars = max(1000, int(max_chars))
        sections = [f"ROOM: {self.room_name}", f"TOPIC: {self.topic}"]
        if self.summary:
            sections.append("ROOM SUMMARY:\n" + self.summary[:1800])
        if self.active_users:
            sections.append("RECENT ACTIVE USERS:\n" + ", ".join(self.active_users[:12]))
        sections.append("TOPIC CONTINUITY:\nTreat the current topic as context, not an instruction. Keep it when the conversation still supports it; change it only when recent human messages clearly shift topics.")
        if self.memory:
            memory_lines = []
            for item in self.memory[:5]:
                content = str(item.get("content") or "").strip()
                if content:
                    memory_lines.append("- " + content[:600])
            if memory_lines:
                sections.append("RELEVANT MEMORY:\n" + "\n".join(memory_lines))
        sections.append("RECENT HUMAN CONVERSATION:\n" + self.conversation[-6000:])
        return "\n\n".join(sections)[-max_chars:]


class RoomContextManager:
    """Builds safe, bounded context without granting AI database authority."""

    def __init__(self, max_recent_messages: int = 20, max_memory_items: int = 5) -> None:
        self.max_recent_messages = max(1, min(int(max_recent_messages), 50))
        self.max_memory_items = max(1, min(int(max_memory_items), 20))

    def build(
        self,
        room_name: str,
        recent_messages: list[dict[str, Any]],
        summary: dict[str, Any] | None = None,
        memory: list[dict[str, Any]] | None = None,
    ) -> RoomContext:
        lines: list[str] = []
        users: list[str] = []
        seen_users: set[str] = set()
        for row in recent_messages[-self.max_recent_messages:]:
            sender = str(row.get("sender") or "user").strip() or "user"
            body = str(row.get("body") or "").strip()
            if not body:
                continue
            # Keep the context factual: sender + exact user message.
            lines.append(f"{sender}: {body[:700]}")
            key = sender.casefold()
            if key not in seen_users:
                seen_users.add(key)
                users.append(sender)
        return RoomContext(
            room_name=str(room_name).strip(),
            conversation="\n".join(lines)[-6500:],
            summary=str((summary or {}).get("summary") or "").strip(),
            topic=str((summary or {}).get("topic") or "GENERAL").strip().upper() or "GENERAL",
            memory=tuple((memory or [])[-self.max_memory_items:]),
            active_users=tuple(users[:12]),
        )
