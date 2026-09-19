"""Pydroid 3 entry point for UzzapBot."""
from __future__ import annotations
import logging,time
from config import BOT_NAME,ADMIN_IDS,POLL_SECONDS,DEFAULT_POINTS,DEFAULT_LIMIT,validate
from database import Database
from game_engine import GameEngine

logging.basicConfig(level=logging.INFO,format="%(asctime)s | %(levelname)s | %(message)s")
log=logging.getLogger("uzzapbot")

HELP="""[c04]╔══════════════════════════════╗
[c14]          UZZAPBOT
[c04]╚══════════════════════════════╝
[c09]One official command per action. No aliases.

[c02]━━ PLAYER COMMANDS ━━
[c16]/HELP[c09] — Show this help
[c16]/JOIN[c09] — Join the active game before answering
[c16]/LEAVE[c09] — Leave the current game
[c16]/PLAYERS[c09] — Show players who joined the game
[c16]/CLUE[c09] — Get a clue
[c16]/REPOST[c09] — Repost the current question
[c16]/STATUS[c09] — Show current game status
[c16]/SCORE[c09] — Show your score
[c16]/LEADERBOARD[c09] — Show leaderboard
[c16]/VERSION[c09] — Show bot version

[c14]━━ PLAYER GAME COMMANDS ━━
[c06]/TT ON[c09] — Start Text Twist
[c06]/MATH ON[c09] — Start Math
[c06]/TRIVIA ON[c09] — Start Trivia
[c06]/ANIME ON[c09] — Start Anime
[c06]/LOGIC ON[c09] — Start Logic
[c06]/ALGEBRA ON[c09] — Start Algebra
[c06]/PH ON[c09] — Start Philippine game
[c06]/RANDOM QUIZ1[c09] — Start Random Quiz 1
[c06]/RANDOM QUIZ2[c09] — Start Random Quiz 2
[c06]/RANDOM QUIZ3[c09] — Start Random Quiz 3
[c06]/RANDOM GTA[c09] — Start Random GTA
[c06]/GTA OPM[c09] — Start OPM GTA
[c06]/GTA FOREIGN[c09] — Start Foreign GTA
[c06]/ENGLISH WORDHUNT[c09] — Start English Wordhunt
[c06]/TAGALOG WORDHUNT[c09] — Start Tagalog Wordhunt

[c03]━━ ADMIN COMMANDS ━━
[c16]/STOP[c09] — Stop current game
[c16]/PAUSE[c09] — Pause current game
[c16]/RESUME[c09] — Resume current game
[c16]/NEXT[c09] — Next question
[c16]/REVEAL[c09] — Reveal answer
[c16]/ACTIVATE[c09] — Activate room
[c16]/LOCK[c09] — Lock game input
[c16]/UNLOCK[c09] — Unlock game input
[c16]/WCBOT ON[c09] — Enable welcome bot
[c16]/WCBOT OFF[c09] — Disable welcome bot
[c16]/WMSG <message>[c09] — Set welcome message
[c16]/CHALLENGE <room>[c09] — Set challenge room
[c16]/CHALLENGE OFF[c09] — Disable challenge/mirror

[c09]🎮 To play, use /JOIN first.
[c09]Only joined players' normal messages are checked as game answers.
[c09]Users who have not joined can chat normally without affecting the game.
[c09]Use /LEAVE to stop playing and /PLAYERS to see who is playing.
[c09]Invalid or old commands are not accepted.
[c14]UzzapBot Game Core 4.5[c09]."""

def is_admin(msg:dict)->bool:
    # Authorization is based only on immutable Supabase Auth user IDs.
    # Usernames are display data and must never grant administrator access.
    sender_id = str(msg.get("sender_id") or "").strip()
    return bool(sender_id and sender_id in ADMIN_IDS)

def persist(db:Database,games:GameEngine,room:str)->None:
    state=games.export_state(room)
    if state: db.save_game_state(state)

