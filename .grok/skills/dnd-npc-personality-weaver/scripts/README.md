# dnd-npc-personality-weaver scripts

`npc_manager.py` — persistent NPC storage and relationship tracking.

```bash
python .grok/skills/dnd-npc-personality-weaver/scripts/npc_manager.py create "Campaign" --name "Mira Voss" --personality "Sharp-tongued fence"
python .grok/skills/dnd-npc-personality-weaver/scripts/npc_manager.py list "Campaign"
python .grok/skills/dnd-npc-personality-weaver/scripts/npc_manager.py adjust-relationship "Campaign" mira-voss 1 --note "Helped with the dock dispute"
```