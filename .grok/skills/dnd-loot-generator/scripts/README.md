# dnd-loot-generator scripts

`procedural_loot.py` — weighted loot generation with campaign ledger.

```bash
python .grok/skills/dnd-loot-generator/scripts/procedural_loot.py generate "Campaign" --cr 3
python .grok/skills/dnd-loot-generator/scripts/procedural_loot.py hoard "Campaign"
python .grok/skills/dnd-loot-generator/scripts/procedural_loot.py ledger "Campaign"
```

Party level is read from `state/player_character.json` when `--level` is omitted.