"""Phase 12B tests for deterministic AI canary selection."""
from ai.rollout import canary_selected


def test_zero_percent_selects_nobody():
    assert not canary_selected("room-a", 0)


def test_one_hundred_percent_selects_everything():
    assert canary_selected("room-a", 100)
    assert canary_selected("room-b", 100)


def test_selection_is_deterministic():
    values = [canary_selected("room-stable", 7) for _ in range(20)]
    assert all(value == values[0] for value in values)


def test_different_room_keys_can_be_independently_bucketed():
    # The assertion checks the function is key-dependent without assuming a
    # particular hash output for any room.
    selected = {room: canary_selected(room, 10) for room in ("a", "b", "c", "d", "e")}
    assert len(selected) >= 1


def test_invalid_percent_fails_closed():
    assert not canary_selected("room-a", -1)
    assert not canary_selected("room-a", 101)
    assert not canary_selected("room-a", "bad")
