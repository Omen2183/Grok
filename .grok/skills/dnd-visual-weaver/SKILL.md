---
name: dnd-visual-weaver
description: Use when the player wants visuals, scene descriptions for image generation, or consistent art direction for characters, locations, or kingdom/domain elements. Triggers include show me, generate art, what does this look like, image of, visual for this scene. Maintains visual consistency for your player character(s), custom companions, important locations, and domain elements. Works with any campaign and heavy homebrew.
---

# Dnd Visual Weaver

## Overview
Creates rich, consistent visual prompts and guidance for image generation. It ensures your player character(s), custom companions, important locations, and kingdom elements maintain a coherent visual identity across the entire campaign. This skill is designed to feel native to Grok’s image capabilities while supporting both intimate tabletop moments and larger domain-scale scenes.

**Recent Upgrade**: The skill now includes automated `weave_visual_prompt()` functionality that pulls live state (world, character, companion, health, and proactive suggestions) to dramatically reduce manual scaffolding and enable context-aware, consistent visuals. It can react to meaningful state changes (companion evolution, kingdom milestones, health issues) by suggesting or generating images.

## Core Functions
- Craft detailed, high-quality image prompts tailored to your campaign's aesthetic and themes (including any homebrew elements).
- Maintain visual consistency for recurring elements such as:
  - Your player character(s)
  - Custom companions or bonded creatures (track current appearance/stage if they evolve)
  - Important locations and settlements
  - Recurring NPCs
- Support both modes:
  - **Tabletop mode**: Dramatic scene illustrations, character close-ups, combat moments, exploration.
  - **Kingdom / Domain mode**: Wider establishing shots of developing domains, construction progress, faction gatherings, strategic overviews.

## Behavior
- When the player says "show me", "generate art of", "what does this look like", or describes a scene/character, **load the visual_canon.md** first.
- Maintain `state/visual_canon.md` with consistent descriptors for:
  - Player character(s)
  - Important companions (especially those that evolve over time) — track growth, bond level, and visual changes
  - Recurring locations
  - Overall aesthetic & color palette
- When generating images, prefer using the available `generate_image` tool (or `edit_image` for refinements) with prompts derived from the canon.
- Offer prompt + optional direct image generation.
- Provide variations (cinematic wide shot, dramatic close-up, concept art, in-world illustration style).

**Visual Canon Fallback**

If `state/visual_canon.md` or companion tracking files do not exist:
- Create minimal versions with current known details (especially for recurring elements like custom companions).
- Populate with whatever the player has described in the current conversation.

## Evolving Companion Visual Guidance (Generic)
When a campaign features an important companion that grows or changes over time:
- Reference the current stage/bond/abilities from the companion tracking file (e.g. `important_companion.md` or `companion_state.json`).
- Track visual evolution: size/age stage, distinctive features, bond indicators, environmental effects, etc.
- Maintain consistent descriptors in the visual canon (e.g., scale color, eye glow, presence, silhouette changes).

## Primary Image Generation Engine
**Grok Imagine is the primary and recommended image generation engine** for this skill.

- All visual generation should prefer the `generate_image` tool (powered by Grok Imagine).
- Use `edit_image` for refinements and iterations.
- The `render_generated_image` component should be used in final responses when displaying generated visuals to the player.

## Image Generation Integration (Mandatory Workflow)
Before generating any image, **you must call `weave_visual_prompt()`** (or the CLI `weave-prompt`).

This function **mandatory loads and merges**:
- `world_state.json` (current location, time, weather, mode)
- `player_character.md` / `.json`
- `visual_canon.md` (or the visual_prompt_library.json)
- `important_companion.json` (for evolving companions)

Only after weaving the prompt should you call `generate_image`.

**Kingdom / Domain Mode Visuals**
- Use wide establishing shots for settlements, construction progress, or domain overviews.
- Show faction gatherings, project sites under development, or strategic maps with visual flair.
- Maintain the same character/companion consistency even in kingdom-scale scenes.
- Example prompts: “wide cinematic establishing shot of the growing stronghold at dusk, with construction cranes and watchtowers, [Player Character] and [Companion] in foreground, atmospheric lighting”

**Edit Image Iteration Loop (Tied to State)**
When the player wants refinements:
1. Generate initial image with `generate_image` using a woven prompt.
2. For changes (“make the companion larger”, “add more Celtic knot motifs”, “shift to golden hour lighting”), call `edit_image` on the previous result.
3. **Visual Canon Automation (New High-Priority Feature)**: After any image generation or significant edit, the skill now proactively:
   - Suggests updates to `state/visual_canon.md` with new descriptors (appearance changes, lighting mood, style notes).
   - Offers to auto-apply consistent elements (e.g., "Add 'ethereal blue glow on companion scales' to canon?").
   - Supports basic style-locking by maintaining a preferred art style/palette section in the canon file.
4. Log major visual generations with tags in the campaign log when possible.

**Reference Image & Style Support**: When available on the platform, the weaver can incorporate reference image IDs or style descriptors for stronger consistency across generations.

Example flow:
```bash
python3 /home/workdir/.grok/skills/dnd-visual-weaver/scripts/visual_prompt_library.py weave-prompt "MyCampaign" \
  --scene "confrontation at the ruined watchtower" --focus "Omen the wyrmling"
# Then pass the resulting prompt to generate_image
```

## Example Prompt Structure
"[Your Character Name], a [brief description of appearance/race/class], standing in [important location] at [time of day]. [Custom Companion Name, if any], a [brief description of the companion], nearby. Atmospheric lighting, [campaign art style or mood], detailed, cinematic."

## Mobile Use
Keep prompts concise enough to copy-paste easily into the image generator while still being highly specific.

This skill turns key moments into memorable visuals and helps maintain visual consistency across your campaign, whether it's a single session or a long-running story.