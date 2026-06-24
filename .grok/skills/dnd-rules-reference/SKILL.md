---
name: dnd-rules-reference
description: Accurate 5e rules clarification including homebrew considerations. v3.2.0 production. Triggers include how does [spell/ability] work, condition rules, advantage/disadvantage, concentration, cover, opportunity attacks, grapple, death saves, action economy. Backend rules_cheatsheet.py with 25+ topics; Grok knowledge for edge cases.
---

# D&D Rules Reference

## When to Use
- Player or DM needs a rules clarification mid-session
- Edge cases: concentration breaks, cover, simultaneous effects
- Homebrew interactions with RAW 5e

**Do not use when:** Rolling dice (dice-engine), tracking combat HP (combat-assistant), or narrative lore (lore-archivist).

## Quick Start (Mobile)
1. Ask **"How does grappling work?"** or **"Does silence break concentration?"**
2. Grok runs `search` or `condition` on the cheatsheet, then gives a clear ruling.
3. Apply ruling in play via persistent-dm or combat-assistant.

## Capabilities (Honest Matrix)
| Capability | Status | Notes |
|------------|--------|-------|
| Cheatsheet topic lookup | ✅ Implemented | `rules_cheatsheet.py` + `rules_data.py` (25+ topics) |
| Search rules by keyword | ✅ Implemented | `search` command |
| Condition reference | ✅ Implemented | `condition` command |
| Topic listing | ✅ Implemented | `list`, `topics` |
| Homebrew-aware rulings | ✅ Implemented | `homebrew` reads campaign notes |
| Full 5e explanations (edge cases) | ⚠️ Partial | Grok knowledge beyond cheatsheet |
| Spell/feat lookup by name | ⚠️ Partial | LLM recall; verify for niche content |
| Full automated rules engine | ❌ Not implemented | No complete SRD database |
| Official source page links | ❌ Prompt-only | Summarize in chat |

## Tools & Scripts
Primary script: `rules_cheatsheet.py` — commands: `list`, `topics`, `lookup`, `search`, `condition`, `homebrew`  
Supporting: `rules_data.py` (import-only topic database)

```bash
python .grok/skills/dnd-rules-reference/scripts/rules_cheatsheet.py list
python .grok/skills/dnd-rules-reference/scripts/rules_cheatsheet.py topics
python .grok/skills/dnd-rules-reference/scripts/rules_cheatsheet.py lookup concentration
python .grok/skills/dnd-rules-reference/scripts/rules_cheatsheet.py search grapple
python .grok/skills/dnd-rules-reference/scripts/rules_cheatsheet.py condition prone
python .grok/skills/dnd-rules-reference/scripts/rules_cheatsheet.py homebrew "My Campaign" custom-rest-rules
```

## Behavior
- Lead with the **ruling**, then one-sentence rationale.
- Prefer cheatsheet CLI output when topic exists; supplement with Grok for edge cases.
- Note when table/homebrew overrides RAW.
- Keep under 6 lines unless player asks *"full detail"*.

## State & Files
| File | R | Purpose |
|------|---|---------|
| `state/player_character.json` | R | Class/features for context |
| `state/world_state.json` | R | Homebrew notes field |

## Skill Coordination
| Layer | Role |
|-------|------|
| Registry | Rules questions route here before combat/character changes |
| Orchestrator | `plan` may chain rules lookup → combat `apply-condition` |
| Playbooks | Not a playbook step — on-demand during play |
| Voice (iOS) | Verdict-first spoken rulings; avoid reading markdown lists |

## Integration
- **Called by:** persistent-dm, combat-assistant, voice-assistant
- **Feeds into:** combat-assistant (apply conditions), character-manager (features)

## iOS / Voice Notes
- Voice rulings: verdict first, example second.
- Avoid numbered rules subsections aloud — use plain speech.
- Use `search` backend silently; speak the synthesized ruling.

## Example Flow
Player: *"Can I use a bonus action while surprised?"*
→ `search surprised` or Grok ruling
→ *"No — surprised creatures can't take actions or reactions on their first turn."*
→ persistent-dm continues combat
→ **What do you do?**