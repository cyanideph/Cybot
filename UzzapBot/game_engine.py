"""Modern Pydroid-safe reconstruction of the legacy UzZAP Game Core 4 rules."""
from __future__ import annotations
import random, re, unicodedata
from collections import Counter
from difflib import SequenceMatcher
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
    clues_used: int = 0

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
    clue_level: int = 0
    number: int = 0
    players: dict[str, Player] = field(default_factory=dict)
    used_questions: set[str] = field(default_factory=set)
    mode: str = ""
    endless: bool = False
    current_game: str = ""
    recent_games: list[str] = field(default_factory=list)
    cycle_number: int = 1
    cycle_games_used: list[str] = field(default_factory=list)
    reply_history: dict[str, list[str]] = field(default_factory=dict)

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
        value="".join(ch for ch in unicodedata.normalize("NFKD",value) if not unicodedata.combining(ch))
        return "".join(ch for ch in value if ch.isalnum())

    def _answer_matches(self,guess,answer):
        guess_n=self._normalize(guess); answer_n=self._normalize(answer)
        if not guess_n or not answer_n: return False
        if guess_n==answer_n: return True
        if guess_n.isdigit() or answer_n.isdigit(): return False
        if len(answer_n)<5 or len(guess_n)<4: return False
        ratio=SequenceMatcher(None,guess_n,answer_n,autojunk=False).ratio()
        threshold=0.92 if max(len(answer_n),len(guess_n))<=8 else 0.88
        return ratio>=threshold

    def _parse_qa(self,rows):
        """Parse legacy CSV-like question rows as (id, question, answer)."""
        parsed=[]
        for row in rows:
            parts=[p.strip() for p in str(row).split(",",2)]
            if len(parts)!=3:
                continue
            ident,question,answer=parts
            if not ident or not question or not answer:
                continue
            parsed.append((ident,question,answer))
        return parsed

    def _pick_qa(self,rows,used):
        qa=self._parse_qa(rows)
        if not qa: raise ValueError("dataset has no valid question/answer rows")
        fresh=[x for x in qa if f"qa:{x[0]}" not in used and f"q:{self._normalize(x[1])}" not in used]
        if not fresh:
            used.clear()
            fresh=qa
        item=random.choice(fresh)
        used.add(f"qa:{item[0]}")
        used.add(f"q:{self._normalize(item[1])}")
        return item

    def _pick_word(self,rows,used,min_len,max_len=None):
        words=[w.strip() for w in rows if len(w.strip())>=min_len and (max_len is None or len(w.strip())<=max_len)]
        if not words: raise ValueError("word dataset has no usable entries")
        fresh=[w for w in words if f"word:{self._normalize(w)}" not in used]
        if not fresh:
            used.clear()
            fresh=words
        word=random.choice(fresh)
        used.add(f"word:{self._normalize(word)}")
        return word

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

    def _random_pool(self,mode):
        return {"random1":self.RANDOM1,"random2":self.RANDOM2,"random3":self.RANDOM3,
                "randomgta":self.RANDOM_GTA,"math":self.RANDOM_MATH,"algebra":self.RANDOM_ALGEBRA}[mode]

    def _choose_random_game(self,s):
        """Choose a weighted game while completing a full non-repeating cycle."""
        pool=self._random_pool(s.mode)
        counts=Counter(pool)
        all_games=list(counts)

        if set(s.cycle_games_used) >= set(all_games):
            s.cycle_number=max(1,s.cycle_number)+1
            s.cycle_games_used=[]

        used=set(s.cycle_games_used)
        candidates=[g for g in all_games if g not in used]
        blocked=set(s.recent_games[-2:])
        non_blocked=[g for g in candidates if g not in blocked]
        if non_blocked:
            candidates=non_blocked

        chosen=random.choices(candidates,weights=[counts[g] for g in candidates],k=1)[0]
        s.cycle_games_used.append(chosen)
        s.recent_games.append(chosen)
        s.recent_games=s.recent_games[-3:]
        return chosen

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
        s.current_game=game; s.clue_text=""; s.clue_level=0
        if game in {"add","minus","multiply","add1","minus1","multiply1"}:
            for _ in range(50):
                if game in {"add","minus","add1","minus1"}:
                    a,b=random.randint(0,1000),random.randint(0,1000)
                else:
                    a,b=random.randint(1,100 if game=="multiply" else 10),random.randint(1,10 if game=="multiply" else 100)
                if game in {"add","add1"}: result,op=a+b,"+"
                elif game in {"minus","minus1"}: result,op=a-b,"-"
                else: result,op=a*b,"x"
                question=f"MATH: {a} {op} {b} = ?" if game in {"add","minus","multiply"} else f"MATH: {a} {op} ({b}) = ?"
                key=f"generated:{self._normalize(question)}"
                if key not in s.used_questions:
                    s.used_questions.add(key)
                    s.question=question; s.answer=str(result); return
            s.question=question; s.answer=str(result); return
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
        game=self._choose_random_game(s) if s.mode in {"random1","random2","random3","randomgta","math","algebra"} else s.mode
        self._build_question(s,game); return self.repost(s.room)

    def next_question(self,s): return "[c08]No active game." if not s else self._next(s)

    def _winner(self,s,p): return not s.endless and p.score>=s.limit

    def finish(self,s,winner=None):
        s.paused=True
        if winner:
            title=self._reply(s,"win",self.WIN_REPLIES)
            return f"{title}\n[c01]Congratulations, {winner.nickname}![c01]\n[c07]⭐ FINAL SCORE: {winner.score}"
        rows=sorted(s.players.values(),key=lambda p:(p.score,p.correct),reverse=True)
        if not rows: return f"[c03]{s.mode.upper()} COMPLETE\n[c01]No scores yet."
        return f"[c03]{s.mode.upper()} COMPLETE\n[c01]Final leaderboard\n"+"\n".join(f"{i}. {p.nickname} — {p.score}" for i,p in enumerate(rows[:10],1))

    CORRECT_REPLIES = (
        "[c02]🎉 CORRECT, {name}! [c07]+{points} POINTS[c01]",
        "[c02]🔥 Nice one, {name}! [c07]+{points} points[c01]",
        "[c02]👏 Excellent answer, {name}! [c07]+{points}[c01]",
        "[c02]⚡ Fast one, {name}! [c07]+{points} points[c01]",
        "[c02]💚 You got it, {name}! [c07]+{points}[c01]",
        "[c14]🏆 Great answer, {name}! [c07]+{points}[c01]",
        "[c02]🎯 Bullseye, {name}! [c07]+{points}[c01]",
        "[c02]🚀 Nailed it, {name}! [c07]+{points} points[c01]",
        "[c02]✨ That's right, {name}! [c07]+{points}[c01]",
        "[c14]💥 Perfect answer, {name}! [c07]+{points}[c01]",
        "[c02]😎 Smooth one, {name}! [c07]+{points}[c01]",
        "[c02]🥳 Another point for you, {name}! [c07]+{points}[c01]",
        "[c14]👑 Well played, {name}! [c07]+{points}[c01]",
        "[c02]💯 You got that one! [c07]+{points}[c01]",
        "[c02]🎊 Correct! Keep it going, {name}! [c07]+{points}[c01]",
    )
    WRONG_REPLIES = (
        "[c08]❌ Not quite, {name}.[c01] Keep trying!",
        "[c12]🤔 Close, {name}.[c01] Give it another shot.",
        "[c12]💪 Keep going, {name}![c01] You can get the next one.",
        "[c04]🧠 Think again, {name}.[c01]",
        "[c04]🔎 Almost there, {name}.[c01] Try another answer.",
        "[c12]😅 Nope, not that one.[c01] Keep guessing!",
        "[c04]🎯 Good attempt, {name}.[c01] Try again.",
        "[c12]💡 You're getting warmer, {name}.[c01]",
        "[c04]👀 Take another look, {name}.[c01]",
        "[c12]🙃 Not this time, {name}.[c01]",
        "[c12]🔥 Keep the guesses coming, {name}![c01]",
        "[c04]🧐 Try another answer, {name}.[c01]",
    )
    CLUE_PREFIXES = (
        "[c12]💡 Here's a clue...",
        "[c12]🧩 Need some help?",
        "[c12]🔎 Look closely...",
        "[c12]✨ A little hint for you...",
        "[c12]🧠 Think about this...",
        "[c12]👀 Here's something useful...",
        "[c12]🎯 Your next clue...",
        "[c12]📖 Maybe this helps...",
        "[c12]💭 Consider this...",
        "[c12]🔐 Unlocking another clue...",
    )
    NEW_GAME_REPLIES = (
        "[c03]🎮 NEW ROUND[c01]",
        "[c03]🎮 NEXT CHALLENGE[c01]",
        "[c03]⚡ HERE WE GO[c01]",
        "[c03]🔥 NEXT QUESTION[c01]",
        "[c03]🧠 TIME TO THINK[c01]",
        "[c03]🎯 YOUR NEXT CHALLENGE[c01]",
    )
    WIN_REPLIES = (
        "[c14]🏆 GAME WINNER 🏆",
        "[c14]🎉 WE HAVE A WINNER! 🎉",
        "[c14]👑 CHAMPION! 👑",
        "[c14]💥 GAME OVER — WINNER! 💥",
        "[c14]🥳 VICTORY! 🥳",
        "[c14]⭐ WHAT A FINISH! ⭐",
    )

    def _personality(self, category, options, **values):
        """Pick a reply while avoiding the category's recent replies."""
        room=values.pop("_room", "")
        s=self.sessions.get(room)
        if s is None:
            return random.choice(options).format(**values)
        recent=s.reply_history.setdefault(category, [])
        available=[option for option in options if option not in recent]
        if not available:
            recent.clear()
            available=list(options)
        template=random.choice(available)
        recent.append(template)
        del recent[:-4]
        return template.format(**values)

    def _reply(self, s, category, options, **values):
        return self._personality(category, options, _room=s.room, **values)

    def answer(self,room,uid,username,nickname,text):
        s=self.sessions.get(room)
        if not s or s.paused: return False,""
        key=uid or username
        p=s.players.setdefault(key,Player(uid,username,nickname))
        p.nickname=nickname or p.nickname; p.username=username or p.username; p.attempts+=1
        if self._answer_matches(text,s.answer):
            p.correct+=1; p.score+=s.points
            response=self._reply(s,"correct",self.CORRECT_REPLIES,name=p.nickname,points=s.points)
            response+="\n"+(self.finish(s,p) if self._winner(s,p) else self._next(s))
            return True,response
        response=self._reply(s,"wrong",self.WRONG_REPLIES,name=p.nickname)
        return False,response

    def clue(self,room,uid=None):
        s=self.sessions.get(room)
        if not s: return "[c08]No active game."
        if not s.answer: return "[c08]No clue available."
        if s.clue_level >= 3:
            return "[c12]Maximum clues reached. Try your answer!"

        # Progressive clues reveal 1/3, 1/2, then 2/3 of the answer.
        s.clue_level += 1
        compact_len=len(re.sub(r"\s+","",s.answer))
        reveal_ratio={1:1/3,2:1/2,3:2/3}[s.clue_level]
        reveal=max(1,int(compact_len*reveal_ratio))
        seen=0; out=[]
        for ch in s.answer:
            if ch.isspace() or not ch.isalnum():
                out.append(ch)
            elif seen<reveal:
                out.append(ch); seen+=1
            else:
                out.append("_")
        s.clue_text="".join(out)
        if uid:
            p=s.players.get(uid)
            if p:
                p.clues_used += 1
        prefix=self._reply(s,"clue",self.CLUE_PREFIXES)
        return f"{prefix} [c01]{s.clue_level}/3: {s.clue_text}"

    def repost(self,room):
        s=self.sessions.get(room)
        if not s: return "[c08]No active game."
        target="ENDLESS" if s.endless else str(s.limit)
        header=self._reply(s,"new_game",self.NEW_GAME_REPLIES)
        return f"{header}\n[c14]{s.mode.upper()} · Q#{s.number}[c01]\n[c01]{s.question}\n[c07]⭐ {s.points} POINTS[c01]"+(f"\n[c12]Clue: {s.clue_text}" if s.clue_text else "")

    def status(self,room):
        s=self.sessions.get(room)
        if not s: return "[c08]No active game."
        target="ENDLESS" if s.endless else str(s.limit)
        cycle_total=len(set(self._random_pool(s.mode))) if s.mode in {"random1","random2","random3","randomgta","math","algebra"} else 0
        cycle_text=f" | Cycle: {s.cycle_number} ({len(set(s.cycle_games_used))}/{cycle_total})" if cycle_total else ""
        return f"[c03]Mode: {s.mode} | Current: {s.current_game} | Points: {s.points} | Score limit: {target} | Paused: {'yes' if s.paused else 'no'} | Players: {len(s.players)}{cycle_text}"

    def score_text(self,room,uid):
        s=self.sessions.get(room)
        if not s: return "[c08]No active game."
        p=s.players.get(uid)
        return "[c12]No score yet." if not p else f"[c03]YOUR SCORE\n[c01]{p.nickname}\n[c07]Points: {p.score} | Correct: {p.correct} | Attempts: {p.attempts} | Clues: {p.clues_used}"

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
                "used_questions":list(s.used_questions), "clue_level":s.clue_level, "recent_games":list(s.recent_games),
                "cycle_number":s.cycle_number, "cycle_games_used":list(s.cycle_games_used),
                "reply_history":{k:list(v) for k,v in s.reply_history.items()},
                "players":[{"user_id":p.user_id,"username":p.username,"nickname":p.nickname,"score":p.score,"correct":p.correct,"attempts":p.attempts,"clues_used":p.clues_used} for p in s.players.values()]}

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
                  str(state.get("clue_text") or ""),int(state.get("clue_level") or 0),int(state.get("number") or 0),
                  mode=mode,endless=bool(state.get("endless")),
                  current_game=str(state.get("current_game") or game or mode), recent_games=list(state.get("recent_games") or []),
                  cycle_number=max(1,int(state.get("cycle_number") or 1)),
                  cycle_games_used=list(state.get("cycle_games_used") or []),
                  reply_history={str(k):list(v or []) for k,v in (state.get("reply_history") or {}).items() if isinstance(v,list)})
        s.used_questions=set(state.get("used_questions") or [])

        for p in state.get("players") or []:
            if not isinstance(p, dict):
                continue
            player=Player(str(p.get("user_id") or ""),str(p.get("username") or ""),str(p.get("nickname") or ""),
                          int(p.get("score") or 0),int(p.get("correct") or 0),int(p.get("attempts") or 0),int(p.get("clues_used") or 0))
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
