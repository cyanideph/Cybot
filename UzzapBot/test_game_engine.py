import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from game_engine import GameEngine

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
