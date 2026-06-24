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
| Exploding dice | ✅ Implemented | `--exploding` flag |
| Campaign roll logging | ✅ Implemented | `--campaign` → `logs/rolls.json` |
| Secret DM rolls | ⚠️ Partial | Grok narrates result; no hidden-channel API |
| 3d physical dice animation | ❌ Prompt-only | Text/JSON output only |

## Tools & Scripts
```bash
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py "1d20+5"
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py "1d20+7" --advantage --campaign "My Campaign"
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py "1d20+3" --disadvantage
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py "4d6kh3"
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py "2d6+4" --exploding
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py "2d10" 
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

## Integration
- **Uses:** dnd-utils `log_roll` (optional)
- **Called by:** persistent-dm, combat-assistant, character-manager (companion initiative)
- **Voice:** voice-assistant routes `dice_roll` intent here

## iOS / Voice Notes
- Voice rolls: speak naturally — *"Roll perception"* → Grok asks modifier if needed.
- Keep result to 2–3 lines on mobile.

## Example Flow
Player: *"I attack with advantage, +8"*
→ `dice_roller.py "1d20+8" --advantage --campaign "My Campaign"`
→ *"**24** to hit (d20: 16, 11 — kept 16). **What do you do?**"*