import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from xp_tables import check_level_up, level_from_xp, xp_to_next_level


def test_level_from_xp():
    assert level_from_xp(0) == 1
    assert level_from_xp(300) == 2
    assert level_from_xp(355000) == 20


def test_xp_to_next_level():
    assert xp_to_next_level(0) == 300
    assert xp_to_next_level(355000) is None


def test_check_level_up_pending():
    info = check_level_up({"level": 1, "xp": 900})
    assert info["derived_level"] == 3
    assert info["pending_level_ups"] == 2
    assert info["level_up_available"] is True