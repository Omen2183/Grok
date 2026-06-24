---
name: dnd-npc-personality-weaver
description: Creates rich, memorable NPCs with personality, speech patterns, secrets, motivations, and quirks. Maintains persistence for recurring characters. Makes social encounters and roleplay significantly more engaging and consistent across sessions.
---

# Dnd Npc Personality Weaver

## Overview
Creates vivid, three-dimensional NPCs that feel alive. It generates personality, voice, secrets, and behavioral quirks so roleplay becomes more engaging and memorable for both player and DM.

## When to Activate
- "Generate an NPC" or "Create a suspicious merchant"
- "Make this barkeep more interesting"
- "Give the guard captain a personality"
- "What would this NPC sound like?"

## Core Capabilities
- Generate core personality traits and flaws
- Create distinct speech patterns and verbal tics
- Define surface motivations vs. hidden secrets
- Suggest how the NPC might react to the player
- Add memorable quirks or habits
- Optionally connect them to factions or larger plots

**Python Backend**: `scripts/npc_manager.py` adds persistent storage and relationship tracking so recurring NPCs stay consistent.

## Behavior Guidelines
- Make NPCs feel like real people with goals, flaws, and secrets.
- Balance interesting traits with believability.
- When developing an existing NPC, build on known information rather than contradicting it.
- Offer 2–3 variations when generating so the user has choice.
- Keep descriptions concise but rich enough to be immediately usable.

## Integration
When an NPC becomes recurring or important, record them (including personality, secrets, and relationship notes) using `dnd-lore-archivist` or `dnd-persistent-dm` (or create the file manually if this is the first mention) so they remain consistent across sessions.

## State & Bootstrap Assumptions
This skill expects the campaign folder structure to exist (created by `dnd-persistent-dm` on first use).  
If files are missing, follow minimal fallback behavior and notify `dnd-persistent-dm`.

## Example Output Style
**Name:** Mira Voss, Dockside Fence  
**Personality:** Sharp-tongued, pragmatic, secretly sentimental about old sailors.  
**Speech:** Speaks in short, clipped sentences. Calls people "love" or "pet" sarcastically.  
**Secret:** She’s quietly funneling money to help orphans connected to a past failure.  
**Quirk:** Always fidgets with a silver coin when nervous.  
**Attitude toward the player character:** Wary respect after they helped her once. Would sell them out if the price was high enough.

This skill helps turn random encounters and social scenes into highlights of the session.