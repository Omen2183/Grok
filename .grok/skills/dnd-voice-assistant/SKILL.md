---
name: dnd-voice-assistant
description: Voice execution layer for the D&D skills suite. Triggers include voice mode, play by voice, DM voice, start voice D&D, continue voice campaign. Routes utterances to persistent-dm, combat-assistant, dice-engine, and session-scribe. Parses damage/healing phrases, confirms destructive actions, and formats listenable short replies. Full mechanical parity with text play.
---

# D&D Voice Assistant

## When to Use
- Player enables voice D&D or speaks instead of typing
- Ambiguous combat/dice/session phrases need routing
- Replies must be short and listenable on iOS

**Do not use when:** Player is in text mode (route directly to persistent-dm).

## Quick Start (Mobile)
1. Say **"Start voice D&D"** or **"Play by voice"**.
2. Talk naturally — Grok routes via `route_voice_request`.
3. Confirm destructive actions when prompted (*"Say yes to proceed"*).

## Capabilities (Honest Matrix)
| Capability | Status | Notes |
|------------|--------|-------|
| Voice session detection | ✅ Implemented | `is_voice_session()` |
| Intent routing | ✅ Implemented | `route_voice_request()` |
| Damage phrase parsing | ✅ Implemented | *"Goblin takes 8 damage"* |
| Healing phrase parsing | ✅ Implemented | *"Aria heals 10"* |
| Confirmation gates | ✅ Implemented | end-session, level-up, attune, init |
| Spoken reply formatting | ✅ Implemented | `format_spoken_reply()` |
| Speech-to-text / TTS | ❌ Prompt-only | Platform handles I/O; utils format only |
| Continuous ambient listening | ❌ Prompt-only | Turn-based voice turns |

## Tools & Scripts
```python
# Import helpers (no standalone CLI):
from voice_utils import (
    route_voice_request,
    format_spoken_reply,
    parse_damage_phrase,
    parse_healing_phrase,
    voice_confirm_prompt,
    is_voice_session,
)
```

Example routing:
```python
route_voice_request("Goblin takes 8 damage")
# → primary_skill: dnd-combat-assistant, damage: ("Goblin", 8)
```

Downstream CLIs invoked after routing:
```bash
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py damage "My Campaign" --target "Goblin" --amount 8
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py "1d20+5" --advantage
python .grok/skills/dnd-session-scribe/scripts/session_scribe.py end-session "My Campaign" "Summary here"
```

## Behavior
- **Always route voice through this skill first**, then delegate.
- Replies ≤3 sentences + mechanical line + *"What do you do?"*
- Confirm before: end session, level-up, attune, campaign init, mass resets.
- State changes: speak before → after (*"32 to 24 HP"*).

## State & Files
No direct file I/O — delegates to routed skills. Reads campaign context via persistent-dm.

## Integration
| Intent | Routes to |
|--------|-----------|
| `narrative` (default) | dnd-persistent-dm |
| damage/healing parsed | dnd-combat-assistant |
| `dice_roll` | dnd-dice-engine |
| `end_session` | dnd-session-scribe |
| `combat_action` | dnd-persistent-dm → combat-assistant |

## iOS / Voice Notes
- Avoid bullet lists and markdown in spoken output.
- Spell numbers for clarity on small totals (*"eight damage"*).
- Pause after confirmation questions; wait for *yes/no*.
- Long recaps: offer *"Want the short or full version?"*

## Example Flow
Player (voice): *"I hit the goblin for 8"*
→ `parse_damage_phrase` → combat `damage --amount 8`
→ `format_spoken_reply("Your blade finds its mark.", "Goblin 7 to 0 HP.")`
→ *"What do you do?"*