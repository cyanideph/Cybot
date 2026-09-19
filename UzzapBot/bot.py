"""Pydroid 3 entry point for UzzapBot."""
from __future__ import annotations
import logging,time
from config import BOT_NAME,ADMIN_IDS,POLL_SECONDS,DEFAULT_POINTS,DEFAULT_LIMIT,validate
from database import Database
from game_engine import GameEngine

logging.basicConfig(level=logging.INFO,format="%(asctime)s | %(levelname)s | %(message)s")
log=logging.getLogger("uzzapbot")

HELP="""[c16]════ [c25]GAMEBOT [c15]v4.5 [c16]════
[c15]One official command per action. No aliases.

[c10]━━ PLAYER ━━━━━━━━━━━━━━━
[c16]/HELP[c15] — help        [c16]/JOIN[c15] — join game
[c16]/LEAVE[c15] — leave      [c16]/PLAYERS[c15] — who joined
[c16]/CLUE[c15] — clue        [c16]/REPOST[c15] — repost
[c16]/STATUS[c15] — status    [c16]/SCORE[c15] — score
[c16]/LEADERBOARD[c15] — ranks [c16]/VERSION[c15] — version

[c04]━━ GAMES ━━━━━━━━━━━━━━━━
[c04]/TT ON[c15] — twist         [c04]/MATH ON[c15] — math
[c04]/TRIVIA ON[c15] — trivia    [c04]/ANIME ON[c15] — anime
[c04]/LOGIC ON[c15] — logic      [c04]/ALGEBRA ON[c15] — algebra
[c04]/PH ON[c15] — pinoy henyo   [c04]/RANDOM QUIZ1[c15] — mix1
[c04]/RANDOM QUIZ2[c15] — mix2   [c04]/RANDOM QUIZ3[c15] — mix3
[c04]/RANDOM GTA[c15] — gta      [c04]/GTA OPM[c15] — opm
[c04]/GTA FOREIGN[c15] — foreign [c04]/ENGLISH WORDHUNT[c15] — eng
[c04]/TAGALOG WORDHUNT[c15] — tag

[c20]━━ ADMIN ━━━━━━━━━━━━━━━━━
[c20]/STOP[c15] — stop           [c20]/PAUSE[c15] — pause
[c20]/RESUME[c15] — resume       [c20]/NEXT[c15] — next
[c20]/REVEAL[c15] — answer       [c20]/ACTIVATE[c15] — room
[c20]/LOCK[c15] — lock           [c20]/UNLOCK[c15] — unlock
[c20]/WCBOT ON[c15] — wc on      [c20]/WCBOT OFF[c15] — wc off
[c20]/WMSG <msg>[c15] — set msg  [c20]/CHALLENGE OFF[c15] — off
[c20]/CHALLENGE <room>[c15] — mirror to room

[c01]🎮 /JOIN to play · normal chat won't affect the game
[c01]/LEAVE to quit · /PLAYERS lists who's playing
[c25]Cybot Game Core 4.5"""

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
                        db.send(room,"[c09]New game started—previous players must /JOIN again to play.")
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
                            db.send(room,f"[c03]The Correct Answer is [c04]   {s.answer}")
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
