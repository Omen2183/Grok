---
name: dnd-loot-generator
description: Generates balanced, flavorful magic items and treasure hoards tailored to campaign tone and party level. Maintains a persistent "already found" ledger to avoid repetition. Supports heavy homebrew and feels like natural campaign rewards.
---

# Dnd Loot Generator

## Overview
Generates balanced, flavorful magic items and treasure hoards appropriate to the campaign tone and party level. This skill helps make rewards feel meaningful, memorable, and connected to the world, supporting long-term player investment and campaign health.

## When to Activate
- "Generate loot"
- "What’s in the chest?"
- "Create a magic item"
- "Random magic item"
- "Treasure hoard"

## Core Capabilities
- Generate individual magic items with flavor and minor mechanics
- Create small loot parcels and full treasure hoards
- Suggest items appropriate to party level and campaign tone
- Include gold, gems, and art objects for complete rewards

**Python Backend**: `scripts/procedural_loot.py` provides weighted generation, CR/level scaling, and a persistent "already found" ledger so the same powerful items aren't repeated across the campaign.

## Behavior Guidelines
- Follow general 5e guidelines for appropriate power level and rarity.
- **Mechanical Scaffolding**: Use `/home/workdir/.grok/skills/dnd-utils/loot_guidelines.md` for suggested rarity by party level, rough treasure values, and campaign flavor guidance. Treat as helpful reference, not strict rules.
- Add flavorful descriptions and minor unique twists to make items feel special and memorable.
- When relevant, connect items to campaign themes, factions, or ongoing story threads.
- Offer multiple options when generating so the DM has meaningful choice.
- Provide complete, satisfying rewards that include gold, gems, art objects, and magic items.

## Integration
Notable or story-relevant magic items should be recorded using `dnd-persistent-dm` (or create the file manually if this is the first mention) so they persist and can generate future consequences or hooks.

## State & Bootstrap Assumptions
This skill expects the campaign folder structure to exist (created by `dnd-persistent-dm` on first use).  
If files are missing, follow minimal fallback behavior and notify `dnd-persistent-dm`.

## Example Output
**Item:** [Campaign-themed Cloak]  
**Rarity:** Uncommon  
**Description:** A dark gray cloak that seems to drink in light. While wearing it, you have advantage on Dexterity (Stealth) checks made in dim light or darkness.  
**Twist:** The cloak occasionally whispers faint, unintelligible words at night (or another flavorful minor effect fitting your campaign).

This skill helps treasure feel exciting and campaign-appropriate instead of generic.