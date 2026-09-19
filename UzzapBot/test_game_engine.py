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
    e.join("score-room","u","user","user")
    s.answer="2"
    ok,_=e.answer("score-room","u","user","user","2")
    assert ok and not s.paused and s.number==2

def test_endless_does_not_finish_at_limit():
    e=GameEngine()
    s=e.start("endless-room","add",100,100,endless=True)
    e.join("endless-room","u","user","user")
    s.answer="2"
    ok,_=e.answer("endless-room","u","user","user","2")
    assert ok and not s.paused

def test_unicode_normalization_and_scramble():
    e=GameEngine()
    assert e._normalize(" Café ")=="cafe"
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


def test_better_answer_matching_accepts_small_typo_but_protects_math():
    e=GameEngine()
    assert e._answer_matches("Micheal Jackson","Michael Jackson")
    assert e._answer_matches("cafe","café")
    assert not e._answer_matches("123","124")
    assert not e._answer_matches("abc","abcd")


def test_random_game_types_do_not_repeat_recently():
    e=GameEngine()
    s=e.start("random-repeat-room","random3",10,100)
    seen=[]
    for _ in range(12):
        game=e._choose_random_game(s)
        seen.append(game)
    for i in range(2,len(seen)):
        assert seen[i] != seen[i-1]
        assert seen[i] != seen[i-2]


def test_generated_math_questions_are_not_repeated():
    e=GameEngine()
    s=e.start("generated-repeat-room","add",10,100)
    first=s.question
    for _ in range(25):
        e._next(s)
    assert first not in [s.question]
    assert len([x for x in s.used_questions if x.startswith("generated:")]) >= 20


def test_random_game_cycle_uses_each_type_once_before_reset():
    e=GameEngine()
    s=e.start("cycle-room","randomgta",10,100)
    cycle_types=set(e.RANDOM_GTA)
    first_cycle=list(s.cycle_games_used)
    while len(set(s.cycle_games_used)) < len(cycle_types):
        e._choose_random_game(s)
        first_cycle=list(s.cycle_games_used)

    assert set(first_cycle)==cycle_types
    assert len(first_cycle)==len(cycle_types)
    assert s.cycle_number==1

    next_game=e._choose_random_game(s)
    assert s.cycle_number==2
    assert next_game in cycle_types
    assert s.cycle_games_used==[next_game]


def test_random_cycle_state_persists_through_export_restore():
    e=GameEngine()
    s=e.start("cycle-state-room","random3",10,100)
    e._choose_random_game(s)
    e._choose_random_game(s)

    state=e.export_state("cycle-state-room")
    restored=GameEngine()
    s2=restored.restore_state(state)

    assert s2.cycle_number==s.cycle_number
    assert s2.cycle_games_used==s.cycle_games_used
    assert s2.recent_games==s.recent_games


def test_answer_matching_accepts_intended_typos_but_rejects_partials_and_empty():
    e=GameEngine()

    # Intended typo tolerance for long text answers.
    assert e._answer_matches("Micheal Jackson", "Michael Jackson")
    assert e._answer_matches("Beattles", "Beatles")

    # Exact answers still work after normalization.
    assert e._answer_matches("  CAFÉ  ", "cafe")

    # Partial names/answers must not receive credit.
    assert not e._answer_matches("Michael", "Michael Jackson")
    assert not e._answer_matches("Jackson", "Michael Jackson")
    assert not e._answer_matches("", "Michael Jackson")
    assert not e._answer_matches("   ", "Michael Jackson")


def test_answer_matching_never_uses_fuzzy_logic_for_numeric_answers():
    e=GameEngine()

    assert e._answer_matches("42", "42")
    assert not e._answer_matches("43", "42")
    assert not e._answer_matches("420", "42")
    assert not e._answer_matches("041", "42")


def test_gta_question_text_cannot_be_used_as_the_artist_answer():
    e=GameEngine()
    session=e.start("gta-anti-leak", "gtaopm", 10, 100)
    e.join("gta-anti-leak", "u1", "alice", "Alice")

    # The game exposes the song title but the required answer is the artist.
    session.question = "TiTLE: 'Buwan'\\n~> Guess The Artist [OPM]"
    session.answer = "Juan Karlos"

    leaked_question_text = "Buwan"
    correct, response = e.answer(
        "gta-anti-leak", "u1", "alice", "Alice", leaked_question_text
    )

    assert correct is False
    assert response
    player=session.players["u1"]
    assert player.score == 0
    assert player.correct == 0
    assert player.attempts == 1


def test_gta_artist_matching_allows_small_typo_but_not_song_title():
    e=GameEngine()
    session=e.start("gta-artist-match", "gtaforeign", 10, 100)
    e.join("gta-artist-match", "u1", "alice", "Alice")

    session.question = "TiTLE: 'Thriller'\\n~> Guess The Artist"
    session.answer = "Michael Jackson"

    wrong, _ = e.answer(
        "gta-artist-match", "u1", "alice", "Alice", "Thriller"
    )
    assert wrong is False
    assert session.players["u1"].score == 0

    # Restore the same question/answer because a wrong answer does not advance.
    correct, response = e.answer(
        "gta-artist-match", "u1", "alice", "Alice", "Micheal Jackson"
    )
    assert correct is True
    assert response
    assert session.players["u1"].correct == 1
    assert session.players["u1"].score == 10
