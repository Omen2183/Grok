---
name: dnd-npc-personality-weaver
description: Create and persist memorable NPCs with personality, speech patterns, secrets, motivations, and relationship scores. Triggers include create NPC, who is [name], NPC personality, update NPC attitude, relationship with [NPC]. Makes recurring characters consistent across sessions. Works with any campaign.
---

# D&D NPC Personality Weaver

## When to Use
- Introducing a recurring NPC worth remembering
- Roleplay scenes needing consistent voice and secrets
- Tracking attitude/relationship changes after player actions

**Do not use when:** Deep world lore queries (lore-archivist) or one-scene throwaway extras (persistent-dm inline).

## Quick Start (Mobile)
1. Meet someone important → **"Remember this NPC — Mira, nervous herbalist"**.
2. Grok creates a profile and speaks in her voice during scenes.
3. After major events → **"Mira trusts us more"** → relationship adjusted.

## Capabilities (Honest Matrix)
| Capability | Status | Notes |
|------------|--------|-------|
| Create NPC record | ✅ Implemented | `npcs/{id}.json` + index |
| List / get NPCs | ✅ Implemented | `list`, `get` |
| Update attitude & notes | ✅ Implemented | `update` |
| Relationship score tracking | ✅ Implemented | `adjust-relationship` |
| Auto-generate personality | ⚠️ Partial | Grok authors fields; CLI stores them |
| NPC knowledge graph | ❌ Prompt-only | No automated "what does NPC know" engine |
| Faction-wide NPC simulation | ❌ Prompt-only | Use rumor-event-generator |

## Tools & Scripts
```bash
python .grok/skills/dnd-npc-personality-weaver/scripts/npc_manager.py create "My Campaign" --name "Mira Thorn" --personality "Anxious but kind" --speech "Soft, rambles when nervous" --secret "Hiding fugitive brother"
python .grok/skills/dnd-npc-personality-weaver/scripts/npc_manager.py list "My Campaign"
python .grok/skills/dnd-npc-personality-weaver/scripts/npc_manager.py get "My Campaign" mira-thorn
python .grok/skills/dnd-npc-personality-weaver/scripts/npc_manager.py update "My Campaign" mira-thorn --attitude friendly --note "Party saved her shop"
python .grok/skills/dnd-npc-personality-weaver/scripts/npc_manager.py adjust-relationship "My Campaign" mira-thorn 2 --note "Shared meal"
```

## Behavior
- Load NPC JSON before speaking as them.
- Show relationship changes: *"Mira: neutral → friendly (+2)."*
- Keep dialogue ≤4 sentences on mobile; embed quirk.
- Never reveal secrets unless discovered in play.

## State & Files
| File | R/W | Contents |
|------|-----|----------|
| `npcs/index.json` | R/W | NPC id/name index |
| `npcs/{id}.json` | R/W | Full NPC profile |
| `logs/events.json` | W | Create/update events |

## Integration
- **Uses:** dnd-utils `event_system`, `paths`
- **Called by:** persistent-dm, lore-archivist (read), content-forge (seed NPCs)

## iOS / Voice Notes
- Voice roleplay: distinct speech pattern, shorter sentences.
- Confirm before overwriting an existing NPC profile.

## Example Flow
→ `create` with Grok-generated personality fields
→ Scene: Grok voices Mira, references stored secret only if earned
→ `adjust-relationship ... 3` after quest completion
→ **What do you do?**