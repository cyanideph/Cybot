"""Pydroid 3 entry point for UzzapBot."""
from __future__ import annotations
import logging,time
from config import BOT_NAME,ADMIN_IDS,ADMIN_USERNAMES,POLL_SECONDS,DEFAULT_POINTS,DEFAULT_LIMIT,validate
from database import Database
from game_engine import GameEngine

logging.basicConfig(level=logging.INFO,format="%(asctime)s | %(levelname)s | %(message)s")
log=logging.getLogger("uzzapbot")

HELP="""[c04]╔══════════════════════════════╗
[c14]        UZZAPBOT GAME CORE 4
[c04]╚══════════════════════════════╝
[c09]One official command per action. Slash commands only.

[c02]━━ PLAYER COMMANDS ━━
[c16]/HELP[c09] — Show this help
[c16]/CLUE[c09] — Get a clue
[c16]/REPOST[c09] — Repost the current question
[c16]/STATUS[c09] — Show game status
[c16]/SCORE[c09] — Show your score
[c16]/LEADERBOARD[c09] — Show leaderboard
[c16]/VERSION[c09] — Show bot version

[c14]━━ GAME COMMANDS ━━
[c06]/TT ON[c09] — Text Twist
[c06]/MATH ON[c09] — Math
[c06]/TRIVIA ON[c09] — Trivia
[c06]/ANIME ON[c09] — Anime
[c06]/LOGIC ON[c09] — Logic
[c06]/ALGEBRA ON[c09] — Algebra
[c06]/PH ON[c09] — Philippine game
[c06]/RANDOM QUIZ1[c09] — Random quiz 1
[c06]/RANDOM QUIZ2[c09] — Random quiz 2
[c06]/RANDOM QUIZ3[c09] — Random quiz 3
[c06]/RANDOM GTA[c09] — Random GTA
[c06]/GTA OPM[c09] — OPM GTA
[c06]/GTA FOREIGN[c09] — Foreign GTA
[c06]/ENGLISH WORDHUNT[c09] — English Wordhunt
[c06]/TAGALOG WORDHUNT[c09] — Tagalog Wordhunt

[c03]━━ ADMIN COMMANDS ━━
[c16]/STOP[c09] — Stop the current game
[c16]/PAUSE[c09] — Pause the current game
[c16]/RESUME[c09] — Resume the current game
[c16]/NEXT[c09] — Next question
[c16]/REVEAL[c09] — Reveal the answer
[c16]/ACTIVATE[c09] — Activate room
[c16]/LOCK[c09] — Lock game input
[c16]/UNLOCK[c09] — Unlock game input
[c16]/WCBOT ON[c09] — Enable welcome bot
[c16]/WCBOT OFF[c09] — Disable welcome bot
[c16]/WMSG <message>[c09] — Set welcome message
[c16]/CHALLENGE <room>[c09] — Set challenge room
[c16]/CHALLENGE OFF[c09] — Disable challenge/mirror

[c09]Game commands use the default points and score limit.
[c09]Players are registered automatically when they answer.
[c14]GAME CORE 4.5[c09] — UzzapBot compatibility edition."""

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
    """Parse the single official command for each UzzapBot action."""
    raw=text.strip()
    if not raw.startswith("/"):
        return None
    parts=raw.split()
    if not parts:
        return None

    command=parts[0][1:].casefold()
    args=parts[1:]

    # Exactly one official command per game.
    game_commands={
        "tt":"twist",
        "math":"math",
        "trivia":"trivia",
        "anime":"anime",
        "logic":"logic",
        "algebra":"algebra",
        "ph":"filipino",
        "random_quiz1":"random1",
        "random_quiz2":"random2",
        "random_quiz3":"random3",
        "random_gta":"randomgta",
        "gta_opm":"gtaopm",
        "gta_foreign":"gtaforeign",
        "english_wordhunt":"wordhunt",
        "tagalog_wordhunt":"summonnight2",
    }
    if command in game_commands:
        if not args or args[0].casefold() != "on":
            return ["invalid_game_command", command]
        if len(args) != 1:
            return ["invalid_game_command", command]
        return ["start", game_commands[command]]

    # Single official player/admin commands.
    simple_commands={
        "help","clue","repost","status","score","leaderboard","version",
        "stop","pause","resume","next","reveal","activate","lock","unlock"
    }
    if command in simple_commands:
        if args:
            return ["invalid_command", command]
        return [command]

    if command=="wcbot":
        if len(args)!=1 or args[0].casefold() not in {"on","off"}:
            return ["invalid_command","wcbot"]
        return ["wcbot",args[0].casefold()]

    if command=="wmsg":
        message=" ".join(args).strip()
        return ["wmsg",message]

    if command=="challenge":
        if len(args)==1 and args[0].casefold()=="off":
            return ["challenge_off"]
        target=" ".join(args).strip()
        if not target:
            return ["invalid_command","challenge"]
        return ["challenge",target]

    return ["unknown",command]

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
                    admin_commands={"start","stop","pause","resume","next","reveal","activate","lock","unlock","wcbot","wmsg","challenge","challenge_off"}
                    log.info('COMMAND room="%s" sender="%s" body=%r admin=%s',room,username,text,admin)

                    if sub=="unknown" or sub=="invalid_command" or sub=="invalid_game_command":
                        db.send(room,"[c08]Invalid command. Use /HELP")
                        continue

                    if sub not in player_commands and sub not in admin_commands:
                        db.send(room,"[c08]Unknown command. Use /HELP")
                        continue
                    if sub in admin_commands and not admin:
                        db.send(room,"[c08]Admin-only command.")
                        continue

                    if sub=="help": db.send(room,HELP)
                    elif sub=="version": db.send(room,"[c03]UzzapBot — Game Core 4.")
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
                        game=args[1]
                        games.start(room,game,DEFAULT_POINTS,DEFAULT_LIMIT,False)
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
