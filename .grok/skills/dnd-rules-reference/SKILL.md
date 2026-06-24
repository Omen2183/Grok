---
name: dnd-rules-reference
description: Accurate 5e rules clarification including homebrew considerations. Triggers include how does [spell/ability] work, condition rules, advantage/disadvantage, concentration, cover, opportunity attacks, grapple, death saves, action economy. Delivers clear rulings for consistent long-term play. Backend rules_cheatsheet.py for common topics; Grok knowledge for edge cases.
---

# D&D Rules Reference

## When to Use
- Player or DM needs a rules clarification mid-session
- Edge cases: concentration breaks, cover, simultaneous effects
- Homebrew interactions with RAW 5e

**Do not use when:** Rolling dice (dice-engine), tracking combat HP (combat-assistant), or narrative lore (lore-archivist).

## Quick Start (Mobile)
1. Ask **"How does grappling work?"** or **"Does silence break concentration?"**
2. Grok gives a clear ruling with brief RAW citation style.
3. Apply ruling in play via persistent-dm or combat-assistant.

## Capabilities (Honest Matrix)
| Capability | Status | Notes |
|------------|--------|-------|
| 5e rules explanations | ⚠️ Partial | Grok knowledge; no SRD script |
| Homebrew-aware rulings | ⚠️ Partial | Reads campaign notes if present |
| Condition reference | ⚠️ Partial | Narrative; combat-assistant applies conditions |
| Spell/feat lookup by name | ⚠️ Partial | LLM recall; verify for niche content |
| Rules cheatsheet CLI | ✅ Implemented | `rules_cheatsheet.py lookup` for common topics |
| Full automated rules engine | ❌ Not implemented | No complete SRD database |
| Official source page links | ❌ Prompt-only | Summarize in chat |

## Tools & Scripts
```bash
python .grok/skills/dnd-rules-reference/scripts/rules_cheatsheet.py list
python .grok/skills/dnd-rules-reference/scripts/rules_cheatsheet.py lookup concentration
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py load "My Campaign" --file player_character
```

## Behavior
- Lead with the **ruling**, then one-sentence rationale.
- Note when table/homebrew overrides RAW.
- For contested calls: offer both interpretations, recommend one.
- Keep under 6 lines unless player asks *"full detail"*.

## State & Files
| File | R | Purpose |
|------|---|---------|
| `state/player_character.json` | R | Class/features for context |
| `state/world_state.json` | R | Homebrew notes field |

## Integration
- **Called by:** persistent-dm, voice-assistant
- **Feeds into:** combat-assistant (apply conditions), character-manager (features)

## iOS / Voice Notes
- Voice rulings: verdict first, example second.
- Avoid numbered rules subsections aloud — use plain speech.

## Example Flow
Player: *"Can I use a bonus action while surprised?"*
→ Ruling: *"No — surprised creatures can't take actions or reactions on their first turn."*
→ persistent-dm continues combat
→ **What do you do?**