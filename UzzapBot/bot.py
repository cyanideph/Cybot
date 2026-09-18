"""Pydroid 3 entry point for UzzapBot."""
from __future__ import annotations
import logging, time
from config import BOT_NAME, ADMIN_IDS, ADMIN_USERNAMES, POLL_SECONDS, DEFAULT_POINTS, DEFAULT_LIMIT, validate
from database import Database
from game_engine import GameEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("uzzapbot")

HELP = """[c03]UZZAPBOT GAME COMMANDS
[c01]!game start math [points] [limit]
!game start mathminus
!game start mathmultiply
!game start trivia
!game start anime
!game start gtaopm
!game start gtaforeign
!game start logic
!game start wordhunt
!game start tagalog
!game start twist
!game start algebra1
!game start algebra2
!game start algebra3
!game stop
!game pause
!game resume
!game next
!game clue
!game repost
!game status
!game score
!game leaderboard"""

def is_admin(msg: dict) -> bool:
    return str(msg.get("sender_id") or "") in ADMIN_IDS or str(msg.get("sender") or "").casefold() in ADMIN_USERNAMES

def persist(db: Database, games: GameEngine, room: str) -> None:
    state = games.export_state(room)
    if state:
        db.save_game_state(state)

def main() -> None:
    validate()
    db, games = Database(), GameEngine()
    restored = games.restore_all(db.load_game_state())
    log.info("Restored %d persistent game session(s)", restored)
    log.info("%s connected; polling every %.1fs", BOT_NAME, POLL_SECONDS)
    while True:
        try:
            for msg in db.poll_messages():
                room = str(msg.get("room_name") or "").strip()
                text = str(msg.get("body") or "").strip()
                username = str(msg.get("sender") or "").strip()
                uid = str(msg.get("sender_id") or "")
                if not room or not text:
                    continue
                try:
                    if text.casefold().startswith("!game"):
                        admin = is_admin(msg)
                        log.info('COMMAND room="%s" sender="%s" body=%r admin=%s', room, username, text, admin)
                        if not admin:
                            db.send(room, "[c08]Game controls are admin-only during testing.")
                            continue
                        args = text.split()
                        sub = args[1].casefold() if len(args) > 1 else "help"
                        if sub == "help":
                            db.send(room, HELP)
                        elif sub == "start":
                            game = args[2] if len(args) > 2 else "math"
                            points = int(args[3]) if len(args) > 3 else DEFAULT_POINTS
                            limit = int(args[4]) if len(args) > 4 else DEFAULT_LIMIT
                            games.start(room, game, points, limit)
                            persist(db, games, room)
                            db.send(room, games.repost(room))
                        elif sub == "stop":
                            if games.get(room):
                                games.stop(room); db.delete_game_state(room); db.send(room, "[c08]Game stopped.")
                            else:
                                db.send(room, "[c08]No active game.")
                        elif sub == "pause":
                            s = games.get(room)
                            if not s: db.send(room, "[c08]No active game.")
                            else:
                                s.paused = True; persist(db, games, room); db.send(room, "[c12]Game paused.")
                        elif sub == "resume":
                            s = games.get(room)
                            if not s: db.send(room, "[c08]No active game.")
                            else:
                                s.paused = False; persist(db, games, room); db.send(room, "[c10]Game resumed.\n" + games.repost(room))
                        elif sub == "next":
                            db.send(room, games.next_question(games.get(room))); persist(db, games, room)
                        elif sub == "clue":
                            db.send(room, games.clue(room)); persist(db, games, room)
                        elif sub == "repost":
                            db.send(room, games.repost(room))
                        elif sub == "status":
                            db.send(room, games.status(room))
                        elif sub == "score":
                            db.send(room, games.score_text(room, uid))
                        elif sub == "leaderboard":
                            db.send(room, games.leaderboard_text(room))
                        else:
                            db.send(room, "[c08]Unknown game command. Use !game help")
                        continue
                    session = games.get(room)
                    if session and not text.startswith("/"):
                        profile = db.profile(uid, username) or {}
                        nickname = str(profile.get("nickname") or username)
                        _, response = games.answer(room, uid, username, nickname, text)
                        if response:
                            persist(db, games, room)
                            db.send(room, response)
                except Exception as exc:
                    log.exception('COMMAND ERROR room="%s" sender="%s"', room, username)
                    db.send(room, f"[c08]Game error: {exc}")
            time.sleep(POLL_SECONDS)
        except KeyboardInterrupt:
            log.info("Bot stopped by user"); return
        except Exception:
            log.exception("Bot loop error; reconnecting")
            time.sleep(max(POLL_SECONDS, 2.0))

if __name__ == "__main__":
    main()
