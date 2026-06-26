---
name: dnd-randomizer
description: Unified D&D randomization for any campaign need — weighted tables, random items, full characters (race, class, feats, spells, stats), NPCs, encounters, quests, worlds, and total-chaos packages. v4.1.0 production. Triggers include randomize, random item, random character, random world, roll table, surprise me, chaos campaign, random feat, random spell, random everything. Delegates balanced loot to loot-generator when player wants CR-scaled rewards; this skill owns pure randomness and table rolls.
---

# D&D Randomizer

## When to Use
- Player or DM wants **anything random** — item drop, NPC, encounter, world seed, full PC
- Rolling on DM tables (weather, complications, dungeon features)
- **Chaos mode** — one-shot random campaign package (`random-everything`)
- Seeding a new campaign with random character + world (`apply-character`, `apply-world`)

**Do not use when:**
- Transparent dice mechanics → `dnd-dice-engine`
- CR-balanced treasure with duplicate protection → `dnd-loot-generator`
- Campaign-reactive rumors tied to live state → `dnd-rumor-event-generator`
- Balanced encounter design → `dnd-content-forge`

## Quick Start (Mobile)
1. **"Random magic item"** → `random-item`
2. **"Roll a travel complication"** → `roll-table travel_complication`
3. **"Generate a random level 5 character"** → `random-character --level 5`
4. **"Surprise me with everything"** → `random-everything`
5. **"Seed this campaign with chaos"** → `apply-world` + `apply-character` (confirm first)

## Capabilities (Honest Matrix)
| Capability | Status | Notes |
|------------|--------|-------|
| Weighted table engine | ✅ Implemented | Builtin + custom tables, ledger anti-repeat |
| Random item (mundane/magic) | ✅ Implemented | `random-item`; ledger when campaign set |
| Random full character | ✅ Implemented | Stats 4d6 drop lowest, class, feats, spells, inventory |
| Multiclass random PCs | ✅ Implemented | `--multiclass` + `build_plan` via class_progression |
| Random NPC | ✅ Implemented | Role, traits, motivation, quirk |
| Random world + kingdom sketch | ✅ Implemented | Domain, factions, resources, threat, hook |
| Random encounter (chaos) | ✅ Implemented | Unbalanced foes — not CR-perfect (use content-forge for that) |
| Random quest hook | ✅ Implemented | `random-quest` |
| Random feat / spell | ✅ Implemented | Pools + rules-reference overlap |
| Random names (person/place/tavern) | ✅ Implemented | `random-name` |
| Total chaos package | ✅ Implemented | `random-everything` |
| Apply to campaign state | ✅ Implemented | `apply-character`, `apply-world` (destructive — confirm) |
| Custom homebrew tables | ✅ Implemented | `add-table-entry` → `custom_random_tables.json` |
| Roll ledger | ✅ Implemented | `randomizer_ledger.json` per campaign |
| List all tables | ✅ Implemented | `list-tables` |

## Tools & Scripts
Primary: `randomizer.py` — Library: `randomizer_engine.py`, `randomizer_data.py`

```bash
python .grok/skills/dnd-randomizer/scripts/randomizer.py list-tables "My Campaign"
python .grok/skills/dnd-randomizer/scripts/randomizer.py roll-table weather "My Campaign"
python .grok/skills/dnd-randomizer/scripts/randomizer.py random-item "My Campaign" --level 5
python .grok/skills/dnd-randomizer/scripts/randomizer.py random-character --level 3 --multiclass
python .grok/skills/dnd-randomizer/scripts/randomizer.py random-npc "My Campaign"
python .grok/skills/dnd-randomizer/scripts/randomizer.py random-world "My Campaign"
python .grok/skills/dnd-randomizer/scripts/randomizer.py random-encounter --party-level 4
python .grok/skills/dnd-randomizer/scripts/randomizer.py random-quest "My Campaign"
python .grok/skills/dnd-randomizer/scripts/randomizer.py random-feat
python .grok/skills/dnd-randomizer/scripts/randomizer.py random-spell --max-level 3
python .grok/skills/dnd-randomizer/scripts/randomizer.py random-name --type tavern
python .grok/skills/dnd-randomizer/scripts/randomizer.py random-everything "My Campaign" --level 5
python .grok/skills/dnd-randomizer/scripts/randomizer.py apply-character "My Campaign" --level 1
python .grok/skills/dnd-randomizer/scripts/randomizer.py apply-world "My Campaign"
python .grok/skills/dnd-randomizer/scripts/randomizer.py add-table-entry "My Campaign" homebrew "Ancient coin" --weight 5
python .grok/skills/dnd-randomizer/scripts/randomizer.py ledger "My Campaign"
```

### Builtin tables
`weather`, `terrain`, `travel_complication`, `dungeon_feature`, `npc_role`, `quest_hook`, `mundane_item`, `magic_item`, `world_threat`, `government`

## Behavior
- **Chaos vs balanced:** This skill prioritizes surprise. Say *"balanced loot"* to route to loot-generator.
- **Apply commands overwrite** `player_character.json` or world/kingdom state — always confirm with player first.
- **Ledger:** Campaign rolls avoid recent repeats on the same table when `campaign` is provided.
- **Seeds:** Pass `--seed` for reproducible one-shots (demos, testing).
- Keep mobile output ≤8 lines; offer detail on request.

## State & Files
| File | R/W | Contents |
|------|-----|----------|
| `state/randomizer_ledger.json` | W | Recent table roll history |
| `state/custom_random_tables.json` | W | Homebrew weighted tables |
| `state/player_character.json` | W | Via `apply-character` only |
| `state/world_state.json` | W | Via `apply-world` |
| `state/kingdom_state.json` | W | Via `apply-world` |

## Skill Coordination
| Layer | Role |
|-------|------|
| Registry | Intent `random` → this skill; playbooks `chaos-campaign`, `random-session` |
| Orchestrator | Voice phrases *"random item"*, *"surprise me"* → `plan` → randomizer CLI |
| Playbooks | `chaos-campaign`: apply-world → apply-character → random-encounter → random-quest |
| Voice (iOS) | One result per utterance; confirm before `apply-*` |

## Integration
| Skill | Relationship |
|-------|--------------|
| dnd-loot-generator | Balanced, ledger-protected treasure — randomizer for quick chaos drops |
| dnd-content-forge | Balanced encounters — randomizer for weird unbalanced fights |
| dnd-rumor-event-generator | Context-aware rumors — randomizer for generic table events |
| dnd-character-manager | Persistent sheet edits after `apply-character` |
| dnd-npc-personality-weaver | Persist generated NPCs via `npc_manager create` after random-npc |
| dnd-dice-engine | Mechanical transparency for player rolls |
| dnd-utils | State read/write, event logging |

## iOS / Voice Notes
- *"Roll weather"* → `roll-table weather [campaign]`
- *"Random character level five"* → `random-character --level 5`
- *"Surprise me"* → `random-everything` with campaign name if in play
- Never run `apply-character` / `apply-world` without explicit player confirmation

## Example Flow
Player: *"Give me a totally random one-shot setup."*
→ `random-everything` → Grok narrates world + PC + hook in ≤8 lines → **What do you do?**