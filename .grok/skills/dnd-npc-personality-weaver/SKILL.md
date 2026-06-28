---
name: dnd-npc-personality-weaver
description: Create and persist memorable NPCs with personality, speech patterns, secrets, motivations, and relationship scores. v5.3.0 production. Triggers include create NPC, who is [name], NPC personality, update NPC attitude, relationship with [NPC], what does [NPC] know. Makes recurring characters consistent across sessions. Works with any campaign.
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
| Search NPCs | ✅ Implemented | `search` by name substring |
| Update attitude & notes | ✅ Implemented | `update`, `append-note` |
| Relationship score tracking | ✅ Implemented | `adjust-relationship`, `relationship-tier` |
| Generate personality seed | ✅ Implemented | `generate-personality` CLI |
| What NPC knows | ✅ Implemented | `what-knows` reads secrets/notes from JSON |
| Delete NPC | ✅ Implemented | `delete` |
| Auto-generate full backstory | ⚠️ Partial | Grok authors rich fields; CLI stores them |
| Faction-wide NPC simulation | ❌ Prompt-only | Use rumor-event-generator |

## Tools & Scripts
Primary script: `npc_manager.py` — commands: `create`, `update`, `get`, `list`, `adjust-relationship`, `append-note`, `search`, `generate-personality`, `what-knows`, `relationship-tier`, `delete`

```bash
python .grok/skills/dnd-npc-personality-weaver/scripts/npc_manager.py create "My Campaign" --name "Mira Thorn" --personality "Anxious but kind" --speech "Soft, rambles when nervous" --secret "Hiding fugitive brother"
python .grok/skills/dnd-npc-personality-weaver/scripts/npc_manager.py generate-personality "Mira Thorn" --role merchant
python .grok/skills/dnd-npc-personality-weaver/scripts/npc_manager.py list "My Campaign"
python .grok/skills/dnd-npc-personality-weaver/scripts/npc_manager.py search "My Campaign" "Mira"
python .grok/skills/dnd-npc-personality-weaver/scripts/npc_manager.py get "My Campaign" mira-thorn
python .grok/skills/dnd-npc-personality-weaver/scripts/npc_manager.py what-knows "My Campaign" mira-thorn
python .grok/skills/dnd-npc-personality-weaver/scripts/npc_manager.py update "My Campaign" mira-thorn --attitude friendly --note "Party saved her shop"
python .grok/skills/dnd-npc-personality-weaver/scripts/npc_manager.py append-note "My Campaign" mira-thorn "Offered discount on potions"
python .grok/skills/dnd-npc-personality-weaver/scripts/npc_manager.py adjust-relationship "My Campaign" mira-thorn 2 --note "Shared meal"
python .grok/skills/dnd-npc-personality-weaver/scripts/npc_manager.py relationship-tier 25
python .grok/skills/dnd-npc-personality-weaver/scripts/npc_manager.py delete "My Campaign" mira-thorn
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

## Skill Coordination
| Layer | Role |
|-------|------|
| Registry | Intents `create_npc`, NPC queries → this skill |
| Orchestrator | `plan` may chain content-forge NPC seeds → `create` |
| Playbooks | `new-campaign` may seed starting NPCs |
| Voice (iOS) | Roleplay via persistent-dm; relationship changes via voice phrases |

## Integration
- **Uses:** dnd-utils `event_system`, `paths`
- **Called by:** persistent-dm, lore-archivist (read), content-forge (seed NPCs)

## iOS / Voice Notes
- Voice roleplay: distinct speech pattern, shorter sentences.
- Confirm before overwriting an existing NPC profile.
- `what-knows` output: summarize in plain speech, not JSON.

## Example Flow
→ `generate-personality` + `create` with Grok-authored fields
→ Scene: Grok voices Mira, references stored secret only if earned
→ `adjust-relationship ... 3` after quest completion
→ **What do you do?**