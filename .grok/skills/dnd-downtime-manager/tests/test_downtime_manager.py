import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))

from downtime_manager import get_rest_status, long_rest, short_rest


def test_long_rest(campaign):
    result = long_rest(campaign)
    assert result["rest"] == "long"
    assert result["hp"]["current"] == result["hp"]["max"]


def test_short_rest_no_hd(campaign):
    result = short_rest(campaign, spend_hd=0)
    assert result["rest"] == "short"
    assert result["healed"] == 0


def test_rest_status(campaign):
    status = get_rest_status(campaign)
    assert "hp" in status