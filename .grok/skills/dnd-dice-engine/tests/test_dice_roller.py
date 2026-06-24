import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from dice_roller import parse_dice_notation, roll_dice


def test_parse_basic_notation():
    parsed = parse_dice_notation("2d6+3")
    assert parsed["num_dice"] == 2
    assert parsed["die_size"] == 6
    assert parsed["modifier"] == 3


def test_advantage_in_notation():
    result = roll_dice("1d20 advantage")
    assert result.get("advantage") is True
    assert "roll_1" in result
    assert "roll_2" in result


def test_keep_highest():
    result = roll_dice("4d6kh3")
    assert len(result.get("kept", [])) == 3