ROOM_SETTINGS = {}
ROOM_SETTINGS_LOADED = {}
SETTINGS_TTL_SECONDS = 60.0

def room_settings(room: str, db: Database | None = None) -> dict:
    now = time.time()
    stale = now - ROOM_SETTINGS_LOADED.get(room, 0.0) > SETTINGS_TTL_SECONDS
    if room not in ROOM_SETTINGS or stale:
        ROOM_SETTINGS[room] = db.get_room_settings(room) if db else {"activated":False,"locked":False,"wcbot":False,"welcome_message":"welcome to {room} {nickname}","challenge_room":""}
        ROOM_SETTINGS_LOADED[room] = now
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
    if not command:
        return None
    args=parts[1:]

    game_commands={
        "tt":"twist","math":"math","trivia":"trivia","anime":"anime","logic":"logic","algebra":"algebra","ph":"filipino",
    }
    if command in game_commands:
        if args != ["ON"] and not (len(args)==1 and args[0].casefold()=="on"):
            return ["invalid_game_command", command]
        return ["start", game_commands[command]]

    multi_game_commands={
        ("random","quiz1"):"random1",("random","quiz2"):"random2",("random","quiz3"):"random3",("random","gta"):"randomgta",
        ("gta","opm"):"gtaopm",("gta","foreign"):"gtaforeign",("english","wordhunt"):"wordhunt",("tagalog","wordhunt"):"summonnight2",
    }
    if len(args)==1:
        key=(command,args[0].casefold())
        if key in multi_game_commands:
            return ["start",multi_game_commands[key]]

    simple_commands={"help","clue","repost","status","score","leaderboard","version","join","leave","players","stop","pause","resume","next","reveal","activate","lock","unlock"}
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
        if args and args[0].casefold()=="off":
            if len(args)==1:
                return ["challenge_off"]
            return ["invalid_command","challenge"]
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
                    player_commands={"help","clue","repost","status","score","leaderboard","version","join","leave","players","start"}
                    admin_commands={"stop","pause","resume","next","reveal","activate","lock","unlock","wcbot","wmsg","challenge","challenge_off"}
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
                    elif sub=="version":
                        db.send(room,"[c11]🤖 UzzapBot[c01] [c14]v4.5[c01]\n[c02]🎮 Game Core:[c01] [c14]4.5[c01]\n[c04]🕹️ Smart Game Modes[c01]\n[c07]💡 Progressive Clues[c01]\n[c18]🔄 Smart Game Cycles[c01]\n[c06]🏆 Scores & Leaderboards[c01]\n[c03]⚡ Fast Answer Checking[c01]\n[c02]🟢 Status: ONLINE[c01]")
                    elif sub=="join":
                        ok,response=games.join(room,uid,username,username)
                        if ok: persist(db,games,room)
                        db.send(room,response)
                    elif sub=="leave":
                        ok,response=games.leave(room,uid)
                        if ok: persist(db,games,room)
                        db.send(room,response)
                    elif sub=="players":
                        db.send(room,games.players_text(room))
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
                    elif sub=="start":
                        game=args[1]
                        games.start(room,game,DEFAULT_POINTS,DEFAULT_LIMIT,False)
                        persist(db,games,room); db.send(room,games.repost(room))
                        db.send(room,"[c09]New game started\u2014previous players must /JOIN again to play.")
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
                        db.send(room,games.clue(room,uid)); persist(db,games,room)
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
                    try: db.send(room,"[c08]Something went wrong while processing that command. Please try again.")
                    except Exception: log.exception('FAILED TO SEND SAFE GAME ERROR room="%s"',room)
            time.sleep(POLL_SECONDS)
        except KeyboardInterrupt:
            log.info("Bot stopped by user"); return
        except Exception:
            log.exception("Bot loop error; reconnecting"); time.sleep(max(POLL_SECONDS,2.0))

if __name__=="__main__": main()
