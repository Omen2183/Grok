---
name: dnd-visual-weaver
description: Build consistent image-generation prompts from live campaign state, visual canon, and companion references. v4.0.0 production. Triggers include show me, generate art, what does this look like, image of, visual for this scene, character portrait, kingdom map style. Maintains visual consistency across PCs, companions, and locations.
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
| Kingdom visual prompts | ✅ Implemented | `weave-kingdom` |
| Visual status check | ✅ Implemented | `status` |
| Visual canon persistence | ✅ Implemented | `save-canon`, `append-canon` |
| Companion appearance pull | ✅ Implemented | From `important_companion.json` |
| Kingdom mode framing | ✅ Implemented | Settlement-scale shot hints |
| Wounded-state visual cues | ✅ Implemented | Low HP adds battle-worn note |
| Battle map prompts | ✅ Implemented | `weave-map` from grid combat state |
| Image generation | ⚠️ Partial | Grok iOS image tool; script outputs prompt only |
| 3D models | ❌ Platform | Prompt text only; no 3D asset export |

## Tools & Scripts
Primary script: `visual_prompt_library.py` — commands: `weave-prompt`, `weave-kingdom`, `weave-map`, `save-canon`, `append-canon`, `status`

```bash
python .grok/skills/dnd-visual-weaver/scripts/visual_prompt_library.py weave-prompt "My Campaign" "Aria confronts the warlord" --style "dark fantasy oil painting" --shot "dramatic low angle"
python .grok/skills/dnd-visual-weaver/scripts/visual_prompt_library.py weave-kingdom "My Campaign" --focus "domain overview"
python .grok/skills/dnd-visual-weaver/scripts/visual_prompt_library.py status "My Campaign"
python .grok/skills/dnd-visual-weaver/scripts/visual_prompt_library.py save-canon "My Campaign" "Aria: silver hair, green cloak."
python .grok/skills/dnd-visual-weaver/scripts/visual_prompt_library.py append-canon "My Campaign" "Warlord" "Scarred jaw, black plate" --category generated
python .grok/skills/dnd-visual-weaver/scripts/visual_prompt_library.py weave-map "My Campaign" --style "top-down tactical battle map, grid squares, forest terrain"
```

## Behavior
- Read `visual_canon.md` and world state before weaving.
- Present prompt briefly; generate image when requested (Grok iOS image gen).
- After player approves, append to canon via `save-canon` or `append-canon`.
- Lead with the image or scene hook, not the raw prompt.

## State & Files
| File | R/W | Contents |
|------|-----|----------|
| `state/visual_canon.md` | R/W | Appearance notes |
| `state/world_state.json` | R | Location, weather, mode |
| `state/player_character.json` | R | PC name, HP band |
| `state/important_companion.json` | R | Companion appearance |

## Skill Coordination
| Layer | Role |
|-------|------|
| Registry | Visual/art intents → this skill |
| Orchestrator | `plan` may chain dramatic beats → `weave-prompt` |
| Playbooks | Optional during `kingdom-turn` for domain art |
| Voice (iOS) | Describe orally first; offer image generation |

## Integration
- **Uses:** dnd-utils state loaders
- **Called by:** persistent-dm at dramatic beats
- **Pairs with:** lore-archivist for location history context

## iOS / Voice Notes
- Voice: describe scene orally first; offer *"Want me to generate an image?"*
- Don't read full prompt aloud — summarize in one sentence.
- `status` helps Grok know if canon exists before weaving.

## Example Flow
→ `weave-prompt "My Campaign" "Moonlit forest clearing"`
→ Generate image from returned prompt (Grok iOS)
→ Player: *"Yes, keep the blue cloak"*
→ `append-canon` with updated notes
→ **What do you do?**