---
name: dnd-dice-engine
description: Provides reliable, accurate dice rolling for all D&D actions. Supports full 5e notation, advantage/disadvantage, keep highest/lowest, exploding dice, and homebrew modifiers. Uses a dedicated Python roller for transparency and consistency. Works seamlessly in both text and voice.
---

# Dnd Dice Engine

## Overview
Provides fast, trustworthy, and well-formatted dice rolls for your campaign. Handles classic 5e rolls as well as any homebrew modifiers, custom abilities, or advantage/disadvantage situations that arise in either tabletop or kingdom play.

## When to Activate
Use for any dice resolution:
- Attack rolls, saves, skill checks
- Damage rolls
- Initiative
- Random events
- Advantage / Disadvantage rolls
- Keep highest / lowest rolls (e.g. 4d6kh3)

## Core Behavior
- Use the included `scripts/dice_roller.py` for all rolls when possible. It supports:
  - Standard notation: `1d20+5`, `2d6+3`, `4d6kh3` (keep highest 3), `2d20kl1`
  - Advantage and Disadvantage with clear dual-roll output
  - Keep Highest / Keep Lowest mechanics
  - Basic exploding dice (`--exploding` flag — common homebrew)
  - Modifiers (+ Proficiency, Expertise, cover, etc.)
  - Clear structured JSON output with breakdown of both rolls when using advantage/disadvantage
- **Official D&D Dice Types** supported:
  - Core polyhedral: d4, d6, d8, d10, d12, d20
  - Percentile: d100 or 2d10 (tens + units)
  - Common derived: d3 (d6/2), d2 (even/odd on d20 or coin flip)
- Always present results clearly for mobile:
  - Show the notation
  - List individual rolls + kept/dropped when using keep mechanics
  - Show final total with modifier applied
  - Add brief flavorful commentary when appropriate
- Support homebrew elements and custom modifiers from your character or campaign.

## Output Format Example
**Stealth Check (Advantage)**  
Notation: 1d20+7 (advantage)  
Rolls: [18, 9] → Took higher  
Modifier: +7 (Dex) + 2 (homebrew cloak)  
**Total: 27** — Critical success. You move like living shadow through the market.

## Common Core D&D Modifiers (for context)
When rolling, consider these standard sources:
- **Ability Modifier** (Str, Dex, Con, Int, Wis, Cha)
- **Proficiency Bonus** (+2 to +6 depending on level)
- **Expertise** (double proficiency on certain skills)
- **Advantage / Disadvantage** (situational)
- **Cover** (+2 or +5 to AC on attacks)
- **Magic items, class features, homebrew bonuses**

The engine applies whatever modifiers you specify in the roll request.

## Rules Notes
- Default to 5e + your established homebrew.
- When in doubt about a modifier, ask once and remember via state for the session.
- For contested rolls, roll once for each side and compare (or ask persistent-dm to adjudicate).
- Never fudge rolls unless explicitly requested for narrative reasons.

**Real Invocation (Recommended)**:
Use the dedicated dice roller (now strengthened as part of the shared D&D Python ecosystem):

```bash
python3 /home/workdir/.grok/skills/dnd-dice-engine/scripts/dice_roller.py "1d20+7" --advantage
```

Or import in other Python scripts:
```python
import sys
sys.path.append("/home/workdir/.grok/skills/dnd-dice-engine/scripts")
from dice_roller import roll_dice

result = roll_dice("2d6+3", advantage=True)
print(result)  # Full breakdown JSON
```

The dice roller can optionally log results into a campaign's session state via dnd_state_utils in future extensions.

**Flow**:
Player action → dice-engine (real roll via dice_roller.py) → parse JSON → narrate outcome with breakdown.

Never simulate rolls manually when this skill is available. Always use the real script for fairness and transparency.