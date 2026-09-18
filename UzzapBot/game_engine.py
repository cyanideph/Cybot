"""Pydroid-safe Uzzap game engine using the original Gamebot data files."""
from __future__ import annotations
import random, re, unicodedata
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
    used_questions: set[str] = field(default_factory=set)

class GameEngine:
    ALIASES = {"gta":"gtaforeign", "gta_foreign":"gtaforeign", "gta_opm":"gtaopm", "words":"wordhunt", "rebus":"logic"}
    GAMES = {"math","mathminus","mathmultiply","algebra1","algebra2","algebra3","trivia","anime","gtaforeign","gtaopm","logic","wordhunt","tagalog","twist"}

    def __init__(self) -> None:
        self.sessions = {}
        self.datasets = {name:self._load(name) for name in ("Zgen-info.txt","Zanime-trivia.txt","Zgta-foreign.txt","Zgta-opm.txt","Zlogic.txt","words.txt","salita.txt")}

    def _load(self,name):
        p=Path(DATA_DIR)/name
        return [x.strip() for x in p.read_text(encoding="utf-8",errors="ignore").splitlines() if x.strip()] if p.exists() else []

    def _parse_qa(self,rows):
        out=[]
        for row in rows:
            parts=row.split(",",2)
            if len(parts)>=3 and parts[1].strip() and parts[2].strip(): out.append((parts[1].strip(),parts[2].strip()))
        return out

    def _normalize(self,value):
        value=unicodedata.normalize("NFKC",value)
        value=re.sub(r"\[[^\]]+\]","",value).casefold().strip()
        return "".join(ch for ch in value if ch.isalnum())

    def _pick_qa(self,rows,used):
        qa=self._parse_qa(rows)
        if not qa: raise ValueError("dataset has no valid question/answer rows")
        fresh=[q for q in qa if self._normalize(q[0]) not in used]
        q=random.choice(fresh or qa); used.add(self._normalize(q[0])); return q

    def _pick_word(self,rows,used,min_len=1):
        words=[w.strip() for w in rows if w.strip() and len(w.strip())>=min_len]
        if not words: raise ValueError("word dataset has no usable entries")
        fresh=[w for w in words if self._normalize(w) not in used]
        word=random.choice(fresh or words); used.add(self._normalize(word)); return word

    def start(self,room,game,points=None,limit=None):
        game=self.ALIASES.get(game.casefold(),game.casefold())
        if game not in self.GAMES: raise ValueError(f"Unknown game: {game}")
        points=DEFAULT_POINTS if points is None else points; limit=DEFAULT_LIMIT if limit is None else limit
        if not 1<=points<=1000: raise ValueError("points must be between 1 and 1000")
        if not 1<=limit<=1000: raise ValueError("limit must be between 1 and 1000")
        s=Session(room,game,points,limit); self.sessions[room]=s; self._next(s); return s

    def get(self,room): return self.sessions.get(room)
    def stop(self,room): self.sessions.pop(room,None)

    def _next(self,s):
        if s.number>=s.limit: return self.finish(s)
        s.number+=1; s.clue_text=""
        if s.game in {"math","mathminus","mathmultiply"}:
            a,b=random.randint(2,99),random.randint(2,20)
            if s.game=="math": s.question=f"{a} + {b} = ?"; s.answer=str(a+b)
            elif s.game=="mathminus":
                if b>a: a,b=b,a
                s.question=f"{a} - {b} = ?"; s.answer=str(a-b)
            else: s.question=f"{a} x {b} = ?"; s.answer=str(a*b)
        elif s.game=="algebra1":
            x=random.randint(2,20); a=random.randint(2,9); b=a*x; s.question=f"Solve: {a}x = {b}"; s.answer=str(x)
        elif s.game=="algebra2":
            x=random.randint(2,20); a=random.randint(2,9); c=random.randint(1,15); b=a*x+c; s.question=f"Solve: {a}x + {c} = {b}"; s.answer=str(x)
        elif s.game=="algebra3":
            x=random.randint(2,20); a=random.randint(2,8); d=random.randint(1,a-1); c=random.randint(1,15); b=(a-d)*x+c; s.question=f"Solve: {a}x + {c} = {d}x + {b}"; s.answer=str(x)
        elif s.game=="trivia":
            q=self._pick_qa(self.datasets["Zgen-info.txt"],s.used_questions); s.question=q[0]; s.answer=q[1]
        elif s.game=="anime":
            q=self._pick_qa(self.datasets["Zanime-trivia.txt"],s.used_questions); s.question=q[0]; s.answer=q[1]
        elif s.game=="gtaforeign":
            q=self._pick_qa(self.datasets["Zgta-foreign.txt"],s.used_questions); s.question=f"Artist of: {q[0]}"; s.answer=q[1]
        elif s.game=="gtaopm":
            q=self._pick_qa(self.datasets["Zgta-opm.txt"],s.used_questions); s.question=f"Artist of: {q[0]}"; s.answer=q[1]
        elif s.game=="logic":
            q=self._pick_qa(self.datasets["Zlogic.txt"],s.used_questions); s.question=q[0]; s.answer=q[1]
        else:
            dataset="words.txt" if s.game!="tagalog" else "salita.txt"
            word=self._pick_word(self.datasets[dataset],s.used_questions,5 if s.game!="tagalog" else 3)
            s.answer=word; letters=list(word); scrambled=word
            if len(letters)>1:
                for _ in range(10):
                    random.shuffle(letters); scrambled="".join(letters)
                    if self._normalize(scrambled)!=self._normalize(word): break
            prefix="Unscramble" if s.game=="wordhunt" else ("Tagalog scramble" if s.game=="tagalog" else "TWIST")
            s.question=f"{prefix}: {scrambled}"
        return self.repost(s.room)

    def next_question(self,s):
        return "[c08]No active game." if not s else self._next(s)

    def finish(self,s):
        s.paused=True
        rows=sorted(s.players.values(),key=lambda p:(p.score,p.correct),reverse=True)
        if not rows: return f"[c03]{s.game.upper()} COMPLETE\n[c01]No scores yet."
        return f"[c03]{s.game.upper()} COMPLETE\n[c01]Final leaderboard\n" + "\n".join(f"{i}. {p.nickname} — {p.score}" for i,p in enumerate(rows[:10],1))

    def answer(self,room,uid,username,nickname,text):
        s=self.sessions.get(room)
        if not s or s.paused: return False,""
        p=s.players.setdefault(uid,Player(uid,username,nickname)); p.nickname=nickname or p.nickname; p.username=username or p.username; p.attempts+=1
        if self._normalize(text)==self._normalize(s.answer):
            p.correct+=1; p.score+=s.points; response=f"[c10]Correct, {nickname}! +{s.points} points."
            response+="\n"+(self.finish(s) if s.number>=s.limit else self._next(s)); return True,response
        return False,""

    def clue(self,room):
        s=self.sessions.get(room)
        if not s: return "[c08]No active game."
        if not s.answer: return "[c08]No clue available."
        n=max(1,len(s.answer)//3); s.clue_text="".join(ch if i<n else "_" for i,ch in enumerate(s.answer))
        return f"[c12]Clue: {s.clue_text}"

    def repost(self,room):
        s=self.sessions.get(room)
        return "[c08]No active game." if not s else f"[c03]{s.game.upper()} #{s.number}/{s.limit}\n[c01]{s.question}\n[c07]Points: {s.points}"

    def status(self,room):
        s=self.sessions.get(room)
        return "[c08]No active game." if not s else f"[c03]Game: {s.game} | Question: {s.number}/{s.limit} | Paused: {'yes' if s.paused else 'no'} | Players: {len(s.players)}"

    def score_text(self,room,uid):
        s=self.sessions.get(room)
        if not s: return "[c08]No active game."
        p=s.players.get(uid)
        return "[c12]No score yet." if not p else f"[c03]YOUR SCORE\n[c01]{p.nickname}\n[c07]Points: {p.score} | Correct: {p.correct} | Attempts: {p.attempts}"

    def leaderboard_text(self,room):
        s=self.sessions.get(room)
        if not s: return "[c08]No active game."
        rows=sorted(s.players.values(),key=lambda p:(p.score,p.correct),reverse=True)
        return "[c12]No scores yet." if not rows else "[c03]LEADERBOARD\n"+"\n".join(f"{i}. {p.nickname} — {p.score}" for i,p in enumerate(rows,1))
