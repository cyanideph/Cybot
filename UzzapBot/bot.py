"""Pydroid 3 entry point for UzzapBot."""
from __future__ import annotations
import logging,time,json
from config import (
    BOT_NAME, ADMIN_IDS, POLL_SECONDS, DEFAULT_POINTS, DEFAULT_LIMIT, validate,
    AI_ENABLED, AI_IDLE_MINUTES, AI_INACTIVE_MINUTES, AI_COOLDOWN_MINUTES,
    AI_MAX_MESSAGES_PER_HOUR, AI_MAX_MESSAGES_PER_DAY, AI_DRY_RUN,
    AI_MAX_REQUESTS_PER_DAY, AI_MIN_CONFIDENCE, AI_LIVE_ENABLED, AI_ROLLOUT_STAGE, AI_CANARY_PERCENT, GEMINI_API_KEY, GEMINI_FLASH_MODEL,
    AI_EMBEDDING_DIMENSIONS,
)
from database import Database
from game_engine import GameEngine
from ai.activity_engine import ActivityEngine
from ai.gemini_decision import GeminiDecisionClient
from ai.decision_engine import DecisionEngine
from ai.room_context import RoomContextManager
from ai.embedding import GeminiEmbedding
from ai.budget import request_budget_available, response_budget_available
from ai.rollout import evaluate_rollout, canary_selected

logging.basicConfig(level=logging.INFO,format="%(asctime)s | %(levelname)s | %(message)s")
log=logging.getLogger("uzzapbot")

_AI_DIAGNOSTIC_LAST: dict[str, str] = {}

def record_ai_diagnostic(
    db: Database,
    room: str,
    stage: str,
    reason: str | None = None,
    details: dict | None = None,
    force: bool = False,
) -> None:
    """Persist the latest non-secret AI gate reached, without poll-loop spam."""
    payload = details or {}
    signature = json.dumps(
        {"stage": stage, "reason": reason, "details": payload},
        sort_keys=True,
        default=str,
    )
    if not force and _AI_DIAGNOSTIC_LAST.get(room) == signature:
        return
    _AI_DIAGNOSTIC_LAST[room] = signature
    try:
        db.save_ai_diagnostic(room, stage, reason, payload)
    except Exception:
        log.exception('AI DIAGNOSTIC WRITE ERROR room="%s"', room)


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
[c16]/AI ON[c09] — Enable AI for this room
[c16]/AI OFF[c09] — Disable AI for this room
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
        ROOM_SETTINGS[room] = db.get_room_settings(room) if db else {"activated":False,"locked":False,"wcbot":False,"welcome_message":"welcome to {room} {nickname}","challenge_room":"", "ai_enabled":False}
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

    if command=="ai":
        if len(args)!=1 or args[0].casefold() not in {"on","off"}:
            return ["invalid_command","ai"]
        return ["ai",args[0].casefold()]

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


