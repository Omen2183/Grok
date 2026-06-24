import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from rules_cheatsheet import list_topics, lookup_rule


def test_list_topics():
    topics = list_topics()
    assert "advantage" in topics
    assert "death_saves" in topics


def test_lookup_known_rule():
    result = lookup_rule("concentration")
    assert result["found"] is True
    assert "summary" in result


def test_lookup_unknown():
    result = lookup_rule("totally_fake_rule_xyz")
    assert result["found"] is False
    assert "available" in result