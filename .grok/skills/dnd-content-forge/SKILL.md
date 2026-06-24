---
name: dnd-content-forge
description: Use to generate balanced encounters, NPCs, magic items, quests, domain events, construction projects, or faction actions. Triggers include generate encounter, create NPC, random event, kingdom project ideas, generate domain event, create magic item, side quest. Supports 5e + heavy homebrew and works differently depending on tabletop vs kingdom mode.
---

# Dnd Content Forge

## Overview
The creative engine for fresh, campaign-native content. It generates encounters, NPCs, magic items, quests, and kingdom projects that feel like they genuinely belong in *your* campaign. It supports heavy homebrew and intelligently adapts output for both tabletop and kingdom/domain modes. This skill works as a natural creative partner to `dnd-persistent-dm`.

## Mode-Aware Generation

### Tabletop Mode
- Balanced combat encounters appropriate to current party level and resources
- **Full monster/stat block generation** with CR-appropriate scaling, lair actions, legendary actions/resistances, and flavorful homebrew reskinning (new high-priority enhancement)
- Social encounters and NPCs with personality, secrets, and clear motivations
- Exploration locations, traps, puzzles, and random events
- Magic items and loot flavored to your campaign's themes and tone
- Side quests and hooks that can connect to larger plot or kingdom threads

**Monster Generation (Significantly Enhanced — June 2026)**:
- `scripts/generate_monster.py` now features substantially improved 5e-inspired scaling for HP ranges, AC, attack bonuses, damage expressions, and save DCs across CR 0–20+.
- Produces richer generation prompts that yield complete, balanced stat blocks with proper legendary/lair actions where appropriate.
- Includes `suggest_encounter_budget()` for XP budget guidance.
- Automatically provides lore integration notes so important monsters can be recorded via `dnd-lore-archivist`.
- Combines solid rule-based baselines with high-quality LLM generation for flavorful, campaign-native results.
- Enhanced CLI: `python3 generate_monster.py "Campaign Name" --theme "Veil Aberration" --cr 7 --difficulty Hard --encounter`

**Ready-to-Use Monster Generation Prompt Template**:

```markdown
You are an expert D&D 5e monster designer. Create a complete, balanced monster stat block for a [CR or Party Level] encounter in the [Campaign Tone / Theme] campaign.

**Requirements:**
- Party Level: [Insert current party level from character-manager]
- Desired Difficulty: [Easy / Medium / Hard / Deadly]
- Creature Theme: [e.g., Aberration from the Veil, Corrupted Fey, Ancient Construct]
- Include full stat block: AC, HP, Speed, Ability Scores, Saving Throws, Skills, Vulnerabilities/Resistances/Immunities, Senses, Languages, CR, Traits, Actions, Reactions, Bonus Actions, and Legendary/Lair Actions if appropriate.
- Add 1-2 unique flavorful twists or minor homebrew mechanics that fit the campaign.
- Provide a short "Tactics & Roleplay Notes" section.
- Suggest one lair action if this creature has a lair.

Output in clean, ready-to-use Markdown format.
```

**Event Recording**: When generating quests, domain events, or significant content, consider recording them using `record_quest_event()` or `record_event()` so they enter the campaign’s long-term memory.

### Kingdom Mode (Domain Builder)
- Domain events and complications (trade disruptions, faction requests, mysterious events, construction setbacks, espionage)
- Construction and infrastructure project ideas with costs, time, and benefits
- Research or magical project options
- Faction actions and political opportunities or threats
- Military/training developments and defense improvements for your domain or strongholds (if applicable)
- Long-term projects that can award light XP when completed (coordinated with dnd-persistent-dm)

## Behavior Guidelines
- Default to 5e balance frameworks but heavily reskin with your campaign's aesthetic and homebrew elements.
- **Mechanical Scaffolding**: Use `/home/workdir/.grok/skills/dnd-utils/encounter_budgets.md` for XP thresholds by party level when building combat encounters. Use it as a guideline, not a straitjacket.
- **Encounter Simulation / Preview (New Medium-Priority Feature)**: Before finalizing an encounter, optionally run a quick simulated difficulty preview. This uses data from `dnd-character-manager` (party level, HP, key abilities, magic items) to estimate expected challenge (e.g., "This fight is likely Hard for your current party composition, with ~60% chance of at least one player dropping if played aggressively"). Useful for fine-tuning.
- Always tie generated content to existing lore when possible (use dnd-lore-archivist if needed).
- For encounters: Consider terrain, time of day, current kingdom/domain state, and any custom companions if present.
- For kingdom content: Make projects feel meaningful and consequential. Include clear mechanical benefits and narrative flavor. Reference rough cost/time/benefit scaffolding when appropriate.
- Offer 3–5 options when generating, with one highlighted as particularly fitting.
- Include rough difficulty or resource estimates.

## Example Triggers & Output
- "Generate a night encounter near [important location]" → Tabletop-style encounter flavored to your campaign.
- "Create a CR 5 homebrew aberration with lair actions" or "Generate a full stat block for a custom dragon" → Detailed monster with scaled stats, legendary/lair actions, and campaign flavor.
- "Kingdom project ideas for improving harbor defenses" → Several options with approximate costs, time, benefits, and potential XP on completion.
- "Create a suspicious NPC merchant" → Full NPC with appearance, personality, what they know, and possible hooks.

## State & Bootstrap Assumptions
This skill expects the campaign folder structure to exist (created by `dnd-persistent-dm` on first use).  
If files are missing, follow minimal fallback behavior and notify `dnd-persistent-dm`.

## Homebrew Support
Strongly incorporate any custom mechanics, item types, creature themes, or companion systems the player has established in their campaign. This skill is designed to work seamlessly with heavy homebrew.

This skill keeps both modes feeling fresh and alive without requiring you to prep everything yourself.