def run_ai_pass(db: Database, activity: ActivityEngine) -> None:
    """Run optional AI analysis only for eligible quiet rooms."""
    record_ai_diagnostic(db, "__GLOBAL__", "config",
        None if AI_ENABLED and GEMINI_API_KEY else "global_ai_gate",
        {
            "ai_enabled": bool(AI_ENABLED),
            "gemini_key_configured": bool(GEMINI_API_KEY),
            "ai_idle_minutes": AI_IDLE_MINUTES,
            "ai_inactive_minutes": AI_INACTIVE_MINUTES,
            "ai_cooldown_minutes": AI_COOLDOWN_MINUTES,
            "ai_live_enabled": bool(AI_LIVE_ENABLED),
            "ai_dry_run": bool(AI_DRY_RUN),
            "rollout_stage": AI_ROLLOUT_STAGE,
            "canary_percent": AI_CANARY_PERCENT,
        },
    )
    if not AI_ENABLED or not GEMINI_API_KEY:
        return

    rollout = evaluate_rollout({
        "rollout_stage": AI_ROLLOUT_STAGE,
        "canary_percent": AI_CANARY_PERCENT,
        "ai_enabled": AI_ENABLED,
        "ai_live_enabled": AI_LIVE_ENABLED,
        "ai_dry_run": AI_DRY_RUN,
        "min_confidence": AI_MIN_CONFIDENCE,
        "max_messages_per_hour": AI_MAX_MESSAGES_PER_HOUR,
        "max_messages_per_day": AI_MAX_MESSAGES_PER_DAY,
        "max_requests_per_day": AI_MAX_REQUESTS_PER_DAY,
    })
    # Phase 11 is an enforced runtime gate. Unsafe or inconsistent live
    # configuration fails closed before provider calls or message sends.
    if AI_LIVE_ENABLED and not AI_DRY_RUN and not rollout["ready"]:
        record_ai_diagnostic(db, "__GLOBAL__", "rollout_blocked",
            ",".join(rollout["findings"]) or "rollout_not_ready",
            {"findings": rollout["findings"]})
        log.error("AI LIVE ROLLOUT BLOCKED: %s", ",".join(rollout["findings"]))
        return
    record_ai_diagnostic(db, "__GLOBAL__", "rollout_passed", None,
        {"ready": bool(rollout["ready"]), "findings": rollout["findings"]})

    global_usage = db.ai_usage()
    if not request_budget_available(global_usage, AI_MAX_REQUESTS_PER_DAY):
        record_ai_diagnostic(db, "__GLOBAL__", "global_budget_blocked",
            "request_budget",
            {"usage": global_usage, "max_requests_per_day": AI_MAX_REQUESTS_PER_DAY})
        return
    record_ai_diagnostic(db, "__GLOBAL__", "global_budget_passed", None,
        {"usage": global_usage, "max_requests_per_day": AI_MAX_REQUESTS_PER_DAY})

    try:
        purged = db.purge_expired_room_memory()
        if purged:
            log.info("Purged %d expired AI memory item(s)", purged)
    except Exception:
        log.exception("AI MEMORY CLEANUP ERROR")

    client = GeminiDecisionClient(GEMINI_API_KEY, GEMINI_FLASH_MODEL)
    embedder = GeminiEmbedding(GEMINI_API_KEY, AI_EMBEDDING_DIMENSIONS)
    gate = DecisionEngine(AI_MIN_CONFIDENCE)
    context_manager = RoomContextManager(max_recent_messages=20, max_memory_items=5)

    for room_name in list(activity.rooms):
        # The durable Supabase room setting is the authoritative room-level AI gate.
        # Do not rely only on in-memory ActivityEngine state, because a restart,
        # stale cache, or another worker may have changed /AI ON|OFF.
        try:
            room_settings = db.get_room_settings(room_name)
            if not bool(room_settings.get("ai_enabled", False)):
                record_ai_diagnostic(db, room_name, "room_opt_in_blocked",
                    "room_ai_disabled", {"room_ai_enabled": False})
                continue
            activity.get_or_create(
                room_name,
                {
                    "enabled": True,
                    "idle_threshold_seconds": AI_IDLE_MINUTES * 60,
                    "inactive_threshold_seconds": AI_INACTIVE_MINUTES * 60,
                    "cooldown_seconds": AI_COOLDOWN_MINUTES * 60,
                    "max_messages_per_hour": AI_MAX_MESSAGES_PER_HOUR,
                    "max_messages_per_day": AI_MAX_MESSAGES_PER_DAY,
                },
            )
        except Exception as exc:
            record_ai_diagnostic(db, room_name, "room_settings_error", str(exc))
            log.exception('AI ROOM GATE ERROR room="%s"', room_name)
            continue

        eligibility = activity.eligibility(room_name)
        if not eligibility["eligible"] or eligibility["state"] not in {"QUIET", "INACTIVE"}:
            record_ai_diagnostic(
                db, room_name, "idle_gate_blocked",
                ",".join(eligibility.get("reasons") or []) or "not_quiet_or_inactive",
                {
                    "eligibility": eligibility,
                    "runtime_idle_threshold_seconds": AI_IDLE_MINUTES * 60,
                    "runtime_inactive_threshold_seconds": AI_INACTIVE_MINUTES * 60,
                    "runtime_cooldown_seconds": AI_COOLDOWN_MINUTES * 60,
                },
            )
            continue
        record_ai_diagnostic(db, room_name, "idle_gate_passed", None, {
            "eligibility": eligibility,
            "runtime_idle_threshold_seconds": AI_IDLE_MINUTES * 60,
            "runtime_inactive_threshold_seconds": AI_INACTIVE_MINUTES * 60,
            "runtime_cooldown_seconds": AI_COOLDOWN_MINUTES * 60,
        })

        usage = db.ai_usage(room_name)
        if not response_budget_available(usage, AI_MAX_MESSAGES_PER_HOUR, AI_MAX_MESSAGES_PER_DAY):
            record_ai_diagnostic(db, room_name, "room_budget_blocked",
                "response_budget", {"usage": usage,
                "max_messages_per_hour": AI_MAX_MESSAGES_PER_HOUR,
                "max_messages_per_day": AI_MAX_MESSAGES_PER_DAY})
            continue
        record_ai_diagnostic(db, room_name, "room_budget_passed", None,
            {"usage": usage})

        recent = db.recent_room_messages(room_name, 20)
        if not recent:
            record_ai_diagnostic(db, room_name, "no_recent_messages",
                "no_human_messages")
            activity.get_or_create(room_name).record_ai_analysis()
            db.save_room_activity(activity.snapshot(room_name))
            continue

        summary = db.load_room_summary(room_name)
        stored_memory = db.load_room_memory(room_name, 5)
        base_context = context_manager.build(room_name, recent, summary, stored_memory)
        query_context = base_context.prompt_text()

        query_embedding = embedder.embed_query(query_context)
        semantic_memory = []
        if query_embedding.ok and query_embedding.values:
            try:
                semantic_memory = db.semantic_room_memory(
                    room_name, query_embedding.values, threshold=0.72, limit=5
                )
            except Exception:
                log.exception('AI MEMORY RETRIEVAL ERROR room="%s"', room_name)

        context = context_manager.build(
            room_name, recent, summary, semantic_memory or stored_memory
        )
        conversation = context.prompt_text()
        record_ai_diagnostic(db, room_name, "provider_call", "gemini_decide",
            {"input_chars": len(conversation), "model": GEMINI_FLASH_MODEL},
            force=True)
        result = client.decide(conversation)
        activity.get_or_create(room_name).record_ai_analysis()
        db.save_room_activity(activity.snapshot(room_name))

        if not result.ok:
            record_ai_diagnostic(db, room_name, "provider_error", result.error,
                {"input_chars": len(conversation), "model": GEMINI_FLASH_MODEL},
                force=True)
            db.save_ai_event({
                "room_name": room_name,
                "event_type": "decision_error",
                "dry_run": True,
                "reason": result.error,
                "input_chars": len(conversation),
            })
            continue

        decision = result.decision or {}
        validated = gate.validate(decision)
        record_ai_diagnostic(db, room_name, "decision_validated",
            validated.get("reason"), {
                "allowed": bool(validated.get("allowed")),
                "topic": decision.get("topic"),
                "confidence": decision.get("confidence"),
                "action": decision.get("action"),
                "game": validated.get("game"),
            }, force=True)
        db.save_ai_event({
            "room_name": room_name,
            "event_type": "decision",
            "dry_run": AI_DRY_RUN,
            "topic": decision.get("topic"),
            "confidence": decision.get("confidence"),
            "action": decision.get("action"),
            "game": validated.get("game"),
            "allowed": validated.get("allowed"),
            "reason": validated.get("reason"),
            "response": validated.get("response"),
            "input_chars": len(conversation),
        })

        # Keep a short-lived deterministic memory snapshot for future context.
        # It is never treated as an instruction and cannot execute commands.
        memory_content = conversation[-1800:]
        db.save_room_memory({
            "room_name": room_name,
            "memory_type": "conversation_window",
            "content": memory_content,
            "source_message_id": recent[-1].get("id"),
            "metadata": {
                "source": "ai_pass",
                "topic": decision.get("topic") or "GENERAL",
                "message_count": len(recent),
            },
        })
        db.save_room_summary({
            "room_name": room_name,
            "summary": memory_content,
            "topic": str(decision.get("topic") or "GENERAL"),
            "message_count": len(recent),
            "source_through_message_id": recent[-1].get("id"),
        })

        document_embedding = embedder.embed_document(
            memory_content, title=f"{room_name} room context"
        )
        if document_embedding.ok and document_embedding.values:
            try:
                latest = db.load_room_memory(room_name, 1)
                if latest:
                    db.save_room_memory_embedding(
                        int(latest[-1]["id"]), document_embedding.values
                    )
            except Exception:
                log.exception('AI MEMORY EMBEDDING SAVE ERROR room="%s"', room_name)

        if AI_LIVE_ENABLED and not AI_DRY_RUN and validated.get("allowed") and validated.get("response"):
            # Re-check the durable output budget immediately before sending.
            # This keeps the cap authoritative even if another worker wrote an
            # AI response after the initial eligibility check.
            latest_usage = db.ai_usage(room_name)
            if response_budget_available(
                latest_usage, AI_MAX_MESSAGES_PER_HOUR, AI_MAX_MESSAGES_PER_DAY
            ):
                record_ai_diagnostic(db, room_name, "response_sent",
                    "live_response", {"latest_usage": latest_usage}, force=True)
                db.send(room_name, validated["response"])
            else:
                record_ai_diagnostic(db, room_name, "response_budget_blocked",
                    "final_response_budget", {"latest_usage": latest_usage},
                    force=True)
                db.save_ai_event({
                    "room_name": room_name,
                    "event_type": "response_sent",
                    "dry_run": False,
                    "allowed": True,
                    "reason": "response_sent",
                    "response": validated["response"],
                    "input_chars": len(conversation),
                })

