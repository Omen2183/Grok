---
name: dnd-visual-weaver
description: Build consistent image-generation prompts from live campaign state, visual canon, and companion references. Triggers include show me, generate art, what does this look like, image of, visual for this scene, character portrait, kingdom map style. Maintains visual consistency across PCs, companions, and locations.
---

# D&D Visual Weaver

## When to Use
- Player asks to see a scene, character, or location
- Establishing art direction for recurring visuals
- Saving appearance notes to visual canon

**Do not use when:** Pure narration without images (persistent-dm) or rules/mechanics questions.

## Quick Start (Mobile)
1. Say **"What does the throne room look like?"**
2. Grok weaves a prompt from location, weather, PC, and canon.
3. Offer image generation; save new canon when player confirms looks.

## Capabilities (Honest Matrix)
| Capability | Status | Notes |
|------------|--------|-------|
| Prompt weaving from state | ✅ Implemented | `weave-prompt` |
| Visual canon persistence | ✅ Implemented | `state/visual_canon.md` |
| Companion appearance pull | ✅ Implemented | From `important_companion.json` |
| Kingdom mode framing | ✅ Implemented | Settlement-scale shot hints |
| Wounded-state visual cues | ✅ Implemented | Low HP adds battle-worn note |
| Image generation | ⚠️ Partial | Grok image tool; script outputs prompt only |
| 3D models / maps | ❌ Prompt-only | Prompt text only |

## Tools & Scripts
```bash
python .grok/skills/dnd-visual-weaver/scripts/visual_prompt_library.py weave-prompt "My Campaign" "Aria confronts the warlord on the rain-slick battlements" --style "dark fantasy oil painting" --shot "dramatic low angle"
python .grok/skills/dnd-visual-weaver/scripts/visual_prompt_library.py save-canon "My Campaign" "Aria: silver hair, scarred left cheek, green cloak. Whisperwood: bioluminescent fungi."
```

## Behavior
- Read `visual_canon.md` and world state before weaving.
- Present prompt briefly; generate image when requested.
- After player approves, append to canon via `save-canon`.
- Lead with the image or scene hook, not the raw prompt.

## State & Files
| File | R/W | Contents |
|------|-----|----------|
| `state/visual_canon.md` | R/W | Appearance notes |
| `state/world_state.json` | R | Location, weather, mode |
| `state/player_character.json` | R | PC name, HP band |
| `state/important_companion.json` | R | Companion appearance |

## Integration
- **Uses:** dnd-utils state loaders
- **Called by:** persistent-dm at dramatic beats
- **Pairs with:** lore-archivist for location history context

## iOS / Voice Notes
- Voice: describe scene orally first; offer *"Want me to generate an image?"*
- Don't read full prompt aloud — summarize in one sentence.

## Example Flow
→ `weave-prompt "My Campaign" "Moonlit forest clearing"`
→ Generate image from returned prompt
→ Player: *"Yes, keep the blue cloak"*
→ `save-canon` with updated notes
→ **What do you do?**