---
name: dnd-downtime-manager
description: Short and long rests, hit dice spending, and downtime activity logging for D&D campaigns. Triggers include short rest, long rest, spend hit dice, downtime activity, rest status. Integrates with dnd-utils player state and event logging.
---

# D&D Downtime Manager

## When to Use
- Player takes a short or long rest
- Spending hit dice between fights
- Logging crafting, research, or other downtime activities

**Do not use when:** Combat HP tracking (combat-assistant) or session wrap-up (session-scribe).

## Quick Start (Mobile)
1. Say **"We take a short rest"** or **"Long rest at the inn"**.
2. Grok runs the rest backend and confirms HP / hit dice changes.
3. For downtime: **"I spend 3 days crafting"** → logged with outcome.

## Capabilities (Honest Matrix)
| Capability | Status | Notes |
|------------|--------|-------|
| Short rest | ✅ Implemented | Optional `--spend-hd` healing |
| Long rest | ✅ Implemented | Full HP, reset HD spent, clear death saves |
| Downtime activity log | ✅ Implemented | `logs/downtime_log.md` |
| Rest status read | ✅ Implemented | `status` command |
| Spell slot tracking | ⚠️ Partial | Long rest clears conditions only; spell slots are DM/Grok judgment |
| Exhaustion recovery | ⚠️ Partial | Long rest clears Exhaustion condition if present |

## Tools & Scripts
```bash
python .grok/skills/dnd-downtime-manager/scripts/downtime_manager.py short-rest "My Campaign" --spend-hd 2
python .grok/skills/dnd-downtime-manager/scripts/downtime_manager.py long-rest "My Campaign"
python .grok/skills/dnd-downtime-manager/scripts/downtime_manager.py log-activity "My Campaign" "Craft healing potions" --days 3 --outcome "Created 2 potions"
python .grok/skills/dnd-downtime-manager/scripts/downtime_manager.py status "My Campaign"
```

## Behavior
- Confirm HP changes: before → after.
- Long rest assumes safe rest environment unless player says otherwise.
- Downtime activities append to log; Grok narrates outcomes.

## Integration
| Trigger | Delegate from |
|---------|---------------|
| Rest after combat | persistent-dm |
| Character HP | dnd-utils / character-manager |
| Session end | session-scribe |