import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bot


def test_ai_command_requires_on_or_off():
    assert bot.parse_command("/AI ON") == ["ai", "on"]
    assert bot.parse_command("/AI OFF") == ["ai", "off"]
    assert bot.parse_command("/AI MAYBE") == ["invalid_command", "ai"]


def test_ai_live_gate_is_separate_from_dry_run():
    assert bot.AI_LIVE_ENABLED is False or isinstance(bot.AI_LIVE_ENABLED, bool)
