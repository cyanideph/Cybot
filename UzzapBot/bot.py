"""Pydroid 3 entry point for UzzapBot."""
from __future__ import annotations
import logging,time
from config import BOT_NAME,ADMIN_IDS,ADMIN_USERNAMES,POLL_SECONDS,DEFAULT_POINTS,DEFAULT_LIMIT,validate
from database import Database
from game_engine import GameEngine

logging.basicConfig(level=logging.INFO,format="%(asctime)s | %(levelname)s | %(message)s")
log=logging.getLogger("uzzapbot")

HELP="""[c03]UZZAPBOT GAME CORE 4
Slash commands only.

PLAYER COMMANDS:
/help
/clue
/sirit
/hint
/repost
/status
/score
/leaderboard
/version

ADMIN COMMANDS:
/game start <game> [points] [score_limit]
/game start <game> [points] endless
/game stop
/game pause
/game resume
/game next
/game clue
/game repost
/game reveal
/game status
/game score
/game leaderboard
/activate
/lock
/unlock
/wcbot on
/wcbot off
/wmsg <message>
/challenge <room>
/challenge off
/mirror off

Legacy no-slash commands and !game commands are no longer accepted."""

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

def parse_command(text:str):
    """Parse slash-only commands. Non-slash input is never treated as a command."""
    raw=text.strip()
    if not raw.startswith("/"):
        return None
    parts=raw.split()
    if not parts:
        return None
    command=parts[0][1:].casefold()
    args=parts[1:]

    aliases={
        "sirit":"clue",
        "hint":"clue",
        "rep0st":"repost",
        "versi0n":"version",
    }
    command=aliases.get(command,command)

    if command=="game":
        if not args:
            return ["help"]
        sub=args[0].casefold()
        if sub=="random" and len(args)>1 and args[1].casefold() in {"quiz1","quiz2","quiz3","gta"}:
            return ["start",{"quiz1":"random1","quiz2":"random2","quiz3":"random3","gta":"randomgta"}[args[1].casefold()]]
        if sub=="english" and len(args)>1 and args[1].casefold()=="wordhunt":
            return ["start","wordhunt"]
        if sub=="tagalog" and len(args)>1 and args[1].casefold()=="wordhunt":
            return ["start","summonnight2"]
        if sub=="ph" and len(args)>1 and args[1].casefold()=="on":
            return ["start","filipino"]
        if sub=="game" and len(args)>1 and args[1].casefold()=="off":
            return ["stop"]
        return args

    if command in {"challenge"} and args and args[0].casefold() in {"off","stop"}:
        return ["challenge_off"]
    if command=="wcbot" and args and args[0].casefold() in {"on","off"}:
        return ["wcbot",args[0].casefold()]
    if command=="wmsg":
        return ["wmsg"," ".join(args)]
    if command in {"challenge","help","clue","repost","status","score","leaderboard","version","activate","lock","unlock","mirror_off"}:
        return [command,*args]
    return [command,*args]

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
                    if not text.startswith("/"):
                        session=games.get(room)
                        cfg=room_settings(room,db)
                        if session and not cfg.get("locked"):
                            profile=db.profile(uid,username) or {}
                            nickname=str(profile.get("nickname") or username)
                            _,response=games.answer(room,uid,username,nickname,text)
                            if response:
                                persist(db,games,room); db.send(room,response)
                                target=cfg.get("challenge_room")
                                if target and target != room: db.send(target,response)
                        continue

                    args=parse_command(text)
                    if not args: continue
                    admin=is_admin(msg)
                    sub=args[0].casefold()
                    player_commands={"help","clue","repost","status","score","leaderboard","version"}
                    admin_commands={"start","stop","pause","resume","next","reveal","activate","lock","unlock","wcbot","wmsg","challenge","challenge_off","mirror_off"}
                    log.info('COMMAND room="%s" sender="%s" body=%r admin=%s',room,username,text,admin)

                    if sub not in player_commands and sub not in admin_commands:
                        db.send(room,"[c08]Unknown command. Use /help")
                        continue
                    if sub in admin_commands and not admin:
                        db.send(room,"[c08]Admin-only command.")
                        continue

                    if sub=="help": db.send(room,HELP)
                    elif sub=="version": db.send(room,"[c03]UzzapBot — Game Core 4 compatibility layer on the modern UzzapBot architecture.")
                    elif sub=="activate":
                        cfg=room_settings(room,db); cfg["activated"]=True; cfg["locked"]=False; save_room_settings(db,room)
                        db.send(room,"[c03]UzzapBot ACTIVATED in this room.")
                    elif sub=="lock":
                        cfg=room_settings(room,db); cfg["locked"]=True; save_room_settings(db,room)
                        s=games.get(room)
                        if s: s.paused=True; persist(db,games,room)
                        db.send(room,"[c12]Systems LOCK!!! Game input is locked in this room.")
                    elif sub=="unlock":
                        cfg=room_settings(room,db); cfg["locked"]=False; save_room_settings(db,room)
                        s=games.get(room)
                        if s: s.paused=False; persist(db,games,room)
                        db.send(room,"[c03]Systems UNLOCK!!! Game input is enabled in this room.")
                    elif sub=="wcbot":
                        cfg=room_settings(room,db); cfg["wcbot"]=(len(args)>1 and args[1].casefold()=="on"); save_room_settings(db,room)
                        db.send(room,"[c03]Welcome bot " + ("ON." if cfg["wcbot"] else "OFF."))
                    elif sub=="wmsg":
                        cfg=room_settings(room,db); message=" ".join(args[1:]).strip()
                        if not message: db.send(room,"[c08]Usage: /wmsg <message>")
                        else: cfg["welcome_message"]=message; save_room_settings(db,room); db.send(room,"[c03]Welcome message updated.")
                    elif sub=="challenge":
                        cfg=room_settings(room,db); target=" ".join(args[1:]).strip()
                        if not target: db.send(room,"[c08]Usage: /challenge <room>")
                        else: cfg["challenge_room"]=target; save_room_settings(db,room); db.send(room,f"[c03]Challenge room set to: {target}")
                    elif sub=="challenge_off":
                        room_settings(room,db)["challenge_room"]=""; save_room_settings(db,room); db.send(room,"[c08]Challenge room disabled.")
                    elif sub=="mirror_off":
                        room_settings(room,db)["challenge_room"]=""; save_room_settings(db,room); db.send(room,"[c08]Mirror/challenge posting disabled.")
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
                        else: s.paused=True; persist(db,games,room); db.send(room,"[c12]Game paused.")
                    elif sub=="resume":
                        s=games.get(room)
                        if not s: db.send(room,"[c08]No active game.")
                        else: s.paused=False; persist(db,games,room); db.send(room,"[c03]Game resumed.\n"+games.repost(room))
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
                            db.send(room,f"[c0c]The Correct Answer is: [c03]{s.answer}")
                            db.send(room,games.next_question(s)); persist(db,games,room)
                    elif sub=="status": db.send(room,games.status(room))
                    elif sub=="score": db.send(room,games.score_text(room,uid))
                    elif sub=="leaderboard": db.send(room,games.leaderboard_text(room))
                except Exception as exc:
                    log.exception('COMMAND ERROR room="%s" sender="%s"',room,username)
                    try: db.send(room,f"[c08]Game error: {exc}")
                    except Exception: log.exception('FAILED TO SEND GAME ERROR room="%s"',room)
            time.sleep(POLL_SECONDS)
        except KeyboardInterrupt:
            log.info("Bot stopped by user"); return
        except Exception:
            log.exception("Bot loop error; reconnecting"); time.sleep(max(POLL_SECONDS,2.0))

if __name__=="__main__": main()
