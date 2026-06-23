"""Unit tests for the XP/level formula in app.services.xp_service."""
from app.services.xp_service import (
    level_for_xp,
    xp_for_bug,
    xp_required_for_level,
)


def test_level_thresholds_match_spec():
    assert xp_required_for_level(1) == 0
    assert xp_required_for_level(2) == 100
    assert xp_required_for_level(3) == 300
    assert xp_required_for_level(4) == 600
    assert xp_required_for_level(5) == 1000


def test_level_thresholds_continue_progressively_beyond_5():
    # delta(5) = 500 -> L6 = 1000 + 500 = 1500
    assert xp_required_for_level(6) == 1500
    # delta(6) = 600 -> L7 = 1500 + 600 = 2100
    assert xp_required_for_level(7) == 2100


def test_level_for_xp_boundaries():
    assert level_for_xp(0) == 1
    assert level_for_xp(99) == 1
    assert level_for_xp(100) == 2
    assert level_for_xp(299) == 2
    assert level_for_xp(300) == 3
    assert level_for_xp(999) == 4
    assert level_for_xp(1000) == 5
    assert level_for_xp(1499) == 5
    assert level_for_xp(1500) == 6


def test_level_for_xp_beyond_precomputed_table_extends_correctly():
    # Sanity check that very large XP totals don't crash and keep increasing.
    high_level = level_for_xp(1_000_000)
    assert high_level > 5
    assert level_for_xp(2_000_000) >= high_level


def test_xp_for_bug_severity_formula():
    assert xp_for_bug("critical", is_duplicate=False, status="accepted") == 100
    assert xp_for_bug("high", is_duplicate=False, status="accepted") == 70
    assert xp_for_bug("medium", is_duplicate=False, status="accepted") == 50
    assert xp_for_bug("low", is_duplicate=False, status="accepted") == 25


def test_xp_for_bug_duplicate_awards_zero():
    assert xp_for_bug("critical", is_duplicate=True, status="duplicate") == 0


def test_xp_for_bug_rejected_awards_zero():
    assert xp_for_bug("high", is_duplicate=False, status="rejected") == 0
