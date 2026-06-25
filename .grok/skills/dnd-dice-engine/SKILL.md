---
name: dnd-dice-engine
description: Reliable Python dice roller for all D&D actions. Triggers include roll, attack roll, saving throw, ability check, advantage, disadvantage, 4d6 drop lowest, exploding dice. Full 5e notation with transparent results. Works in text and voice. Optional campaign logging to rolls.json.
---

# D&D Dice Engine

## When to Use
- Any mechanical roll: attacks, saves, checks, damage, initiative
- Advantage/disadvantage on d20 tests
- Stat generation (`4d6kh3`) or homebrew exploding dice

**Do not use when:** The player wants a ruling without rolling (rules-reference) or narrative-only outcomes.

## Quick Start (Mobile)
1. Say **"Roll stealth with advantage"** — Grok runs the roller and shows dice.
2. Results appear as: *"Stealth 1d20+7 → 22 (15, 11 kept)."*
3. Add `--campaign` to log rolls for session recaps.

## Capabilities (Honest Matrix)
| Capability | Status | Notes |
|------------|--------|-------|
| Standard notation (2d6+3) | ✅ Implemented | CLI + importable |
| Advantage / disadvantage | ✅ Implemented | Best/worst of 2d20; cancel when both apply |
| Percentile (d100) | ✅ Implemented | Tens + ones dice |
| d3 (homebrew) | ✅ Implemented | ceil(d6/2) |
| Keep highest/lowest (kh/kl) | ✅ Implemented | e.g. `4d6kh3` |
| Exploding dice | ✅ Implemented | `--exploding` flag + per-pool `!` |
| Multi-pool damage | ✅ Implemented | e.g. `1d8+1d6+5` |
| Fudge dice (dF) | ✅ Implemented | -1/0/+1 pools |
| Critical hit doubling | ✅ Implemented | `crit` command |
| Resistance / vulnerability | ✅ Implemented | `--resistance`, `modify-damage` |
| Success counting | ✅ Implemented | `count-successes` for target-number systems |
| Campaign roll logging | ✅ Implemented | `--campaign` → `logs/rolls.json` |
| Secret DM rolls | ⚠️ Partial | Grok narrates result; no hidden-channel API |
| 3d physical dice animation | ❌ Prompt-only | Text/JSON output only |

## Tools & Scripts
Primary script: `dice_roller.py` — commands: `roll`, `initiative`, `parse`, `percentile`, `check`, `attack`, `save`, `history`, `crit`, `count-successes`, `modify-damage`

```bash
# General notation (legacy positional also works: dice_roller.py "1d20+5")
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py roll 1d20+7 --advantage --campaign "My Campaign"
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py roll 4d6kh3 --campaign "My Campaign"
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py roll 2d6+4 --exploding
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py roll 1d8+1d6+5 --campaign "My Campaign"
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py roll 4dF
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py crit 1d8+1d6+4 --multiplier 2
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py count-successes 8d10 --target 8
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py modify-damage 14 --resistance

# 5e-specific rolls
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py check 5 --advantage --dc 15 --campaign "My Campaign"
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py attack 8 --advantage --campaign "My Campaign"
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py save 3 --disadvantage --dc 14
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py initiative 4 --campaign "My Campaign"
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py percentile 0
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py parse 4d6kh3

# Campaign roll log
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py history "My Campaign" --limit 10
```

## Behavior
- Always show notation, individual dice, modifier, and total.
- On adv/disadv, show both d20 values and which was kept.
- Lead with the number; flavor second.
- Never fudge — use the script output.

## State & Files
| File | R/W | When |
|------|-----|------|
| `logs/rolls.json` | W | When `--campaign` is provided |

## Skill Coordination
| Layer | Role |
|-------|------|
| Registry | Intent `dice_roll` / `combat_action` (step 1) → this skill |
| Orchestrator | `plan` adds `--campaign` and follow-up combat damage when attack hits |
| Playbooks | `start-combat` may call `initiative`; combat flow uses `check`/`attack` then combat-assistant |
| Voice (iOS) | `voice_utils plan` → `dice_roller roll` or `attack`/`check`/`save` |

## Integration
- **Uses:** dnd-utils `log_roll` (optional via `--campaign`)
- **Called by:** persistent-dm, combat-assistant, character-manager (companion initiative)
- **Voice:** voice-assistant routes `dice_roll` intent here

## iOS / Voice Notes
- Voice rolls: speak naturally — *"Roll perception"* → Grok asks modifier if needed.
- Keep result to 2–3 lines on mobile.

## Example Flow
Player: *"I attack with advantage, +8"*
→ `dice_roller.py "1d20+8" --advantage --campaign "My Campaign"`
→ *"**24** to hit (d20: 16, 11 — kept 16). **What do you do?**"*