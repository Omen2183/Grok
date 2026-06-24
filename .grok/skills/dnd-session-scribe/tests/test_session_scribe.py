import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))

from session_scribe import award_xp, end_session


def test_end_session_flow(campaign):
    result = end_session(campaign, "Explored the ruins.", xp=100)
    assert result["status"] == "session_saved"
    assert result["xp"]["total_xp"] == 100