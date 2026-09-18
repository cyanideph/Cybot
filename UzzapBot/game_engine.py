"""Pydroid-safe Uzzap game engine using the original Gamebot data files."""
from __future__ import annotations
import random
import re
from dataclasses import dataclass, field
from pathlib import Path
from config import DATA_DIR, DEFAULT_POINTS, DEFAULT_LIMIT

@dataclass
class Player:
    user_id: str
    username: str
    nickname: str
    score: int = 0
    correct: int = 0
    attempts: int = 0

@dataclass
class Session:
    room: str
    game: str
    points: int = DEFAULT_POINTS
    limit: int = DEFAULT_LIMIT
    paused: bool = False
    question: str = ""
    answer: str = ""
    clue_text: str = ""
    number: int = 0
    players: dict[str, Player] = field(default_factory=dict)

class GameEngine:
    ALIASES = {"gta": "gtaforeign", "gta_foreign": "gtaforeign", "gta_opm": "gtaopm",
               "words": "wordhunt", "tagalog": "tagalog", "rebus": "logic"}
    GAMES = {"math","mathminus","mathmultiply","algebra1","algebra2","algebra3",
             "trivia","anime","gtaforeign","gtaopm","logic","wordhunt","tagalog","twist"}

    def __init__(self) -> None:
        self.sessions: dict[str, Session] = {}
        self.datasets = {name:self._load(name) for name in (
            "Zgen-info.txt","Zanime-trivia.txt","Zgta-foreign.txt","Zgta-opm.txt",
            "Zlogic.txt","words.txt","salita.txt")}

    def _load(self, name: str) -> list[str]:
        p = Path(DATA_DIR) / name
        if not p.exists():
            return []
        return [x.strip() for x in p.read_text(encoding="utf-8", errors="ignore").splitlines() if x.strip()]

    def _parse_qa(self, rows: list[str], sep=",") -> list[tuple[str,str]]:
        out=[]
        for row in rows:
            parts=row.split(sep,2)
            if len(parts)>=3: out.append((parts[1].strip(),parts[2].strip()))
        return out

    def _normalize(self, s: str) -> str:
        s=re.sub(r"\[[^\]]+\]","",s).casefold()
        return re.sub(r"[^a-z0-9]+","",s)

    def start(self, room: str, game: str, points: int|None=None, limit: int|None=None) -> Session:
        game=self.ALIASES.get(game.casefold(),game.casefold())
        if game not in self.GAMES: raise ValueError(f"Unknown game: {game}")
        s=Session(room,game,points or DEFAULT_POINTS,limit or DEFAULT_LIMIT)
        self.sessions[room]=s
        self._next(s)
        return s

    def get(self, room: str) -> Session|None: return self.sessions.get(room)
    def stop(self, room: str) -> None: self.sessions.pop(room,None)

    def _next(self,s: Session) -> str:
        s.number += 1
        s.clue_text=""
        if s.game in {"math","mathminus","mathmultiply"}:
            a,b=random.randint(2,99),random.randint(2,20)
            if s.game=="math": s.question=f"{a} + {b} = ?"; s.answer=str(a+b)
            elif s.game=="mathminus":
                if b>a: a,b=b,a
                s.question=f"{a} - {b} = ?"; s.answer=str(a-b)
            else: s.question=f"{a} x {b} = ?"; s.answer=str(a*b)
        elif s.game.startswith("algebra"):
            x=random.randint(2,20); a=random.randint(2,9); b=a*x
            s.question=f"Solve: {a}x = {b}"; s.answer=str(x)
        elif s.game=="trivia":
            q=random.choice(self._parse_qa(self.datasets["Zgen-info.txt"])); s.question=q[0]; s.answer=q[1]
        elif s.game=="anime":
            q=random.choice(self._parse_qa(self.datasets["Zanime-trivia.txt"])); s.question=q[0]; s.answer=q[1]
        elif s.game=="gtaforeign":
            q=random.choice(self._parse_qa(self.datasets["Zgta-foreign.txt"])); s.question=f"Artist of: {q[0]}"; s.answer=q[1]
        elif s.game=="gtaopm":
            q=random.choice(self._parse_qa(self.datasets["Zgta-opm.txt"])); s.question=f"Artist of: {q[0]}"; s.answer=q[1]
        elif s.game=="logic":
            rows=self.datasets["Zlogic.txt"]; row=random.choice(rows)
            parts=row.split(",",2); s.question=parts[1] if len(parts)>2 else row; s.answer=parts[2] if len(parts)>2 else ""
        elif s.game=="wordhunt":
            words=self.datasets["words.txt"]; s.answer=random.choice(words).strip(); s.question=f"Unscramble: {''.join(random.sample(s.answer,len(s.answer)))}"
        elif s.game=="tagalog":
            s.answer=random.choice(self.datasets["salita.txt"]).strip(); s.question=f"Word hunt: {s.answer}"
        else:
            words=[w for w in self.datasets["words.txt"] if len(w)>=5]
            s.answer=random.choice(words).strip(); letters=list(s.answer); random.shuffle(letters); s.question=f"TWIST: {''.join(letters)}"
        return self.repost(s.room)

    def next_question(self,s: Session|None) -> str:
        return "[c08]No active game." if not s else self._next(s)

    def answer(self, room: str, uid: str, username: str, nickname: str, text: str) -> tuple[bool,str]:
        s=self.sessions.get(room)
        if not s or s.paused: return False,""
        p=s.players.setdefault(uid,Player(uid,username,nickname))
        p.attempts += 1
        if self._normalize(text)==self._normalize(s.answer):
            p.correct += 1; p.score += s.points
            response=f"[c10]Correct, {nickname}! +{s.points} points."
            response += "\n"+self._next(s)
            return True,response
        return False,""

    def clue(self,room: str) -> str:
        s=self.sessions.get(room)
        if not s: return "[c08]No active game."
        if not s.answer: return "[c08]No clue available."
        n=max(1,len(s.answer)//3)
        s.clue_text="".join(ch if i<n else "_" for i,ch in enumerate(s.answer))
        return f"[c12]Clue: {s.clue_text}"

    def repost(self,room: str) -> str:
        s=self.sessions.get(room)
        if not s: return "[c08]No active game."
        return f"[c03]{s.game.upper()} #{s.number}\n[c01]{s.question}\n[c07]Points: {s.points}"

    def status(self,room: str) -> str:
        s=self.sessions.get(room)
        if not s: return "[c08]No active game."
        return f"[c03]Game: {s.game} | Question: {s.number} | Paused: {'yes' if s.paused else 'no'} | Players: {len(s.players)}"

    def leaderboard_text(self,room: str) -> str:
        s=self.sessions.get(room)
        if not s: return "[c08]No active game."
        rows=sorted(s.players.values(),key=lambda p:(p.score,p.correct),reverse=True)
        if not rows: return "[c12]No scores yet."
        return "[c03]LEADERBOARD\n"+"\n".join(f"{i}. {p.nickname} — {p.score}" for i,p in enumerate(rows,1))
