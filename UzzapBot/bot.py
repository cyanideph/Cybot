"""Pydroid 3 entry point for UzzapBot."""
from __future__ import annotations
import logging,time
from config import BOT_NAME,ADMIN_IDS,ADMIN_USERNAMES,POLL_SECONDS,DEFAULT_POINTS,DEFAULT_LIMIT,validate
from database import Database
from game_engine import GameEngine

logging.basicConfig(level=logging.INFO,format="%(asctime)s | %(levelname)s | %(message)s")
log=logging.getLogger("uzzapbot")

HELP="""[c03]UZZAPBOT GAME CORE 4 COMPATIBILITY
[c01]!game start <game> [points] [score_limit]
!game start <game> [points] endless
Games:
add minus multiply add1 minus1 multiply1
algebra1 algebra2 algebra3
trivia anime gtaforeign gtaopm logic
wordhunt summonnight summonnight2 filipino love twist
random1 random2 random3 randomgta math algebra
Controls:
!game stop
!game pause
!game resume
!game next
!game clue
!game repost
!game reveal
!game status
!game score
!game leaderboard

Legacy commands (original Game Core 4 style):
RANDOM QUIZ1
RANDOM QUIZ2
RANDOM QUIZ3
RANDOM GTA
MATH ON
TT ON
TRIVIA ON
ENGLISH WORDHUNT
TAGALOG WORDHUNT
PH ON
GAME ON
GAME OFF
CLUE / SIRIT / HINT
REPOST / REP0ST
STATUS / SCORE / LEADERBOARD

These are compatibility aliases; the modern GameEngine and persistence remain authoritative."""

def is_admin(msg:dict)->bool:
    return str(msg.get("sender_id") or "") in ADMIN_IDS or str(msg.get("sender") or "").casefold() in ADMIN_USERNAMES

def persist(db:Database,games:GameEngine,room:str)->None:
    state=games.export_state(room)
    if state: db.save_game_state(state)

ROOM_SETTINGS = {}
def room_settings(room: str, db: Database | None = None) -> dict:
    if room not in ROOM_SETTINGS:
        ROOM_SETTINGS[room] = db.get_room_settings(room) if db else {"activated":False,"locked":False,"wcbot":False,"welcome_message":"welcome to {room} {nickname}","challenge_room":""}
    return ROOM_SETTINGS[room]

def save_room_settings(db: Database, room: str) -> None:
    db.save_room_settings(room, ROOM_SETTINGS[room])

def parse_legacy_command(text:str):
    """Translate legacy Game Core 4 commands into modern GameEngine actions."""
    key=" ".join(text.strip().casefold().split())
    starts={
        "random quiz1":"random1",
        "random quiz2":"random2",
        "random quiz3":"random3",
        "random gta":"randomgta",
        "math on":"math",
        "math":"math",
        "tt on":"twist",
        "tt":"twist",
        "texttwist":"twist",
        "english wordhunt":"wordhunt",
        "wordhunt":"wordhunt",
        "tagalog wordhunt":"summonnight2",
        "tagaloghunt":"summonnight2",
        "ph on":"filipino",
        "trivia on":"trivia",
        "anime on":"anime",
        "logic on":"logic",
        "gta opm":"gtaopm",
        "gta foreign":"gtaforeign",
        "algebra on":"algebra",
        "game on":"random1",
        "random on":"random1",
    }
    if key in starts: return ["start",starts[key]]
    if key in {"game off","game stop","stop game"}: return ["stop"]
    if key == "activate": return ["activate"]
    if key == "challenge off": return ["challenge_off"]
    if key == "mirror off": return ["mirror_off"]
    if key == "lock": return ["lock"]
    if key == "unlock": return ["unlock"]
    if key in {"version","versi0n"}: return ["version"]
    if key.startswith("/challenge "): return ["challenge", text.strip()[11:].strip()]
    if key in {"/challenge off","/challenge stop"}: return ["challenge_off"]
    if key.startswith("/wmsg "): return ["wmsg", text.strip()[6:].strip()]
    if key in {"/wcbot on","/wcbot off","wcbot on","wcbot off"}: return ["wcbot", key.rsplit(" ",1)[-1]]
    if key in {"help","game help"}: return ["help"]
    if key in {"clue","/clue","sirit","/sirit","hint","/hint"}: return ["clue"]
    if key in {"repost","/repost","rep0st"}: return ["repost"]
    if key in {"status","/status"}: return ["status"]
    if key in {"score","/score"}: return ["score"]
    if key in {"leaderboard","/leaderboard"}: return ["leaderboard"]
    if key in {"reveal","/reveal"}: return ["reveal"]
    if key in {"next","/next"}: return ["next"]
    if key in {"pause","/pause"}: return ["pause"]
    if key in {"resume","/resume"}: return ["resume"]
    return None