def main()->None:
    validate()
    db,games=Database(),GameEngine()
    activity=ActivityEngine({
        "enabled": AI_ENABLED,
        "idle_threshold_seconds": AI_IDLE_MINUTES * 60,
        "inactive_threshold_seconds": AI_INACTIVE_MINUTES * 60,
        "cooldown_seconds": AI_COOLDOWN_MINUTES * 60,
        "max_messages_per_hour": AI_MAX_MESSAGES_PER_HOUR,
        "max_messages_per_day": AI_MAX_MESSAGES_PER_DAY,
    })
    restored_activity = activity.load(db.load_room_activity())
    restored=games.restore_all(db.load_game_state())
    seen_participants=set()
    db.poll_new_participants(seen_participants)
    log.info("Restored %d room-activity state(s)",restored_activity)
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
                    settings = db.get_room_settings(room)
                    activity.record_human_message(
                        room,
                        settings={
                            "enabled": AI_ENABLED and bool(settings.get("ai_enabled", False)),
                            "idle_threshold_seconds": AI_IDLE_MINUTES * 60,
                            "inactive_threshold_seconds": AI_INACTIVE_MINUTES * 60,
                            "cooldown_seconds": AI_COOLDOWN_MINUTES * 60,
                            "max_messages_per_hour": AI_MAX_MESSAGES_PER_HOUR,
                            "max_messages_per_day": AI_MAX_MESSAGES_PER_DAY,
                        },
                    )
                    db.save_room_activity(activity.snapshot(room))
                except Exception:
                    # Activity tracking must never break the existing bot.
                    log.exception('ROOM ACTIVITY ERROR room="%s"', room)
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
                    admin_commands={"stop","pause","resume","next","reveal","activate","lock","unlock","ai","wcbot","wmsg","challenge","challenge_off"}
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

                    if sub=="ai":
                        cfg=room_settings(room,db)
                        cfg["ai_enabled"] = args[1] == "on"
                        save_room_settings(db,room)
                        activity.get_or_create(room, {
                            "enabled": AI_ENABLED and cfg["ai_enabled"],
                            "idle_threshold_seconds": AI_IDLE_MINUTES * 60,
                            "inactive_threshold_seconds": AI_INACTIVE_MINUTES * 60,
                            "cooldown_seconds": AI_COOLDOWN_MINUTES * 60,
                            "max_messages_per_hour": AI_MAX_MESSAGES_PER_HOUR,
                            "max_messages_per_day": AI_MAX_MESSAGES_PER_DAY,
                        })
                        db.save_room_activity(activity.snapshot(room))
                        db.send(room, "[c03]Room AI enabled." if cfg["ai_enabled"] else "[c08]Room AI disabled.")
                    elif sub=="help": db.send(room,HELP)
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
            try:
                run_ai_pass(db, activity)
            except Exception:
                # AI is optional; a provider or AI bug must never stop the
                # deterministic bot/game loop.
                log.exception("AI PASS ERROR")
            time.sleep(POLL_SECONDS)
        except KeyboardInterrupt:
            log.info("Bot stopped by user"); return
        except Exception:
            log.exception("Bot loop error; reconnecting"); time.sleep(max(POLL_SECONDS,2.0))

if __name__=="__main__": main()
