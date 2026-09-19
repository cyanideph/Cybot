"""Modern Pydroid-safe reconstruction of the legacy UzZAP Game Core 4 rules."""
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
    mode: str = ""
    endless: bool = False
    current_game: str = ""

    def __post_init__(self):
        if not self.mode: self.mode = self.game
        if not self.current_game: self.current_game = self.game

class GameEngine:
    # Commands are normalized by bot.py. Keep the engine strict so each game has one official command.
    ALIASES = {}
    GAMES = {
        "add","minus","multiply","add1","minus1","multiply1",
        "algebra1","algebra2","algebra3","trivia","anime","gtaforeign",
        "gtaopm","logic","wordhunt","summonnight","summonnight2",
        "filipino","love","twist","random1","random2","random3",
        "randomgta","math","algebra"
    }
    RANDOM1 = ("algebra1","algebra2","algebra3","add","minus","multiply",
               "add1","minus1","multiply1","filipino","filipino","filipino","filipino",
               "love","love","love","love","summonnight","summonnight","summonnight",
               "summonnight","summonnight","summonnight2","summonnight2","summonnight2","summonnight2")
    RANDOM2 = ("algebra1","algebra2","algebra3","add","minus","multiply","add1","minus1","multiply1",
               "filipino","filipino","filipino","love","love","summonnight","summonnight","summonnight",
               "summonnight","summonnight2","summonnight2","summonnight2",
               "trivia","trivia","trivia","trivia","trivia","trivia","trivia",
               "gtaopm","gtaopm","gtaopm","gtaopm","gtaforeign","gtaforeign","gtaforeign","gtaforeign")
    RANDOM3 = RANDOM2 + ("logic","logic","logic","anime","anime","anime")
    RANDOM_GTA = ("gtaforeign","gtaopm")
    RANDOM_MATH = ("add","minus","multiply","add1","minus1","multiply1")
    RANDOM_ALGEBRA = ("algebra1","algebra2","algebra3")

    def __init__(self):
        self.sessions = {}
        self.datasets = {n:self._load(n) for n in (
            "Zgen-info.txt","Zanime-trivia.txt","Zgta-foreign.txt",
            "Zgta-opm.txt","Zlogic.txt","words.txt","salita.txt")}

    def _load(self,name):
        p=Path(DATA_DIR)/name
        return [x.strip() for x in p.read_text(encoding="utf-8",errors="ignore").splitlines() if x.strip()] if p.exists() else []

    def _normalize(self,value):
        value=unicodedata.normalize("NFKC",str(value))
        value=re.sub(r"\[[^\]]+\]","",value).casefold().strip()
        return "".join(ch for ch in value if ch.isalnum())

    def _parse_qa(self,rows):
        out=[]
        for row in rows:
            parts=row.split(",",2)
            if len(parts)==3:
                ident,question,answer=(x.strip() for x in parts)
                if question and answer: out.append((ident,question,answer))
        return out

    def _pick_qa(self,rows,used):
        qa=self._parse_qa(rows)
        if not qa: raise ValueError("dataset has no valid question/answer rows")
        fresh=[x for x in qa if x[0] not in used and self._normalize(x[1]) not in used]
        item=random.choice(fresh or qa)
        used.add(item[0]); used.add(self._normalize(item[1]))
        return item

    def _pick_word(self,rows,used,min_len,max_len=None):
        words=[w.strip() for w in rows if len(w.strip())>=min_len and (max_len is None or len(w.strip())<=max_len)]
        if not words: raise ValueError("word dataset has no usable entries")
        fresh=[w for w in words if self._normalize(w) not in used]
        word=random.choice(fresh or words); used.add(self._normalize(word)); return word

    def _scramble(self,word):
        chars=list(word); original=self._normalize(word)
        if len(chars)<2: return word
        for _ in range(20):
            random.shuffle(chars); candidate="".join(chars)
            if self._normalize(candidate)!=original: return candidate
        return word

    def _random_game(self,mode):
        pool={"random1":self.RANDOM1,"random2":self.RANDOM2,"random3":self.RANDOM3,
              "randomgta":self.RANDOM_GTA,"math":self.RANDOM_MATH,"algebra":self.RANDOM_ALGEBRA}[mode]
        return random.choice(pool)

    def start(self,room,game,points=None,limit=None,endless=False):
        requested=self.ALIASES.get(game.casefold(),game.casefold())
        points=DEFAULT_POINTS if points is None else int(points)
        limit=DEFAULT_LIMIT if limit is None else int(limit)
        if not 1<=points<=1000: raise ValueError("points must be between 1 and 1000")
        if not endless and not 100<=limit<=5000: raise ValueError("score limit must be between 100 and 5000")
        if requested not in self.GAMES: raise ValueError(f"Unknown game: {game}")
        s=Session(room,requested,points,limit,mode=requested,endless=endless)
        self.sessions[room]=s; self._next(s); return s

    def get(self,room): return self.sessions.get(room)
    def stop(self,room): self.sessions.pop(room,None)

    def _build_question(self,s,game):
        s.current_game=game; s.clue_text=""
        if game in {"add","minus","multiply","add1","minus1","multiply1"}:
            if game in {"add","minus","add1","minus1"}: a,b=random.randint(0,1000),random.randint(0,1000)
            else: a,b=random.randint(1,100 if game=="multiply" else 10),random.randint(1,10 if game=="multiply" else 100)
            if game in {"add","add1"}: result,op=a+b,"+"
            elif game in {"minus","minus1"}: result,op=a-b,"-"
            else: result,op=a*b,"x"
            s.question=f"MATH: {a} {op} {b} = ?" if game in {"add","minus","multiply"} else f"MATH: {a} {op} ({b}) = ?"
            s.answer=str(result); return
        if game in {"algebra1","algebra2","algebra3"}:
            a,b=random.randint(0,10),random.randint(1,10)
            xcoef,ycoef=random.randint(1,10),random.randint(1,10)
            if game=="algebra1": result=a*xcoef+b*ycoef; op="+"
            elif game=="algebra2": result=a*xcoef-b*ycoef; op="-"
            else: result=(a*xcoef)*(b*ycoef); op="x"
            s.question=f"If X={xcoef} & Y={ycoef}, solve {a}X {op} {b}Y = ?"; s.answer=str(result); return
        if game=="trivia":
            _,s.question,s.answer=self._pick_qa(self.datasets["Zgen-info.txt"],s.used_questions); return
        if game=="anime":
            _,s.question,s.answer=self._pick_qa(self.datasets["Zanime-trivia.txt"],s.used_questions); return
        if game=="gtaforeign":
            _,title,s.answer=self._pick_qa(self.datasets["Zgta-foreign.txt"],s.used_questions)
            s.question=f"TiTLE: '{title}'\n~> Guess The Artist"; return
        if game=="gtaopm":
            _,title,s.answer=self._pick_qa(self.datasets["Zgta-opm.txt"],s.used_questions)
            s.question=f"TiTLE: '{title}'\n~> Guess The Artist [OPM]"; return
        if game=="logic":
            _,s.question,s.answer=self._pick_qa(self.datasets["Zlogic.txt"],s.used_questions); return
        if game in {"wordhunt","summonnight"}:
            word=self._pick_word(self.datasets["words.txt"],s.used_questions,3,8)
            s.answer=word; s.question=f"ENG WordHunt: {self._scramble(word)}"; return
        if game=="summonnight2":
            word=self._pick_word(self.datasets["salita.txt"],s.used_questions,3,8)
            s.answer=word; s.question=f"TAGALOG WordHunt: {self._scramble(word)}"; return
        if game=="filipino":
            word=self._pick_word(self.datasets["salita.txt"],s.used_questions,3,15)
            s.answer=word; s.question=f"PINoy HENYO: {self._scramble(word)}"; return
        if game in {"love","twist"}:
            word=self._pick_word(self.datasets["words.txt"],s.used_questions,3,17)
            s.answer=word; s.question=f"{'TT=>' if game=='twist' else 'LOVE'}: {self._scramble(word)}"; return
        raise ValueError(f"Unsupported game: {game}")

    def _next(self,s):
        if s.paused: return self.repost(s.room)
        s.number+=1
        game=self._random_game(s.mode) if s.mode in {"random1","random2","random3","randomgta","math","algebra"} else s.mode
        self._build_question(s,game); return self.repost(s.room)

    def next_question(self,s): return "[c08]No active game." if not s else self._next(s)

    def _winner(self,s,p): return not s.endless and p.score>=s.limit

    def finish(self,s,winner=None):
        s.paused=True
        if winner: return f"[c03]{winner.nickname} WINS THE GAME!\n[c03]Score: {winner.score}"
        rows=sorted(s.players.values(),key=lambda p:(p.score,p.correct),reverse=True)
        if not rows: return f"[c03]{s.mode.upper()} COMPLETE\n[c01]No scores yet."
        return f"[c03]{s.mode.upper()} COMPLETE\n[c01]Final leaderboard\n"+"\n".join(f"{i}. {p.nickname} — {p.score}" for i,p in enumerate(rows[:10],1))

    CORRECT_REPLIES = (
        "🎉 Correct, {name}! +{points} points.",
        "🔥 Nice one, {name}! +{points} points.",
        "👏 Good answer, {name}! +{points} points.",
        "⚡ Fast one, {name}! +{points} points.",
        "💚 You got it, {name}! +{points} points.",
        "🏆 Excellent, {name}! +{points} points.",
    )
    CLUE_PREFIXES = (
        "💡 Clue",
        "🧩 Here's a clue",
        "🔎 Try this clue",
        "✨ Clue",
    )

    def _personality(self, options, **values):
        return random.choice(options).format(**values)

    def answer(self,room,uid,username,nickname,text):
        s=self.sessions.get(room)
        if not s or s.paused: return False,""
        key=uid or username
        p=s.players.setdefault(key,Player(uid,username,nickname))
        p.nickname=nickname or p.nickname; p.username=username or p.username; p.attempts+=1
        if self._normalize(text)==self._normalize(s.answer):
            p.correct+=1; p.score+=s.points
            response=f"[c03]{self._personality(self.CORRECT_REPLIES,name=p.nickname,points=s.points)}"
            response+="\n"+(self.finish(s,p) if self._winner(s,p) else self._next(s))
            return True,response
        return False,""

    def clue(self,room):
        s=self.sessions.get(room)
        if not s: return "[c08]No active game."
        if not s.answer: return "[c08]No clue available."
        reveal=max(1,len(re.sub(r"\s+","",s.answer))//3); seen=0; out=[]
        for ch in s.answer:
            if ch.isspace() or not ch.isalnum(): out.append(ch)
            elif seen<reveal: out.append(ch); seen+=1
            else: out.append("_")
        s.clue_text="".join(out); return f"[c12]{random.choice(self.CLUE_PREFIXES)}: {s.clue_text}"

    def repost(self,room):
        s=self.sessions.get(room)
        if not s: return "[c08]No active game."
        target="ENDLESS" if s.endless else str(s.limit)
        return f"[c03]{s.mode.upper()} / {s.current_game.upper()} Q#{s.number} / LIMIT {target}\n[c01]{s.question}\n[c07]Points: {s.points}"+(f"\n[c12]Clue: {s.clue_text}" if s.clue_text else "")

    def status(self,room):
        s=self.sessions.get(room)
        if not s: return "[c08]No active game."
        target="ENDLESS" if s.endless else str(s.limit)
        return f"[c03]Mode: {s.mode} | Current: {s.current_game} | Points: {s.points} | Score limit: {target} | Paused: {'yes' if s.paused else 'no'} | Players: {len(s.players)}"

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

    def export_state(self,room):
        s=self.sessions.get(room)
        if not s: return None
        return {"room":s.room,"game":s.game,"mode":s.mode,"current_game":s.current_game,
                "points":s.points,"limit":s.limit,"endless":s.endless,"paused":s.paused,
                "question":s.question,"answer":s.answer,"clue_text":s.clue_text,"number":s.number,
                "used_questions":list(s.used_questions),
                "players":[{"user_id":p.user_id,"username":p.username,"nickname":p.nickname,"score":p.score,"correct":p.correct,"attempts":p.attempts} for p in s.players.values()]}

    def restore_state(self,state):
        if not isinstance(state, dict):
            return None

        # Support the current field and possible legacy naming.
        room = state.get("room") or state.get("room_id")
        if not room:
            print("Skipping persisted game state without a room identifier.")
            return None

        mode = str(state.get("mode") or state.get("game") or "math")
        game = str(state.get("game") or mode)

        s=Session(str(room),game,int(state.get("points") or DEFAULT_POINTS),
                  int(state.get("limit") or DEFAULT_LIMIT),bool(state.get("paused")),
                  str(state.get("question") or ""),str(state.get("answer") or ""),
                  str(state.get("clue_text") or ""),int(state.get("number") or 0),
                  mode=mode,endless=bool(state.get("endless")),
                  current_game=str(state.get("current_game") or game or mode))
        s.used_questions=set(state.get("used_questions") or [])

        for p in state.get("players") or []:
            if not isinstance(p, dict):
                continue
            player=Player(str(p.get("user_id") or ""),str(p.get("username") or ""),str(p.get("nickname") or ""),
                          int(p.get("score") or 0),int(p.get("correct") or 0),int(p.get("attempts") or 0))
            s.players[player.user_id or player.username]=player

        self.sessions[s.room]=s
        return s

    def restore_all(self,states):
        restored = 0
        for state in states or []:
            try:
                if self.restore_state(state) is not None:
                    restored += 1
            except (TypeError, ValueError, KeyError) as exc:
                print(f"Skipping invalid persisted game state: {exc}")
        return restored
