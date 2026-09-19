import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from game_engine import GameEngine, Player

def test_legacy_math_modes():
    e=GameEngine()
    for mode in ("add","minus","multiply","add1","minus1","multiply1"):
        s=e.start("room-"+mode,mode,10,100)
        assert s.answer and s.current_game==mode

def test_algebra_modes():
    e=GameEngine()
    e1=e.start("room-algebra1","algebra1",10,100)
    e2=e.start("room-algebra2","algebra2",10,100)
    e3=e.start("room-algebra3","algebra3",10,100)

    assert e1.answer and e1.mode==e1.current_game=="algebra1"
    assert e2.answer and e2.mode==e2.current_game=="algebra2"
    assert e3.answer and e3.mode==e3.current_game=="algebra3"

    # Validate distinct algebra operators; internal mode names need not
    # appear in human-facing question text.
    assert " + " in e1.question
    assert " - " in e2.question
    assert " x " in e3.question

def test_random_modes():
    e=GameEngine()
    for mode in ("random1","random2","random3","randomgta","math","algebra"):
        s=e.start("room-"+mode,mode,10,100)
        assert s.mode==mode and s.current_game

def test_limit_is_score_target():
    e=GameEngine()
    s=e.start("score-room","add",10,100)
    s.answer="2"
    ok,_=e.answer("score-room","u","user","user","2")
    assert ok and not s.paused and s.number==2

def test_endless_does_not_finish_at_limit():
    e=GameEngine()
    s=e.start("endless-room","add",100,100,endless=True)
    s.answer="2"
    ok,_=e.answer("endless-room","u","user","user","2")
    assert ok and not s.paused

def test_unicode_normalization_and_scramble():
    e=GameEngine()
    assert e._normalize(" Café ")=="café"
    assert e._normalize(e._scramble("HELLO"))!="hello"


def test_progressive_clues_reveal_more_without_exposing_answer():
    games=GameEngine()
    session=games.start("clue-test","math")
    session.answer="ABCDEFGH"
    session.question="TEST"
    session.clue_level=0

    first=games.clue("clue-test")
    second=games.clue("clue-test")
    third=games.clue("clue-test")
    fourth=games.clue("clue-test")

    assert "1/3" in first
    assert "2/3" in second
    assert "3/3" in third
    assert "Maximum clues" in fourth
    assert session.clue_level==3
    assert session.clue_text!=session.answer


def test_clue_usage_is_tracked_per_player():
    games=GameEngine()
    session=games.start("clue-player-test","math")
    session.answer="ABCDEFGH"
    session.players["u1"]=Player("u1","user1","User One")

    for _ in range(4):
        games.clue("clue-player-test","u1")

    assert session.players["u1"].clues_used==3
    assert "Clues: 3" in games.score_text("clue-player-test","u1")


def test_clue_progress_resets_for_next_question():
    games=GameEngine()
    session=games.start("clue-reset-test","math")
    session.answer="ABCDEFGH"

    games.clue("clue-reset-test")
    assert session.clue_level==1

    games._next(session)
    assert session.clue_level==0
    assert session.clue_text==""
