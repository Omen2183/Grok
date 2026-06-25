import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from dice_roller import (
    apply_damage_modifiers,
    count_successes,
    parse_dice_notation,
    roll_crit,
    roll_dice,
    roll_percentile,
    roll_d3,
    roll_single_pool,
)


def test_parse_basic_notation():
    parsed = parse_dice_notation("2d6+3")
    assert parsed["num_dice"] == 2
    assert parsed["die_size"] == 6
    assert parsed["modifier"] == 3


def test_parse_multi_pool():
    parsed = parse_dice_notation("1d8+1d6+5")
    assert parsed["roll_type"] == "multi_pool"
    assert len(parsed["pools"]) == 2
    assert parsed["flat_modifier"] == 5


def test_multi_pool_roll():
    result = roll_dice("1d8+1d6")
    assert result["roll_type"] == "multi_pool"
    assert len(result["pools"]) == 2
    assert result["total"] >= 2


def test_fudge_dice_pool():
    result = roll_single_pool(4, "F")
    assert result["die_type"] == "fudge"
    assert len(result["rolls"]) == 4
    assert all(v in (-1, 0, 1) for v in result["rolls"])


def test_parse_fudge_notation():
    parsed = parse_dice_notation("4dF")
    assert parsed["roll_type"] == "multi_pool"
    assert parsed["pools"][0]["is_fudge"] is True


def test_advantage_in_notation():
    result = roll_dice("1d20 advantage")
    assert result.get("advantage") is True
    assert "roll_1" in result
    assert "roll_2" in result


def test_keep_highest():
    result = roll_dice("4d6kh3")
    assert len(result.get("kept", [])) == 3


def test_percentile_roll():
    parsed = parse_dice_notation("d100")
    assert parsed["roll_type"] == "percentile"
    result = roll_percentile()
    assert 1 <= result["total"] <= 100


def test_d3_roll():
    parsed = parse_dice_notation("d3")
    assert parsed["roll_type"] == "d3"
    result = roll_d3()
    assert 1 <= result["total"] <= 3
    assert 1 <= result["underlying_d6"] <= 6


def test_adv_disadv_cancel():
    result = roll_dice("1d20 advantage disadvantage")
    assert not result.get("advantage")
    assert not result.get("disadvantage")
    assert "roll_1" not in result


def test_apply_damage_resistance():
    mod = apply_damage_modifiers(10, resistance=True)
    assert mod["final"] == 5


def test_apply_damage_immunity():
    mod = apply_damage_modifiers(20, immunity=True)
    assert mod["final"] == 0


def test_roll_crit_doubles_dice():
    result = roll_crit("2d6+3")
    assert result["crit"] is True
    assert result["total"] >= 3


def test_count_successes():
    result = count_successes("6d10", target=8)
    assert "successes" in result
    assert result["successes"] >= 0
    assert len(result["rolls"]) == 6