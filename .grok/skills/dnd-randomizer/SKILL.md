---
name: dnd-randomizer
description: Unified D&D randomization for any campaign need — weighted tables, random items, full characters (race, class, feats, spells, stats, class kits), NPCs, parties, encounters, dungeons, quests, worlds, wild magic surges, and total-chaos packages. v5.3.0 production. Triggers include randomize, random item, random character, random party, random dungeon, wild magic surge, roll table, surprise me, chaos campaign, balanced random. Delegates CR-scaled loot/encounters via --balanced; owns pure randomness and table rolls.
---

# D&D Randomizer

## When to Use
- Player or DM wants **anything random** — item drop, NPC, encounter, dungeon floor, full PC or party
- Rolling on DM tables (weather, complications, wild magic, traps)
- **Chaos mode** — one-shot random campaign package (`random-everything`)
- Seeding a new campaign with random character + world (`apply-character`, `apply-world`)
- **Balanced mode** — `--balanced` on items/encounters delegates to loot-generator / content-forge

**Do not use when:**
- Transparent dice mechanics → `dnd-dice-engine`
- Campaign-reactive rumors tied to live state → `dnd-rumor-event-generator`
- Persistent NPC relationship tracking alone → `dnd-npc-personality-weaver` (use `apply-npc` after random-npc)

## Quick Start (Mobile)
1. **"Random magic item"** → `random-item`
2. **"Balanced loot for level 5"** → `random-item "Campaign" --level 5 --balanced`
3. **"Roll a travel complication"** → `roll-table travel_complication`
4. **"Generate a random level 5 character"** → `random-character --level 5`
5. **"Roll up a party of four"** → `random-party --size 4 --level 3`
6. **"Random dungeon floor"** → `random-dungeon "Campaign" --party-level 4`
7. **"Wild magic surge"** → `wild-magic-surge`
8. **"Surprise me with everything"** → `random-everything`

## Capabilities (Honest Matrix)
| Capability | Status | Notes |
|------------|--------|-------|
| Weighted table engine | ✅ Implemented | Builtin + custom tables, ledger anti-repeat |
| Random item (mundane/magic) | ✅ Implemented | `random-item`; ledger when campaign set |
| Balanced random loot | ✅ Implemented | `--balanced` → `dnd-loot-generator` |
| Random full character | ✅ Implemented | Stats 4d6 drop lowest, class kits, gold, feats, spells |
| Cultural name generation | ✅ Implemented | 6 cultures; race-aware defaults |
| Class starting equipment | ✅ Implemented | Per-class kits + scaled gold |
| Multiclass random PCs | ✅ Implemented | `--multiclass` + `build_plan` via class_progression |
| Random party (3–5 PCs) | ✅ Implemented | `random-party` |
| Random NPC | ✅ Implemented | Role, traits, motivation, quirk |
| Random world + kingdom sketch | ✅ Implemented | Domain, factions, resources, threat, hook |
| Random encounter (chaos) | ✅ Implemented | Unbalanced foes |
| Balanced random encounter | ✅ Implemented | `--balanced` → `dnd-content-forge` |
| Procedural dungeon floor | ✅ Implemented | Rooms, traps, foes, exits |
| Random quest hook | ✅ Implemented | `random-quest` |
| Random feat / spell | ✅ Implemented | SRD pools via `srd_data.py` |
| Wild magic surge hook | ✅ Implemented | `wild-magic-surge` on spell cast |
| Total chaos package | ✅ Implemented | `random-everything` |
| Apply to campaign state | ✅ Implemented | `apply-character`, `apply-world` (confirm first) |
| Custom homebrew tables | ✅ Implemented | `add-table-entry` |
| Import / export tables | ✅ Implemented | `import-tables`, `export-tables` |
| Roll ledger | ✅ Implemented | `randomizer_ledger.json` per campaign |
| Persist random NPC / quest | ✅ Implemented | `apply-npc`, `apply-quest` |
| Travel day batch rolls | ✅ Implemented | `travel-day` |
| Mobile/voice one-liner | ✅ Implemented | `mobile-summary` |

## Tools & Scripts
Primary: `randomizer.py` — Libraries: `randomizer_engine.py`, `randomizer_data.py`, `name_cultures.py`, `equipment_generator.py`, `dungeon_generator.py`

```bash
python .grok/skills/dnd-randomizer/scripts/randomizer.py list-tables "My Campaign"
python .grok/skills/dnd-randomizer/scripts/randomizer.py roll-table weather "My Campaign"
python .grok/skills/dnd-randomizer/scripts/randomizer.py random-item "My Campaign" --level 5 --balanced
python .grok/skills/dnd-randomizer/scripts/randomizer.py random-character --level 3 --multiclass
python .grok/skills/dnd-randomizer/scripts/randomizer.py random-party --size 4 --level 3
python .grok/skills/dnd-randomizer/scripts/randomizer.py random-name --culture dwarven
python .grok/skills/dnd-randomizer/scripts/randomizer.py random-dungeon "My Campaign" --rooms 8
python .grok/skills/dnd-randomizer/scripts/randomizer.py random-encounter "My Campaign" --balanced
python .grok/skills/dnd-randomizer/scripts/randomizer.py wild-magic-surge "My Campaign"
python .grok/skills/dnd-randomizer/scripts/randomizer.py export-tables "My Campaign" --output tables.json
python .grok/skills/dnd-randomizer/scripts/randomizer.py import-tables "My Campaign" tables.json
python .grok/skills/dnd-randomizer/scripts/randomizer.py random-world "My Campaign"
python .grok/skills/dnd-randomizer/scripts/randomizer.py random-feat
python .grok/skills/dnd-randomizer/scripts/randomizer.py random-spell --max-level 3
python .grok/skills/dnd-randomizer/scripts/randomizer.py add-random-loot "My Campaign" --level 5
python .grok/skills/dnd-randomizer/scripts/randomizer.py list-cultures
python .grok/skills/dnd-randomizer/scripts/randomizer.py mobile-summary party --level 3
```

## Behavior
- **Chaos vs balanced:** Default is surprise. Add `--balanced` for CR-aware loot or XP-budget encounters.
- **Apply commands overwrite** `player_character.json` or world/kingdom state — always confirm with player first.
- **Wild magic:** Call `wild-magic-surge` when a sorcerer rolls a 1 on surge check or DM wants table chaos.
- Keep mobile output ≤8 lines; offer detail on request.

## Skill Coordination
| Layer | Role |
|-------|------|
| Registry | Intent `random`; playbooks `chaos-campaign`, `random-session`, `party-generator` |
| Voice (iOS) | party, dungeon, wild magic phrases routed here |

## Integration
| Skill | Relationship |
|-------|--------------|
| dnd-loot-generator | Balanced treasure via `--balanced`; chaos drops stay here |
| dnd-content-forge | Balanced encounters via `--balanced` |
| dnd-rumor-event-generator | Context-aware rumors vs generic table rolls |
| dnd-character-manager | Sheet edits after `apply-character` / `add-random-loot` |
| dnd-npc-personality-weaver | `apply-npc` persists generated NPCs |
| dnd-quest-tracker | `apply-quest` saves random hooks |
| dnd-dice-engine | Player-facing transparent rolls |
| dnd-utils | State read/write, event logging |

## iOS / Voice Notes
- *"Roll weather"* → `roll-table weather [campaign]`
- *"Random party level three"* → `random-party --size 4 --level 3`
- *"Wild magic surge"* → `wild-magic-surge`
- *"Balanced random loot"* → `random-item [campaign] --balanced`
- Never run `apply-character` / `apply-world` without explicit player confirmation