def parse_game_command(text:str):
    parts=text.split()
    if len(parts)>=3 and parts[1].casefold()=="random" and parts[2].casefold() in {"quiz1","quiz2","quiz3","gta"}:
        return ["start",{"quiz1":"random1","quiz2":"random2","quiz3":"random3","gta":"randomgta"}[parts[2].casefold()]]
    if len(parts)>=3 and parts[1].casefold()=="english" and parts[2].casefold()=="wordhunt":
        return ["start","wordhunt"]
    if len(parts)>=3 and parts[1].casefold()=="tagalog" and parts[2].casefold()=="wordhunt":
        return ["start","summonnight2"]
    if len(parts)>=2 and parts[1].casefold()=="ph" and len(parts)>=3 and parts[2].casefold()=="on":
        return ["start","filipino"]
    if len(parts)>=2 and parts[1].casefold()=="game" and len(parts)>=3 and parts[2].casefold()=="off":
        return ["stop"]
    return parts[1:]

def main()->None:
    validate()
    db,games=Database(),GameEngine()
    restored=games.restore_all(db.load_game_state())
    seen_participants=set()
    db.poll_new_participants(seen_participants)
    log.info("Restored %d persistent game session(s)",restored)
    log.info("%s connected; polling every %.1fs",BOT_NAME,POLL_SECONDS)
    while True:
        try:
            for participant in db.poll_new_participants(seen_participants):
                room=str(participant.get("room_name") or "").strip()
                username=str(participant.get("username") or "").strip()
                if room and username:
                    cfg=room_settings(room, db)
                    if cfg.get("wcbot"):
                        profile=db.profile(None, username) or {}
                        nickname=str(profile.get("nickname") or username)
                        body=str(cfg.get("welcome_message") or "welcome to {room} {nickname}")
                        body=body.replace("{room}",room).replace("{nickname}",nickname).replace("{username}",username)
                        db.send(room,body)
            for msg in db.poll_messages():
                room=str(msg.get("room_name") or "").strip()
                text=str(msg.get("body") or "").strip()
                username=str(msg.get("sender") or "").strip()
                uid=str(msg.get("sender_id") or "")
                if not room or not text: continue
                try:
                    is_modern=text.casefold().startswith("!game")
                    legacy=parse_legacy_command(text) if not is_modern else None
                    if is_modern or legacy:
                        admin=is_admin(msg)
                        log.info('COMMAND room="%s" sender="%s" body=%r admin=%s legacy=%s',room,username,text,admin,bool(legacy))
                        args=legacy if legacy else parse_game_command(text)
                        sub=args[0].casefold() if args else "help"
                        public_legacy={"help","clue","repost","score","status","leaderboard"}
                        if not legacy and not admin:
                            db.send(room,"[c08]Game controls are admin-only during testing."); continue
                        if legacy and sub not in public_legacy and not admin:
                            db.send(room,"[c08]Game controls are admin-only during testing."); continue
                        if sub=="help": db.send(room,HELP)
                        elif sub=="version": db.send(room,"[c03]UzzapBot — Game Core 4 compatibility layer on the modern UzzapBot architecture.")
                        elif sub=="activate":
                            cfg=room_settings(room,db); cfg["activated"]=True; cfg["locked"]=False; save_room_settings(db,room)
                            db.send(room,"[c10]UzzapBot ACTIVATED in this room.")
                        elif sub=="lock":
                            cfg=room_settings(room,db); cfg["locked"]=True; save_room_settings(db,room)
                            s=games.get(room)
                            if s: s.paused=True; persist(db,games,room)
                            db.send(room,"[c12]Systems LOCK!!! Game input is locked in this room.")
                        elif sub=="unlock":
                            cfg=room_settings(room,db); cfg["locked"]=False; save_room_settings(db,room)
                            s=games.get(room)
                            if s: s.paused=False; persist(db,games,room)
                            db.send(room,"[c10]Systems UNLOCK!!! Game input is enabled in this room.")
                        elif sub=="wcbot":
                            cfg=room_settings(room,db); cfg["wcbot"]=(len(args)>1 and args[1].casefold()=="on"); save_room_settings(db,room)
                            db.send(room,"[c03]Welcome bot " + ("ON." if cfg["wcbot"] else "OFF."))
                        elif sub=="wmsg":
                            cfg=room_settings(room,db); message=" ".join(args[1:]).strip()
                            if not message: db.send(room,"[c08]Usage: /wmsg <message>")
                            else: cfg["welcome_message"]=message; save_room_settings(db,room); db.send(room,"[c10]Welcome message updated.")
                        elif sub=="challenge":
                            cfg=room_settings(room,db); target=" ".join(args[1:]).strip()
                            if not target: db.send(room,"[c08]Usage: /challenge <room>")
                            else: cfg["challenge_room"]=target; save_room_settings(db,room); db.send(room,f"[c10]Challenge room set to: {target}")
                        elif sub=="challenge_off":
                            room_settings(room,db)["challenge_room"]=""; save_room_settings(db,room); db.send(room,"[c08]Challenge room disabled.")
                        elif sub=="mirror_off":
                            room_settings(room)["challenge_room"]=""; db.send(room,"[c08]Mirror/challenge posting disabled.")
                        elif sub=="legacy_noop": db.send(room,"[c08]Legacy command recognized. This feature is handled by the modern room architecture.")
                        elif sub=="legacy_noop": db.send(room,"[c08]Legacy command recognized. This feature is handled by the modern room architecture.")
                        elif sub=="start":
                            game=args[1] if len(args)>1 else "math"
                            points=int(args[2]) if len(args)>2 else DEFAULT_POINTS
                            endless=any(x.casefold()=="endless" for x in args[3:])
                            numeric=[x for x in args[3:] if x.isdigit()]
                            limit=int(numeric[0]) if numeric else DEFAULT_LIMIT
                            games.start(room,game,points,limit,endless)
                            persist(db,games,room); db.send(room,games.repost(room))
                        elif sub=="stop":
                            if games.get(room):
                                games.stop(room); db.delete_game_state(room); db.send(room,"[c08]Game stopped.")
                            else: db.send(room,"[c08]No active game.")
                        elif sub=="pause":
                            s=games.get(room)
                            if not s: db.send(room,"[c08]No active game.")
                            else:
                                s.paused=True; persist(db,games,room); db.send(room,"[c12]Game paused.")
                        elif sub=="resume":
                            s=games.get(room)
                            if not s: db.send(room,"[c08]No active game.")
                            else:
                                s.paused=False; persist(db,games,room); db.send(room,"[c10]Game resumed.\n"+games.repost(room))
                        elif sub=="next":
                            db.send(room,games.next_question(games.get(room))); persist(db,games,room)
                        elif sub=="clue":
                            db.send(room,games.clue(room)); persist(db,games,room)
                        elif sub=="repost":
                            db.send(room,games.repost(room))
                        elif sub=="reveal":
                            s=games.get(room)
                            if not s: db.send(room,"[c08]No active game.")
                            else:
                                db.send(room,f"[c0c]The Correct Answer is: [c10]{s.answer}")
                                db.send(room,games.next_question(s)); persist(db,games,room)
                        elif sub=="status": db.send(room,games.status(room))
                        elif sub=="score": db.send(room,games.score_text(room,uid))
                        elif sub=="leaderboard": db.send(room,games.leaderboard_text(room))
                        else: db.send(room,"[c08]Unknown game command. Use !game help")
                        continue
                    session=games.get(room)
                    cfg=room_settings(room,db)
                    if session and cfg.get("locked"):
                        continue
                    if session and not text.startswith("/"):
                        profile=db.profile(uid,username) or {}
                        nickname=str(profile.get("nickname") or username)
                        _,response=games.answer(room,uid,username,nickname,text)
                        if response:
                            persist(db,games,room); db.send(room,response)
                            target=cfg.get("challenge_room")
                            if target and target != room: db.send(target,response)
                except Exception as exc:
                    log.exception('COMMAND ERROR room="%s" sender="%s"',room,username)
                    try:
                        db.send(room,f"[c08]Game error: {exc}")
                    except Exception:
                        log.exception('FAILED TO SEND GAME ERROR room="%s"',room)
            time.sleep(POLL_SECONDS)
        except KeyboardInterrupt:
            log.info("Bot stopped by user"); return
        except Exception:
            log.exception("Bot loop error; reconnecting"); time.sleep(max(POLL_SECONDS,2.0))

if __name__=="__main__": main()
