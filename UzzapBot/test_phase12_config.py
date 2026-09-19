"""Phase 12 tests for fail-closed AI canary configuration parsing."""
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, 0),
        ("", 0),
        ("abc", 0),
        ("  abc  ", 0),
        ("-1", 0),
        ("0", 0),
        ("11", 0),
        ("100", 0),
        ("1", 1),
        ("10", 10),
        (" 5 ", 5),
        (5, 5),
    ],
)
def test_parse_canary_percent_is_fail_closed(value, expected):
    assert config._parse_canary_percent(value) == expected


@pytest.mark.parametrize("value", ["abc", "-1", "0", "11", "100"])
def test_malformed_or_out_of_range_environment_does_not_crash_import(monkeypatch, value):
    monkeypatch.setenv("AI_CANARY_PERCENT", value)
    reloaded = importlib.reload(config)
    assert reloaded.AI_CANARY_PERCENT == 0


def test_valid_environment_value_is_preserved(monkeypatch):
    monkeypatch.setenv("AI_CANARY_PERCENT", "7")
    reloaded = importlib.reload(config)
    assert reloaded.AI_CANARY_PERCENT == 7


def test_default_is_safe_and_valid(monkeypatch):
    monkeypatch.delenv("AI_CANARY_PERCENT", raising=False)
    reloaded = importlib.reload(config)
    assert reloaded.AI_CANARY_PERCENT == 1
