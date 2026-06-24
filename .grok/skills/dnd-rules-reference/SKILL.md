---
name: dnd-rules-reference
description: Provides accurate, reliable 5e rules clarification and guidance (including homebrew considerations). Use for conditions, actions, advantage/disadvantage, concentration, cover, object interaction, and edge cases. Delivers clear, defensible rulings that support consistent and fair long-term play.
---

# Dnd Rules Reference

## Overview
A quick-reference skill for accurate 5th Edition rules. Use this when you need to recall or clarify core mechanics so rulings stay consistent and fair.

## When to Activate
- Player asks about a condition or mechanic
- Unsure about a specific rule interaction
- Before making an important ruling
- Common triggers: "What does [condition] do?", "Does this break concentration?", "How does advantage work?"

## Core Rules to Reference Accurately

### Conditions (Key Effects)
- **Blinded**: Can't see, auto-fail sight-based checks, disadvantage on attacks, attacks against you have advantage.
- **Charmed**: Can't attack charmer or target them with harmful effects.
- **Frightened**: Disadvantage on attacks and checks while source of fear is in line of sight.
- **Grappled**: Speed 0. Can't move.
- **Incapacitated**: No actions or reactions.
- **Invisible**: Can't be seen, advantage on attacks, attacks against you have disadvantage (until hidden or condition ends).
- **Paralyzed**: Incapacitated + auto-fail Str/Dex saves, attacks against you have advantage and are crits if within 5 ft.
- **Poisoned**: Disadvantage on attacks and checks.
- **Prone**: Disadvantage on attacks, attacks within 5 ft have advantage. Crawl or stand up costs movement.
- **Restrained**: Speed 0, disadvantage on attacks and Dex saves, attacks against you have advantage.
- **Stunned**: Incapacitated + auto-fail Str/Dex saves, attacks against you have advantage.
- **Unconscious**: Incapacitated + prone + auto-fail checks, attacks against you have advantage and crits within 5 ft.

### Action Economy (Important)
- **One Action** per turn (Attack, Cast a Spell, Dash, Disengage, Dodge, Help, Hide, Ready, Search, Use an Object).
- **One Bonus Action** per turn (only if a feature/spell says so).
- **One Reaction** per round (when triggered).
- **One free object interaction** per turn (draw/stow weapon, open door, etc.). Additional interactions usually cost an action.

### Advantage & Disadvantage
- Roll two d20s, take the higher (advantage) or lower (disadvantage).
- They cancel each other out if both apply.
- Multiple sources don't stack — you either have it or you don't.

### Concentration
- Only one concentration spell at a time.
- Taking damage requires a Constitution saving throw (DC = 10 or half damage taken, whichever is higher).
- Incapacitated, killed, or unconscious ends concentration.

### Cover
- **Half Cover**: +2 AC and Dexterity saves.
- **Three-Quarters Cover**: +5 AC and Dexterity saves.
- **Full Cover**: Can't be targeted directly.

### Homebrew & Edge Cases (Production Guidance)

When running heavy homebrew or custom rules, follow these principles:

**General Philosophy**
- Default to official 5e rules unless the homebrew is explicitly established in the campaign.
- When homebrew conflicts with RAW, clearly state the ruling and why.
- Keep homebrew consistent across sessions — record important rulings in `state/world_state.json` or a dedicated `homebrew_rules.md` file.

**Common Homebrew Edge Cases**

- **Custom Companions / Familiars / Mounts**: Treat them as controlled by the player but give them their own initiative in combat. They usually act on the player's turn unless specified otherwise.
- **Custom Magic Items**: Clarify attunement, charges, and whether effects require concentration or bonus actions.
- **Homebrew Feats / Subclasses**: Ask for the exact text once, then remember it. When in doubt, default to the most balanced interpretation.
- **Legendary Actions / Lair Actions on Custom Monsters**: Use sparingly. Make sure they have clear triggers and recharge mechanics.
- **Advantage/Disadvantage Stacking**: Multiple sources do **not** stack. You either have advantage, disadvantage, or neither.
- **Critical Hits on Homebrew**: Confirm whether extra dice or effects apply on crits.
- **Death Saves with Homebrew Healing**: Be explicit about whether magical healing resets death saves or just stabilizes.

**Recommended Approach**
1. When a homebrew rule comes up, ask the player for the exact wording once.
2. Record it in state or a dedicated file.
3. Apply it consistently.
4. If it creates balance issues later, discuss adjustments openly rather than silently changing it.

This section helps maintain fairness and consistency when the campaign uses significant homebrew content.

- **Half cover**: +2 AC and Dex saves.
- **Three-quarters cover**: +5 AC and Dex saves.
- **Full cover**: Can't be targeted directly.

## Usage
When a rules question comes up, give a clear, concise answer based on standard 5e rules, then note any common house rule variations if relevant. Prioritize fairness and consistency.

**Dynamic Query Approach (Recommended):**
- For complex or homebrew interactions, load current campaign state first.
- Ask clarifying questions once, then record the ruling in `state/homebrew_rules.md` or world_state.json so it persists.
- Re-use recorded rulings in future sessions.

## Expanded Edge Cases & Homebrew Guidance (June 2026)

### Concentration & Multiple Effects
- Only one concentration spell at a time.
- Taking damage while concentrating: Constitution save DC = 10 or half damage (whichever is higher).
- Incapacitated, unconscious, or killed ends concentration immediately.
- Homebrew: Some items or feats may allow "maintaining concentration on two spells" — this should be explicitly recorded as a house rule.

### Object Interaction & Environment
- One free object interaction per turn (draw/stow weapon, open door, pick up item).
- Using an object that requires an action (e.g., drinking a potion in combat, activating a lever) costs your Action.
- Homebrew "quick draw" or "fast hands" features should specify whether they grant a free interaction or a bonus action.

### Advantage / Disadvantage & Stacking
- Multiple sources of advantage do **not** stack — you either have advantage or you don't.
- Same for disadvantage.
- Homebrew abilities that "grant advantage on all attacks" should still follow this (they simply provide advantage).

### Death Saves & Healing
- Healing a creature at 0 HP with magical healing greater than their max HP stabilizes them and restores hit points.
- Healing that brings them above 0 HP ends death saves.
- Homebrew: Some effects "reset death saves on a successful save" — record this explicitly.

### Cover
- Half cover: +2 AC and Dexterity saving throws.
- Three-quarters cover: +5 AC and Dexterity saving throws.
- Full cover: Cannot be targeted directly by attacks or spells that require a target you can see.
- Homebrew "improved cover" or terrain features should specify the exact bonus.

### Legendary & Lair Actions (Homebrew Monsters)
- Legendary actions are usually available at the end of another creature's turn.
- Lair actions happen on initiative count 20 (losing ties).
- When creating homebrew legendary creatures, clearly define:
  - How many legendary actions they can take per round
  - What options they have
  - Any recharge or limitation

**Homebrew Conflict Resolution Principle**
When homebrew conflicts with RAW:
1. State the ruling clearly.
2. Explain the reasoning (balance, fun, narrative).
3. Record it so it can be referenced consistently later.
4. Be willing to revisit if it causes problems.

This skill is evolving toward more dynamic, state-aware rulings. For very complex interactions, it may suggest recording the specific ruling in campaign state.

This skill helps keep DM rulings accurate and defensible across long campaigns.