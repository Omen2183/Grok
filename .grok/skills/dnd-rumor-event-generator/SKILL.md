---
name: dnd-rumor-event-generator
description: Generates rumors, faction actions, random world events, and downtime developments to keep the campaign world feeling reactive and alive. Especially powerful in kingdom mode and long-running sandbox campaigns.
---

# Dnd Rumor Event Generator

## Overview
Generates rumors, faction actions, random world events, and downtime developments to keep the campaign world feeling dynamic, reactive, and alive. This skill supports long-term campaign health by allowing the world to continue moving and evolving even when the player is not actively engaging it. It is especially valuable in kingdom/domain play and long-running campaigns.

## When to Activate
- "Generate a rumor"
- "What’s happening in the world?"
- "Random event"
- "Faction action"
- "Downtime event"
- "What are people saying in town?"

## Core Capabilities
- Generate rumors (true, partially true, or false)
- Create faction actions and political developments
- Produce random world events (minor to major scale)
- Generate downtime outcomes and complications
- Deliver news that could reasonably reach the player characters

## Behavior Guidelines
- Connect generated content to the current campaign state and ongoing threads when possible.
- Balance immediate/local events with larger developments that can unfold over time.
- Include a mix of opportunities, threats, complications, and flavorful world movement.
- Provide several options so the DM has meaningful choice.
- In Kingdom Mode, prioritize events that affect domain progress, faction dynamics, trade, defenses, or external pressures.
- Support long-term world reactivity so the campaign continues to feel alive and responsive between player actions.

## Integration
Important rumors, faction developments, or world events should be recorded using `dnd-lore-archivist` or `dnd-persistent-dm` (or create the file manually if this is the first mention) so the campaign world stays consistent and feels reactive.

## State & Bootstrap Assumptions
This skill expects the campaign folder structure to exist (created by `dnd-persistent-dm` on first use).  
If files are missing, follow minimal fallback behavior and notify `dnd-persistent-dm`.

## Example Output
**Rumor:** “Word on the docks is that the new watchtower is cursed — three workers have already vanished.”

**Faction Action:** The Shadowveil smugglers are quietly pulling back from the eastern trade routes after recent losses.

**Random Event:** A strange colored mist has been seen rolling in from the [mysterious border or location] at night. Animals are acting strangely.

This skill helps the campaign world feel reactive and alive even when the player isn’t actively adventuring.