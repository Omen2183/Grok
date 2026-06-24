import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dnd-character-manager" / "scripts"))

from sync_bridge import on_player_damaged, on_player_death_save
import dnd_state_utils as state


def test_player_damage_sync(campaign):
    state.update_player_hp(campaign, new_current=20)
    on_player_damaged(campaign, 0)
    char = state.get_player_character(campaign)
    assert char["status"] == "Dying"

    on_player_death_save(campaign, True)
    char = state.get_player_character(campaign)
    assert char["death_saves"]["successes"] == 1