---
name: dnd-loot-generator
description: Procedural treasure and magic item generation with party-level scaling and a persistent loot ledger to avoid duplicates. v3.2.0 production. Triggers include generate loot, treasure hoard, what's been found, magic item reward, post-combat loot. Supports 5e tone + homebrew campaigns.
---

# D&D Loot Generator

## When to Use
- Post-combat or discovery rewards
- Treasure hoards scaled to party level/CR
- Checking what items the party already found

**Do not use when:** Custom bespoke artifact design with deep lore (content-forge + lore-archivist) or inventory management (character-manager).

## Quick Start (Mobile)
1. After a fight: **"Generate loot for CR 3"**.
2. Grok presents 2–4 items; ledger prevents repeats.
3. Player picks items → character-manager `inventory add`.

## Capabilities (Honest Matrix)
| Capability | Status | Notes |
|------------|--------|-------|
| Weighted item generation | ✅ Implemented | `generate` — mundane, consumable, magic |
| Loot ledger (anti-duplicate) | ✅ Implemented | `state/loot_ledger.json` |
| Ledger summary & search | ✅ Implemented | `summary`, `search-ledger` |
| Table metadata | ✅ Implemented | `tables` |
| Treasure hoard | ✅ Implemented | `hoard` command |
| CR/level scaling | ✅ Implemented | `--cr`, `--level` flags |
| Custom item authoring | ⚠️ Partial | Grok homebrews; tables are generic |
| Magic item balance audit | ❌ Prompt-only | No automated power analysis |

## Tools & Scripts
Primary script: `procedural_loot.py` — commands: `generate`, `ledger`, `hoard`, `summary`, `search-ledger`, `tables`

```bash
python .grok/skills/dnd-loot-generator/scripts/procedural_loot.py generate "My Campaign" --cr 3 --count 4 --type mixed --level 5
python .grok/skills/dnd-loot-generator/scripts/procedural_loot.py hoard "My Campaign" --level 5 --cr 5
python .grok/skills/dnd-loot-generator/scripts/procedural_loot.py ledger "My Campaign"
python .grok/skills/dnd-loot-generator/scripts/procedural_loot.py summary "My Campaign"
python .grok/skills/dnd-loot-generator/scripts/procedural_loot.py search-ledger "My Campaign" "healing"
python .grok/skills/dnd-loot-generator/scripts/procedural_loot.py tables
python .grok/skills/dnd-loot-generator/scripts/procedural_loot.py generate "My Campaign" --type magic --allow-duplicates
```

## Behavior
- Present loot as a short bullet list with rarity hints.
- Note ledger additions silently; don't dump JSON.
- Match tone to campaign (grim, whimsical, high-magic).
- Confirm when player claims an item → route to inventory.

## State & Files
| File | R/W | Contents |
|------|-----|----------|
| `state/loot_ledger.json` | R/W | Items already generated/found |

## Skill Coordination
| Layer | Role |
|-------|------|
| Registry | Post-combat loot intent → this skill |
| Orchestrator | `plan` chains `end-combat` → `generate` or `hoard` |
| Playbooks | `end-combat`: end combat → loot → clear combat state |
| Voice (iOS) | Read 2–3 items per beat; confirm pickups |

## Integration
- **Uses:** dnd-utils paths and JSON helpers
- **Called by:** persistent-dm after `end-combat` playbook
- **Pairs with:** character-manager for pickup/attunement

## iOS / Voice Notes
- Read loot lists slowly in voice; 3 items max per beat.
- *"You find a potion of healing and 40 gold."*
- Use `summary` for quick *"what have we found?"* without full JSON.

## Example Flow
→ `hoard "My Campaign" --level 4 --cr 4`
→ *"Hoard: Potion of Greater Healing, +1 dagger, 120 gp, silk pouch."*
→ Player takes dagger → `inventory add --name "+1 Dagger"`
→ **What do you do?**