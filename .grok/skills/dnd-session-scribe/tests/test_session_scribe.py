import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))

from session_scribe import award_xp, end_session


def test_end_session_flow(campaign):
    result = end_session(campaign, "Explored the ruins.", xp=100)
    assert result["status"] == "session_saved"
    assert result["xp"]["total_xp"] == 100


def test_xp_level_up_detection(campaign):
    result = award_xp(campaign, 300, reason="Boss defeat")
    assert result["total_xp"] == 300
    assert result["derived_level"] == 2
    assert result["level_up"]["level_up_available"] is True