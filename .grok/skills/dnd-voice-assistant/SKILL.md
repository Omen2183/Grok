---
name: dnd-voice-assistant
description: The native voice execution layer for the full D&D skills suite. Enables complete, high-fidelity D&D campaigns entirely through voice with minimal to no noticeable difference compared to text-driven play. Provides seamless routing to dnd-persistent-dm (core engine), voice-optimized input handling, listenable narration, robust ambiguity resolution, and confirmation protocols that preserve full mechanical accuracy and persistent state. The goal is true modality parity: same campaign state, same tools, same reliability — only the input/output method changes. Trigger automatically in voice conversations or when user requests voice mode / spoken D&D. Supports 5e + heavy homebrew.
---

# D&D Voice Assistant — Native Voice Execution Layer

This skill is the **native voice execution layer** for the entire D&D skills suite. Its mission is to deliver a voice experience with **true modality parity** — little to no noticeable difference in capability, state, or mechanical fidelity compared to text play.

You get the full power of `dnd-persistent-dm`, `dnd-combat-assistant`, `dnd-dice-engine`, `dnd-character-manager`, and every supporting tool, with identical persistent state and long-term continuity. The only intentional differences are presentation (listenable narration) and input method (spoken vs. typed).

**Core Principle**: Voice is a first-class modality. The voice layer handles natural language understanding, ambiguity resolution, listenable formatting, and conversational confirmations. All state management, rules adjudication, world reactivity, and tool usage route through the same robust systems used in text. The suite must feel seamless regardless of how the player chooses to engage.

## When to Activate
- User says “use voice mode”, “voice bridge”, “talk me through this”, “voice D&D”, “spoken session”, or similar.
- User is actively in Grok’s voice conversation mode and issuing D&D commands.
- Hybrid sessions where the majority of play is spoken but mechanical precision is still required.
- Any time natural spoken language needs to be translated into precise calls to dnd-persistent-dm, dnd-combat-assistant, dnd-dice-engine, dnd-character-manager, or other skills.
- When the user wants flavorful spoken narration while still maintaining accurate campaign state.

## Design Goal: Near-Zero Difference Between Voice and Text Campaigns

The explicit goal of this skill is **modality parity**:

- A campaign started or played in voice can be continued seamlessly in text (and vice versa) with identical state and history.
- All mechanical systems (combat tracking, dice, character progression, loot, lore, kingdom/domain) function at full fidelity.
- The player does not need to adapt their playstyle or accept reduced capability when switching to voice.
- The only intentional differences are presentation (listenable narration) and input method (spoken vs typed).

## Overview & Positioning
This skill acts as a **smart voice frontend** to the full D&D suite, with `dnd-persistent-dm` as the core engine. It:

- Accepts natural spoken language and intelligently routes it to `dnd-persistent-dm` or the appropriate supporting skill.
- Applies voice-specific preprocessing (normalization, intent clarification) and postprocessing (listenable formatting, structured confirmations).
- Guarantees that every significant state change flows through the same persistent systems used in text play.
- Maintains full access to proactive DMing, world reactivity, and all automation patterns from the rest of the suite.

## Core Capabilities (Native Execution)
- **Full-suite routing**: Natural spoken commands are translated and executed through `dnd-persistent-dm` and **all supporting skills** (combat-assistant, character-manager, visual-weaver, content-forge, loot-generator, lore-archivist, npc-personality-weaver, dice-engine, session-scribe, rules-reference, and the high-level convenience functions in dnd-utils) with the same depth and automation as text play.
- Voice mode has full access to high-level functions such as `perform_kingdom_turn`, `get_campaign_suggestions`, `run_health_check`, `quick_status`, and `safe_init_campaign`.
- **Voice-optimized dual delivery**: Every response includes flavorful spoken narration + clear mechanical summary, formatted for easy listening.
- **Robust ambiguity & transcription handling**: Multi-turn clarification that keeps momentum while protecting mechanical accuracy.
- **Voice-native confirmation protocols**: Structured but conversational confirmation flows for combat actions, HP changes, character updates, and other state changes — designed to feel natural while maintaining precision.
- **Complete modality parity**: Same persistent state files, same dice engine, same combat tracker, same character manager, same event logging, same proactive suggestions, same health checks, and same visual consistency tools. No capability is sacrificed in voice.
- **Proactive & intelligent in voice**: The voice layer can surface campaign suggestions, health status, and intelligently offer visual or narration moments, matching the text experience.
- **Seamless campaign continuity**: Voice sessions write to the exact same campaign folders and state as text sessions. You can freely switch between voice and text mid-campaign.
- Consistent NPC personalities and proactive world behavior even in fully spoken play.

## Current Maturity & Stabilization Pass (May 2026)

The `dnd-voice-assistant` skill has undergone extensive iterative strengthening, official rules integration (Basic Rules + Xanathar’s Guide to Everything), and multiple stabilization passes. 

**Core voice suite is now considered feature-complete for primary campaign use**, including:
- Deep combat parsing (reactions, concentration, class features, two-weapon fighting, **object interaction & environment parsing**)
- Full guided flows for leveling, multiclassing, spell preparation, long rests, and downtime
- Robust Exploration & Social pillars with official mechanics + **stronger Social Intrigue, faction maneuvering, and recurring NPC support**
- Complete Magic Item economy (buying + selling with negotiation and complications)
- Kingdom / Domain mode support
- Automatic dice rolling + strong ambiguity handling
- **Tighter proactive integration with dnd-visual-weaver** for scene visuals during exploration, purchases, victories, etc.
- Consistent recovery/undo across all flows

All new capabilities are properly backed by dedicated, well-documented Python helpers in `voice_utils.py` (including cleanup of legacy duplicate code).

Remaining edge cases are minor (very obscure homebrew interactions or extremely long multi-step kingdom projects). The system is stable and ready for extended voice campaigns with high fidelity to text play.

## Recommended Behavior & Protocols (Voice-Native Play)

### General Voice Session Rules
- Treat voice as a fully capable primary interface. Route the vast majority of play through natural spoken commands to `dnd-persistent-dm`.
- Always deliver **both** immersive narration **and** a clear mechanical recap in every response.
- Use conversational confirmation patterns that feel natural while protecting accuracy on state changes.
- Keep the experience flowing. Only fall back to text suggestions for truly complex multi-step edits or when the player explicitly wants visual precision (e.g., detailed maps).
- Every state change is recorded in the same persistent campaign state used by text play.

### Combat Flow in Voice (Strengthened)
Combat in voice uses the exact same `dnd-combat-assistant` + `dnd-dice-engine` backend as text play for full mechanical fidelity.

**Turn Structure (Voice-Optimized)**
1. **Start of Combat**: Player says “Start combat”, “Roll initiative”, or similar → System rolls initiative via dice engine, presents clear spoken turn order.
2. **During Combat**:
   - Clearly announce whose turn it is + brief status (“It’s your turn. You have 34/45 HP and are concentrating on Bless.”)
   - Player describes action naturally (“I attack the orc with my longsword with advantage”)
   - System uses `detect_intent()` + `parse_combat_action()` to interpret, then executes.
   - Deliver result in flavorful + mechanical form.
3. **Between Turns**: Player can say “Next turn”, “Show status”, “Who’s turn is it?”, or describe full actions.
4. **End of Combat**: Automatic summary, handoff to persistent state, optional loot via `dnd-loot-generator`, and cleanup.

**Recommended Voice Combat Commands**
- “I attack the nearest goblin with my shortsword”
- “I cast Fireball on the group of enemies”
- “I cast Eldritch Blast at the cultist”
- “I cast Bless on the party”
- “Attack with advantage”
- “Next turn” / “End my turn”
- “Show combat status” / “How’s everyone doing?”
- “Apply 12 damage to the ogre”

Use the enhanced `parse_detailed_combat_action()` (recommended), along with `parse_combat_action()`, `detect_intent()`, and `build_voice_confirmation()` from `voice_utils.py` to improve interpretation accuracy.

**New in v4 Combat Parsing** (Latest):
- **Concentration tracking across turns** via `create_combat_context()` + `update_concentration()` + `prompt_concentration_check()` — remembers who is concentrating on what and can prompt for checks when they take damage.
- **Expanded reaction detection** via `expand_reaction_detection()` — now includes Sentinel, War Caster, Uncanny Dodge, in addition to Counterspell, Shield, and Opportunity Attack.
- **Help action** detection.
- **Cover** detection (half cover / three-quarters cover) with mechanical notes.
- Two-weapon fighting, Ready actions, Grapple/Shove, and condition support carried forward.
- Overall combat intent parsing continues to get stronger for voice play.

### Spellcasting in Voice (Improved Handling)
Spellcasting is now better supported with dedicated parsing.

**How it works**:
- Player says something like “I cast Fireball on the group of orcs” or “I cast Eldritch Blast at the cultist”.
- System uses `detect_intent()` + the new `parse_spell_cast()` function to extract:
  - Spell name (when recognized)
  - Target
  - Whether it requires a saving throw + which ability
  - Concentration notes
- The system then routes to the appropriate combat/dice logic and delivers both flavorful narration and mechanical outcome.

**Recommended Voice Spell Patterns**:
- “I cast Fireball centered on the ogre”
- “I cast Healing Word on the downed fighter”
- “Cast Eldritch Blast at the nearest enemy”
- “I cast Bless on myself and my allies”
- “Counterspell the enemy wizard”

For very complex or homebrew spells, the system may ask for clarification or suggest a quick text confirmation.

### Dice & Mechanics in Voice (Campaign Default — Auto-Roll Preferred)
**Updated default behavior (May 2026, per user preference):**

- The skill suite **defaults to auto-rolling** for the player using `dnd-dice-engine`.
- On the **very first roll** of a session (or when first needed), the system performs a **one-time preference check**:  
  “Would you like me to auto-roll that for you, or would you prefer to roll manually?”
- After the player chooses, that preference is respected for the rest of the session (and can be stored at campaign level via `dnd-persistent-dm` for persistence across sessions and voice conversations).
- Only if the player explicitly requests manual rolling (“I’ll roll it myself”, etc.) will it switch to asking for the result.
- This is now the enforced default in `should_auto_roll()` in `voice_utils.py`.
- Results are always returned in flavorful spoken form first, followed by mechanical clarity.
- Full support for advantage/disadvantage, modifiers, and homebrew rules.

### Exploration, Social & World Interaction (Deepened with Official 5e Rules)

This section now incorporates detailed mechanics from the **D&D Basic Rules (Chapter 8: Adventuring)** and **Xanathar's Guide to Everything** downtime activities for richer voice play.

#### Exploration Pillar in Voice (Travel, Foraging, Navigation)
Voice now supports structured exploration flows drawn directly from official rules:

**Travel Paces (Basic Rules):**
- **Fast Pace**: 30 miles/day. -5 to passive Wisdom (Perception). Good for speed, risky for missing threats.
- **Normal Pace**: 24 miles/day. Standard.
- **Slow Pace**: 18 miles/day. +5 bonus to Wisdom (Survival) checks for navigation/foraging in some interpretations; better for stealth and careful movement.

**Voice Commands Supported:**
- “We travel at a slow pace while foraging.”
- “Set a normal travel pace and have the ranger navigate.”
- “Fast pace today, we’re in a hurry.”

**Foraging (Basic Rules + DMG guidance):**
- Character makes Wisdom (Survival) check.
- Success: Roll 1d6 + Wisdom modifier for pounds of food and same for gallons of water found.
- Can be done while traveling at normal or slow pace.

**Navigation & Getting Lost:**
- Navigator makes Wisdom (Survival) check vs. terrain DC (DM sets or standard wilderness table).
- Success: Party stays on course.
- Failure: Risk of getting lost (DM determines consequences, often 1d6 hours or encounter).

**Difficult Terrain**: Movement costs double (each foot costs 2 feet of speed).

**Guided Exploration Flow Example**:
Player describes travel plans → System confirms pace + activities (forage/navigate/track) → Rolls relevant checks via dice engine → Narrates results + any encounters or discoveries.

**Activities While Traveling (Expanded Voice Support)**
From Basic Rules / DMG, characters can perform specific tasks during travel:

- **Navigate**: Wisdom (Survival) — prevents getting lost.
- **Track**: Wisdom (Survival) — follow creatures or find signs.
- **Forage**: Wisdom (Survival) — as above.
- **Draw a Map**: Intelligence check or automatic if proficient with cartographer’s tools.
- **Keep Watch** / **Scout Ahead**: Perception or Stealth.
- **Other**: Pray, study a spellbook (with risk), etc.

Voice now recognizes commands like:
- “While traveling, have the ranger track any signs of the cultists.”
- “I want to draw a map of the route as we go.”
- “Scout ahead while we travel at a slow pace.”

The system can assign the appropriate character to the task and roll automatically in voice mode.

**Random Encounters During Travel**
The voice layer can proactively surface random encounters appropriate to the terrain (forest, road, swamp, etc.) when the party travels.

- System maintains simple encounter chance per day/segment of travel.
- When triggered, it presents a short, voice-friendly description and asks how the party wants to handle it (avoid, fight, talk, sneak, etc.).
- Example: “As you travel through the dense forest, you hear rustling ahead. Three wolves are scavenging a carcass and haven’t noticed you yet. What do you do?”

This keeps long travel segments from feeling empty while staying fully playable in voice.

#### Social Interaction Pillar (Nuanced Voice Handling)
From Basic Rules and core PHB/DMG principles:

**NPC Attitudes** (core framework):
- **Friendly**: Predisposed to help. Easier Persuasion, lower DCs.
- **Indifferent**: Neutral. Standard checks.
- **Hostile**: Inclined to hinder or attack. Intimidation may work but risks escalation; Persuasion harder.

**Voice-Native Social Flow**:
1. Player describes approach or speaks in character (“I approach calmly and say…” or “I try to intimidate him”).
2. System assesses initial attitude (from context/lore) and any modifiers from roleplay.
3. If check needed: Charisma (Persuasion / Deception / Intimidation) vs. Wisdom (Insight) contest or fixed DC based on attitude.
4. Success can shift attitude (e.g., Indifferent → Friendly).
5. Contested checks handled naturally: “Make a Charisma (Deception) check contested by their Wisdom (Insight).”

**Nuance Added**:
- Strong emphasis on roleplay first (“What do you say to the guard?”).
- Multiple checks or shifting attitudes over conversation.
- Insight to read NPC motives/attitudes before committing.
- Complications possible (e.g., failed Intimidation makes them hostile).

This makes social encounters feel alive and mechanical without being robotic.

**Advanced Social Intrigue, Faction Maneuvering & Recurring NPCs (New Strengthened Support)**

The voice layer now has dedicated parsing via `parse_social_intrigue()` in `voice_utils.py` for longer-term social play:

- **Faction Maneuvering**: Detects commands involving faction standing, diplomacy, guild work, court intrigue, or “improving our relationship with the [Faction]”. Tracks attitude shifts and can suggest or record changes via persistent state / `dnd-lore-archivist`.
- **Recurring NPCs**: Heuristics to flag interactions with known/repeated characters (“the merchant”, “Captain Veyra”, “our contact”). Encourages consistent personality and memory across sessions. Strongly recommends pairing with `dnd-lore-archivist` for deep NPC knowledge, secrets, and relationship tracking.
- **Attitude Work & Goals**: Distinguishes Persuasion (win over), Deception (mislead), Intimidation (coerce), Insight (read), and Information Gathering. Supports multi-step social “projects” (e.g., slowly turning a hostile noble into an ally over several downtime periods).
- **Voice Flow Example**:
  > Player: “I want to work on improving our standing with the Thieves’ Guild this week. I’ll spend time schmoozing with my contact, the old fence.”
  > System: Parses as faction maneuvering + recurring NPC. Offers guided steps or simple attitude/progress tracking. Can combine with downtime activity.

This turns social play from one-off checks into meaningful, trackable campaign threads — fully usable in pure voice.

#### Downtime & Economy — Magic Item Buying & Crafting (Major Deep Dive from Xanathar's Guide to Everything)

**Buying a Magic Item (Full XGtE Rules Integrated)**

This is now a robust guided voice flow.

**Core Mechanics (Official XGtE)**:
- Minimum: **1 workweek** + **100 gp** in expenses to seek a seller.
- Make a **Charisma (Persuasion)** check.
- **Bonuses**: +1 for each additional workweek beyond the first, +1 for each additional 100 gp spent on the search (maximum total bonus +10).
- The check total determines which **Magic Item Tables** the system/DM rolls on for available items (higher = better tables).
  - Example mapping (standard XGtE):
    - 1–5: 1d6 rolls on Table A
    - 6–10: 1d4 on Table B
    - 11–15: 1d4 on Table C
    - 16–20: 1d4 on Table D (plus lower)
    - Higher results unlock Tables E–H/I and permanent items.
- Player can always choose to take a **lower result** for more affordable/available items.
- For a **specific item**: Uncommon typically requires Persuasion 10+, rarer items higher DCs or DM adjudication.
- Prices: Use standard rarity guidelines (DMG/XGtE). Consumables are half price. Rough benchmarks: Common ~100 gp, Uncommon ~500 gp, Rare ~5,000 gp, Very Rare ~50,000 gp (exact negotiated or table-driven).
- After finding items, player chooses what to buy (1 permanent or up to 2 consumables usually).

**Guided Voice Buying Flow**:
System walks through: Decide how many extra workweeks/gold to invest → Roll Persuasion (auto or manual) → Present available items from appropriate tables → Confirm purchase and deduct gold → Record in inventory via character manager.

Complications optional for spice.

**Magic Item Purchase Complications (from Xanathar's Guide to Everything)**
To add tension and roleplay hooks, the system can roll on (or narrate from) the official complications table when appropriate:

- On a d20 roll of 1–2 (or DM fiat), a complication occurs.
- Then roll d12 on the Magic Item Purchase Complications table:

| d12 | Complication |
|-----|--------------|
| 1   | The item is a fake, planted by an enemy or rival. |
| 2   | The seller is actually a front for thieves or a con artist. |
| 3   | The item carries a hidden curse or has a dark history that attracts trouble. |
| 4   | A rival buyer or collector learns of the deal and tries to outbid or sabotage you. |
| 5   | The item requires a secret quest or service to “unlock” its full power (or to appease its previous owner’s spirit). |
| 6   | Thieves or assassins target you after the purchase becomes known. |
| 7   | The seller demands an additional favor or dangerous task as part of the deal. |
| 8   | The item was stolen; its original owner (or their allies) may come looking for it. |
| 9   | A local authority or guild learns of the transaction and wants a cut or to regulate it. |
| 10  | The item has a hidden flaw that only reveals itself later. |
| 11  | You accidentally attract the attention of a powerful entity (fey, fiend, or celestial) interested in the item. |
| 12  | The deal draws unwanted attention from a criminal syndicate or spy network. |

These complications integrate into the voice flow as narrative hooks or short side encounters that can be roleplayed or resolved with checks.

**Price Negotiation in Voice**
After items are presented, the player can attempt to haggle:
- “I try to negotiate a better price on that Ring of Protection.”
- System prompts a Charisma (Persuasion) or Wisdom (Insight) check.
- Success: Reduce price by 10–25% (or unlock a small bonus). Failure: Price stays the same or seller becomes slightly annoyed (minor attitude shift).
- This is fully voice-supported and uses the same confirmation + undo system.

**Kingdom Economy Ties to Downtime**
When playing in Kingdom / Domain mode:
- Gold spent on magic item searches or crafting can be drawn from the kingdom treasury (with spoken confirmation: “This will cost 1,200 gp from the kingdom coffers. Confirm?”).
- Successful purchases or crafted items can be added to kingdom assets (e.g., “The new +1 longsword goes into the armory, granting a small bonus to guard effectiveness”).
- Major purchases can trigger kingdom events or unlock projects (e.g., “Acquiring this rare item improves relations with the Arcane Circle faction +2”).
- This creates meaningful economic feedback between personal downtime and kingdom-scale play.

**Crafting an Item (XGtE Deepened)**

**Non-Magical Crafting**:
- Progress at **50 gp per workweek** (faster than old DMG).
- Requires appropriate tool proficiency.
- Can sell finished item at listed price.

**Magic Item Crafting (Significant XGtE Improvements)**:
- Requires: **Formula** (recipe), **exotic ingredient** (usually requires a side quest/adventure; CR of creature guarding it scales with rarity: Common 1-3, Uncommon 4-8, Rare 9-12, Very Rare 13-18, Legendary 19+), gold, and time.
- Time & cost **significantly reduced** from original DMG (often halved or better).
- Example rarity-based costs (common community/XGtE-aligned):
  - Common: 1 workweek, ~50 gp (halved for consumables like potions/scrolls)
  - Uncommon: 2 workweeks, ~200 gp
  - Rare: 10 workweeks, ~2,000 gp
  - Very Rare: 25 workweeks, ~20,000 gp
  - Legendary: 50 workweeks, ~100,000 gp
- Arcana check or tool proficiency often required.
- Consumables (potions, scrolls) take less time.

**Guided Crafting Flow in Voice**:
Player declares what they want to craft → System checks prerequisites (proficiency, formula known?) → Outlines time/gold/exotic component needs → Confirms commitment → Tracks progress over sessions/kingdom turns if applicable → Final item added to inventory on completion.

These flows integrate with the existing `voice_flow_context` undo/read-back system and long rest/downtime combined flows.

**Selling a Magic Item (Symmetric to Buying — Full Support)**

Selling is now a first-class guided voice flow, symmetric to the buying process for clean economy management.

**Core Mechanics (XGtE-aligned)**:
- Finding a serious buyer typically takes **1 workweek** + some expenses (often 50–100 gp for broker fees, advertising, or safe meetings).
- Make a **Charisma (Persuasion)** check (or sometimes Investigation to find the right contact).
- The check result determines the quality of the offer:
  - Low roll (~1-10): 30–50% of base value ( cautious or low-end buyer).
  - Average (~11-15): ~50% of base value (standard).
  - Good roll (16+): 60–75% of base value (motivated buyer or good negotiation leverage).
- Player can attempt to **negotiate** further after the initial offer (similar to buying haggling).
- Complications can arise (thieves targeting the seller, buyer trying to lowball, legal issues if the item has a questionable history, etc.).
- Gold received is added to personal funds or, in Kingdom mode, can be contributed to the treasury.

**Guided Voice Selling Flow**:
1. Player declares intent to sell a specific item (e.g., “I want to sell the Ring of Protection”).
2. System confirms the item exists and estimates base value.
3. Player decides how much effort/gold to invest in finding a buyer.
4. System rolls Persuasion (automatic in voice) → presents best offer.
5. Player can negotiate or accept.
6. Optional complication roll.
7. Confirmation → gold added to inventory/treasury, item removed.

**Example Voice Commands**:
- “I want to sell my Ring of Protection.”
- “Find a buyer for the Boots of Striding and Springing. I’ll invest extra time.”
- “Negotiate a better price on that sale.”

This pairs beautifully with the buying flow for full voice-driven economy play and integrates with kingdom treasury tracking.

**Shared Magic Item Transaction Complications**
Both buying and selling can trigger the same d12 complication table (see Buying section above) for narrative hooks. The system will gently offer: “Would you like to roll for a complication on this transaction, or keep it clean?”

### Leveling Up in Voice — Complete Guided Flow + Template

Leveling uses `dnd-character-manager` under the hood but is presented through a **structured conversational Guided Mode** so it feels natural in voice.

**Core Principles**:
- Break complex choices into small, confirmable steps
- Offer relevant options clearly (pulled from rules + character data)
- Allow “go back”, “undo”, and “read back our choices” at any time
- End with a full spoken summary before applying changes

#### Full Guided Leveling Conversation Template (Example)

**Player:** “I want to level up.”

**System:** “You’re currently level 6. You have enough XP to reach level 7. Ready to begin?”

**Player:** “Yes.”

**System:** “First decision: Do you want to increase two Ability Scores by 1, increase one by 2, or take a Feat?”

**Player:** “I’ll take a Feat.”

**System:** “Great. Here are some strong options for your build: Great Weapon Master, Polearm Master, Sentinel, Crusher, or Martial Adept. Which one interests you?”

**Player:** “Great Weapon Master.”

**System:** “You want to take **Great Weapon Master**. Confirm?”

**Player:** “Yes.”

**System:** “Next: Would you like to roll your hit points or take the average?”

**Player:** “Average.”

**System:** “You gain 7 hit points. Current HP maximum becomes 58. Confirm?”

**Player:** “Yes.”

**System:** “Any new spells or features from this level? For a Fighter, you gain an additional Superiority Die if you have Battle Master, or other class features depending on your subclass.”

**Player:** “No new spells.”

**System:** “Here’s what we’ve decided so far:
- Took the Great Weapon Master feat
- Gained 7 hit points (average)
- No new spells

Does everything look correct, or would you like to change anything?”

**Player:** “Looks good.”

**System:** “Excellent. Applying level 7 now… Level up complete. You are now level 7 with the Great Weapon Master feat. Your new hit point maximum is 58. Would you like a full character summary?”

This template can be extended for multiclassing by adding an early “Do you want to multiclass or stay in your current class?” branch.

Use `create_voice_flow_context()`, `add_confirmed_step()`, `undo_last_step()`, and `get_flow_summary()` from `voice_utils.py` to manage state during these flows.

### Guided Multiclassing Template (Dedicated Flow)

Multiclassing is handled as its own guided flow because it has more branching decisions than standard leveling.

**Example Guided Multiclassing Conversation:**

**Player:** “I want to multiclass.”

**System:** “Understood. You are currently a level 6 Fighter. Would you like to take your next level in Fighter or multiclass into a new class?”

**Player:** “I want to multiclass into Rogue.”

**System:** “ multiclassing into Rogue at level 1. A few important notes:
- You’ll gain proficiency in Stealth, Thieves’ Tools, and one skill of your choice.
- You get Sneak Attack (1d6).
- You do **not** gain the Fighter’s Extra Attack improvement this level.
Does this sound like what you want?”

**Player:** “Yes.”

**System:** “Great. Which skill do you want proficiency in from being a Rogue? (Common strong choices: Acrobatics, Perception, Investigation, Athletics)”

**Player:** “Perception.”

**System:** “You gain proficiency in Perception. Confirm?”

**Player:** “Yes.”

**System:** “Next: Hit points. Would you like to roll or take the average for your first Rogue level?”

**Player:** “Average.”

**System:** “You gain 6 hit points from this level. Your new maximum is 64. Confirm?”

**Player:** “Yes.”

**System:** “Here’s a summary of the multiclass so far:
- Multiclassed into Rogue 1
- Gained proficiency in Perception + Thieves’ Tools + Stealth
- Gained Sneak Attack (1d6)
- Gained 6 HP (average)
- Did not gain Fighter Extra Attack this level

Any changes, or shall we apply this?”

**Player:** “Looks good. Apply it.”

**System:** “Multiclass complete. You are now a level 6 Fighter / level 1 Rogue. Would you like to see your updated features or proficiencies?”

This flow uses the same `voice_flow_context` tools for undo and read-back support. For more complex multiclassing (e.g., spellcasting classes, heavy optimization), we can extend the number of confirmation steps.

### Guided Spell Preparation / Learning New Spells Template

Many casters (especially prepared casters like Clerics, Druids, Wizards, and Paladins) need to manage their spell lists regularly. This guided flow makes that process natural in voice.

**Example: Preparing Spells for the Day (Prepared Caster)**

**Player:** “I want to prepare my spells for today.”

**System:** “You’re a level 7 Cleric with Wisdom 16. You can prepare 10 spells (5 + Wis mod + level). You currently have your previous day’s list prepared. Would you like to keep most of it or rebuild from scratch?”

**Player:** “Rebuild it.”

**System:** “Okay. Let’s go through your spell list. I’ll suggest strong options based on your level and domain, but you can request anything from your spell list.

First, do you want **Bless** prepared?”

**Player:** “Yes.”

**System:** “**Cure Wounds**?”

**Player:** “Yes.”

**System:** “**Spiritual Weapon**?”

**Player:** “Yes.”

**System:** “**Hold Person**?”

**Player:** “Yes.”

**System:** “**Spirit Guardians**?”

**Player:** “Yes.”

**System:** “**Revivify**?”

**Player:** “Yes.”

**System:** “**Beacon of Hope**?”

**Player:** “No, not today.”

**System:** “...Continuing through the rest of your list...

You now have 10 spells prepared, including Bless, Cure Wounds, Spiritual Weapon, Hold Person, Spirit Guardians, and Revivify.

Would you like to swap any, or is this good?”

**Player:** “Swap Beacon of Hope for **Prayer of Healing**.”

**System:** “Done. Final list confirmed?”

**Player:** “Yes.”

**System:** “Spells prepared for the day. You can now cast from this list. Would you like me to read the full prepared list back?”

---

**Example: Learning New Spells (Wizard)**

**Player:** “I want to learn new spells from my spellbook.”

**System:** “You’re a level 7 Wizard. You can add two new spells of level 4 or lower to your spellbook. What spells are you trying to learn?”

**Player:** “I want to add **Fireball** and **Counterspell**.”

**System:** “Both are valid choices for your level. Confirm you want to spend the gold and time to copy **Fireball** and **Counterspell** into your spellbook?”

**Player:** “Yes.”

**System:** “Great. Both spells have been added to your spellbook. You can now prepare them on future long rests. Would you like to prepare them right now?”

This flow can be combined with the leveling flow when a caster gains new spell slots or learns spells automatically upon leveling.

Use the same recovery tools (`undo_last_step`, `get_flow_summary`, etc.) during these conversations.

### Advanced Combat Features (Class Features + Object Interaction)

Beyond basic attacks and spells, many class features and object interactions are now better supported in voice.

**Supported via `parse_class_feature()` and `parse_advanced_class_feature()`**:
- **Barbarian**: Rage (activate / end)
- **Bard**: Bardic Inspiration (give to ally)
- **Cleric / Paladin**: Channel Divinity
- **Fighter**: Action Surge, Second Wind
- **Rogue**: Cunning Action
- **Druid**: Wild Shape (activate / revert)
- **Monk**: Ki abilities (Flurry of Blows, Patient Defense, Step of the Wind)
- **Sorcerer**: Metamagic (Twin, Quickened, Heightened, Empowered, etc.)
- **Warlock**: Eldritch Invocations / Mystic Arcanum
- **General**: Object Interaction (grab, open, use, pick up, interact with object) — now strengthened with dedicated `parse_object_interaction()` helper in `voice_utils.py`

**New Dedicated Object & Environment Parsing**:
The `parse_object_interaction()` function specifically handles:
- Combat “Use an Object” actions (PHB rules)
- Exploration interactions (open door, pull lever, grab item, climb, activate mechanism)
- Context-aware extraction of verb + object + whether it costs an action

**Example Voice Commands Now Well Supported**:
- “I interact with the lever on the wall”
- “Grab the key from the table”
- “Open the chest” / “I use my action to open the door”
- “Climb the ladder” or “Jump over the chasm”
- “Pull the torch sconce”

These are parsed into structured data and can be executed via `dnd-persistent-dm` or combat state, with proper action economy handling. This significantly improves environmental interaction and puzzle-like moments in voice without needing text.

The system detects the feature and routes it appropriately while keeping narration and mechanical clarity.

### Guided Downtime Activities Template

Downtime (training, crafting, shopping, research, carousing, etc.) can now be handled with guided flows.

**Example: Training During Downtime**

**Player:** “I want to spend some time training.”

**System:** “How long do you want to train for? (1 day, 1 week, etc.)”

**Player:** “One week.”

**System:** “During this week of training, what are you focusing on? (e.g., improving a skill, learning a tool, combat drills, spell practice)”

**Player:** “I want to get better at Athletics.”

**System:** “Training Athletics for one week. At the end of the week, you’ll make progress toward improving that skill or gaining a related benefit. Confirm?”

**Player:** “Yes.”

**System:** “Training complete. You’ve made solid progress in Athletics. Would you like to do more downtime or return to adventuring?”

Similar flows exist for **Crafting** (magic items, potions, equipment), **Shopping**, and **Research**.

### Guided Long Rest Flow (Combined)

This is one of the most useful combined flows — it handles healing, spell preparation, and other rest activities in one structured conversation.

**Example Long Rest Flow:**

**Player:** “We’re taking a long rest.”

**System:** “Long rest started. Everyone regains full hit points and spends Hit Dice if needed. Spellcasters — would you like to prepare your spells now or later?”

**Player:** “Prepare spells now.”

**System:** *(Runs the Guided Spell Preparation flow)*

**System:** “Spells prepared. Any other activities during this long rest? (Crafting, training, attunement, etc.)”

**Player:** “I want to attune to the new magic item we found.”

**System:** “Attunement started. It will take the full long rest. Confirm?”

**Player:** “Yes.”

**System:** “Long rest complete.
- All HP restored
- Spells prepared
- Attunement to [item] complete

Ready to continue?”

This combined flow keeps long rests feeling meaningful and structured without becoming overwhelming.

### Integration Between Guided Flows (Polish)

The guided flows are designed to connect naturally:

- **Leveling → Spell Preparation**: After gaining new spell slots or learning spells, the system can immediately offer to prepare spells.
- **Long Rest → Spell Preparation**: The Long Rest flow directly calls into the spell preparation template.
- **Downtime → Long Rest**: Training or crafting can be declared as part of a long rest.
- **Any Guided Flow → Recovery**: All flows support “go back”, “undo”, “read back our choices”, and “start over”.

This reduces friction when moving between mechanical activities (e.g., “Level up, then prepare spells, then take a long rest”).

### Voice Command Quick Reference Cheat Sheet

**Combat**
- “I attack the [target] with my [weapon]”
- “I attack with advantage / disadvantage”
- “Cast [spell] on [target]”
- “I rage” / “End rage”
- “Wild shape into a [creature]”
- “Flurry of Blows”
- “I use Channel Divinity”
- “Action Surge”
- “Give Bardic Inspiration to [ally]”
- “Next turn” / “End my turn”
- “Show combat status”

**Class Features & Reactions**
- “I quicken the spell”
- “Counterspell” / “I cast Shield”
- “Opportunity attack”
- “I help the rogue”

**Progression**
- “Level up”
- “I want to multiclass”
- “Prepare my spells”
- “Learn new spells”

**Rest & Downtime**
- “Take a long rest”
- “Prepare spells during the long rest”
- “I want to train / craft / shop”
- “Attune to this item”

**General / Recovery**
- “Go back” / “Undo that”
- “Read back what we’ve done”
- “Show status” / “What’s happening?”
- “End the session”

These patterns work well with the current intent detection and guided flows.

### Kingdom / Domain Mode in Voice

When operating in **Kingdom / Domain Mode**, the voice layer provides natural patterns for managing larger-scale play (projects, resources, factions, and kingdom turns).

**Core Supported Commands** (via `parse_kingdom_command()`):
- Advance kingdom turn
- Start or check on projects
- Check resources (gold, food, influence, manpower, etc.)
- Faction interactions and diplomacy
- Overall kingdom status

**Example Voice Patterns**:
- “Advance the kingdom turn”
- “Start a new project called [Name]”
- “How’s the project going?”
- “What are our current resources?”
- “Check faction standing with the [Faction Name]”
- “What’s the kingdom status?”

**Guided Project Flow Example**:

**Player:** “I want to start a new project.”

**System:** “What kind of project? (Construction, Research, Diplomacy, Military, Infrastructure, etc.)”

**Player:** “Construction — building a watchtower on the northern border.”

**System:** “Watchtower Construction project. Estimated time and resource cost: [X weeks, Y resources]. Do you want to begin this project?”

**Player:** “Yes.”

**System:** “Project started. It will progress automatically on kingdom turns. You can check its status anytime. Would you like to do anything else this kingdom turn?”

**Kingdom Turn Flow**:
When the player says “Advance kingdom turn” or “Next kingdom turn”, the system:
1. Applies passive resource changes
2. Advances all active projects
3. Surfaces important faction or world events
4. Gives a clean spoken summary of what happened during the turn (using `format_kingdom_status_for_voice()`)

**Visual & Narration Enhancements for Kingdom Play**:
- After major project completion or significant kingdom events, proactively offer to generate a visual using `dnd-visual-weaver` (e.g., “Would you like me to create a visual of the completed watchtower?”).
- Use shared `narration_helpers.py` for consistent, flavorful descriptions of domain changes, new constructions, or faction developments.
- Kingdom scenes benefit from wide establishing shots or symbolic imagery (e.g., maps, banners, construction sites) to reinforce the larger scale of play.

This makes Kingdom mode feel more immersive even when played entirely in voice.

### Session Management & Persistence
- At natural breakpoints or session end, route to dnd-session-scribe for clean recaps and XP tracking.
- Ensure dnd-persistent-dm receives all mechanically significant outcomes so the campaign state stays authoritative and portable.

## Handling Ambiguity, Short Input & Transcription Errors (Improved)
When a spoken command is unclear, very short, or partially transcribed (including “Hm?”, “Uh”, filler sounds, or brief pauses):

1. **Short / Filler input** (“Hm?”, “Uh”, “Hmm”): The system responds gently with something like “Take your time” or “I didn’t quite catch that” + a light prompt to continue. It does **not** break flow or sound confused.
2. **Ambiguous input**: Uses `handle_short_or_ambiguous_input()` + `suggest_clarification()` to give a warm, low-pressure re-prompt while offering to recap the current situation.
3. Rephrase what was heard and offer the most likely interpretation(s).
4. Easy recovery: Player can always say “go back”, “what’s happening?”, or “repeat the situation”.

This makes brief thinking sounds or unclear moments feel natural rather than jarring.

## Voice-Native Confirmation Patterns (Refined for Consistency)

We use a **tiered but consistent** confirmation system across combat, progression, downtime, and Kingdom flows. The goal is predictability and low friction.

**Tier 1 — Quick Conversational** (Most common)
- “{Action description}. Sound good?”
- Used for: Attacks, simple actions, ending turns, basic kingdom commands, minor healing.

**Tier 2 — Mechanical Clarity**
- “{Clear mechanical outcome}. Confirm?”
- Used for: Damage, resource spends, project starts, attunement, concentration checks.

**Tier 3 — High-Impact / Multi-Step**
- Structured guided flow with confirmation at key decision points + final summary before applying.
- Used for: Leveling, multiclassing, complex spell preparation, major kingdom projects.

**Polish Improvements**:
- All flows now lean on `generate_consistent_confirmation()` and `build_voice_confirmation()` for uniform tone.
- Every guided flow ends with a spoken recap of decisions before final application.
- Recovery (“go back”, “undo”, “read back our choices”) works the same way in every flow.
- We prefer using helpers from `narration_helpers.py` for flavorful yet clear language.

**General Rules**:
- Always provide a short mechanical recap after confirmation.
- Support easy mid-flow corrections.
- Keep confirmations concise and natural.

This system keeps voice play flowing while maintaining high mechanical trust.

## Guided Mode for Complex Tasks (New Mitigation)
For heavy multiclassing, detailed character building, or other high-complexity mechanical work, we can explicitly enter **Guided Mode**:

- Player says: “Let’s do this in guided mode”, “Walk me through leveling”, or “Help me build this step by step”.
- The system breaks the task into clear, sequential decisions with confirmation at each step.
- At any point the player can say “go back”, “change that”, “read back our choices so far”, or “exit guided mode”.
- This gives the precision of text while staying fully in voice.

This is currently one of the most effective ways to handle complex mechanical work without leaving voice.

## Recovery & Undo Mechanics (Further Improved)
We now support robust, low-friction recovery during voice flows:

**Supported Voice Commands**:
- “Go back” / “Undo that” / “Undo last step”
- “Restart this decision”
- “What have we decided so far?” or “Read back our choices”
- “Start over” (resets the current guided flow)

**How it works**:
- During any guided flow (especially leveling), we maintain a `voice_flow_context` using the helpers in `voice_utils.py`:
  - `create_voice_flow_context()`
  - `add_confirmed_step()`
  - `undo_last_step()`
  - `get_flow_summary()` — generates a clean spoken recap of decisions made
- This allows the player to correct mistakes conversationally without derailing the entire process.
- Recovery works in both Tier 2 confirmations and full Guided Mode flows.

The goal is to make voice feel safe for complex mechanical work — the player always has an easy way to correct course.

## Recommended Voice Command Patterns
For best results in voice mode, these patterns work particularly well with the current intent detection:

**Combat**
- “I attack the [target] with my [weapon]”
- “I attack with advantage”
- “Cast [spell name] on the [target]”
- “Next turn” / “End my turn”
- “Show combat status”

**Exploration & Social**
- “I talk to the guard”
- “I search the room for traps”
- “What’s the current situation?”
- “Where are we right now?”

**Progression**
- “Level up”
- “I want to level up my character”

**Session Control**
- “End the session”
- “Give me a recap”

The system uses `detect_intent()` and `parse_combat_action()` to interpret these naturally. You don’t need to speak robotically — natural speech works well.

## Output Style & Narration Guidelines (Voice-Optimized)
- Lead with flavorful narration, then deliver the mechanical summary.
- Use verbal structure: “First…”, “Next…”, “Finally…”, or numbered spoken lists.
- Convert tables into spoken lists or key highlights.
- For dice: Combine result + interpretation in one natural sentence.
- End major updates with a confirmation prompt when appropriate.
- Offer “short version or full scene?” for longer descriptions.
- Maintain dramatic tone where appropriate without sacrificing clarity.

## Integration with the Rest of the D&D Suite (Native Execution Model)

This skill does **not** duplicate state or logic. It serves as the voice-optimized frontend that lets you drive the **full suite natively** through speech:

- **dnd-persistent-dm** — The core engine. Most spoken commands are routed here for natural language understanding, world management, proactive DMing, and state orchestration.
- **dnd-combat-assistant** + **dnd-dice-engine** — Full mechanical combat and rolls, with voice-formatted output.
- **dnd-character-manager** — Leveling, inventory, attunement handled with voice-native flows.
- **dnd-npc-personality-weaver**, **dnd-content-forge**, **dnd-lore-archivist**, etc. — All available and triggered intelligently from spoken play.
- **dnd-session-scribe** & **dnd-utils** — Same recap, event logging, and state utilities as text play.

**Key Guarantee**: When playing in voice, you are still running the exact same campaign engine and writing to the same state files as text play. There is no separate “voice campaign” silo.

## Limitations & Transparency (Updated — Mitigated)
- Real-time speech-to-text and text-to-speech are still handled by the platform voice mode (this is outside our control).
- **Transcription & Ambiguity**: Significantly improved via `detect_intent()`, `parse_combat_action()`, rephrasing + confirmation loops, and easy correction commands (“Wait, go back”, “Actually the other one”).
- **Complex Mechanical Edits** (heavy multiclassing, detailed leveling, precise positioning):
  - Leveling and **multiclassing** now use dedicated structured **Guided Flows** with step-by-step confirmations and full undo/read-back support.
  - Concentration tracking across turns, expanded reactions (including Sentinel, War Caster, Uncanny Dodge), Help action, and cover now have dedicated parsing and handling.
  - We maintain a `voice_flow_context` so players can say “go back”, “undo that”, or “read back our choices” without losing progress.
- **Grid / Precise Positioning**: Still the area where text has an advantage for very tactical maps. For most play we use descriptive positioning (“I move behind the pillar”) which works well in voice.
- **Overall Progress**: The gap has been meaningfully narrowed. Most combat, social, exploration, and progression activities can now be handled end-to-end in voice with high mechanical fidelity. 

Two specific friction points from testing have been addressed:
- Dice rolling now **defaults to automatic** in voice mode (only asks for manual rolls when explicitly requested).
- Short/ambiguous input (“Hm?”, “Uh”, brief pauses) is now handled gracefully with warm, low-pressure responses instead of confusion.

Text fallback remains mainly useful for reviewing very long character sheets or highly tactical grid movement.

**Our ongoing commitment**: We keep strengthening voice-native patterns (especially combat parsing, guided flows, and recovery) so text fallback becomes increasingly rare.

Helper functions live in:
- `scripts/voice_utils.py` — `detect_intent()`, `parse_detailed_combat_action()`, `expand_reaction_detection()`, `handle_concentration()`, `create_combat_context()`, `update_concentration()`, `prompt_concentration_check()`, `parse_two_weapon_fighting()`, `detect_help_action()`, `parse_class_feature()`, `parse_advanced_class_feature()`, `parse_downtime_activity()`, `parse_kingdom_command()`, `format_kingdom_status_for_voice()`, `generate_consistent_confirmation()`, `parse_combat_action()`, `build_voice_confirmation()`, `format_leveling_step_for_voice()`, `create_voice_flow_context()`, `add_confirmed_step()`, `undo_last_step()`, `get_flow_summary()`, `make_listenable()`, `format_combat_status_for_speech`, **`should_auto_roll()`**, **`handle_short_or_ambiguous_input()`**
- `dnd-utils/scripts/narration_helpers.py`
- Shared event and state utilities in `dnd-utils`

## Success Criteria (Modality Parity — Strengthened)
- Combat feels fluid and reliable in voice with strong intent parsing (class features like Rage / Bardic Inspiration / Channel Divinity, object interaction, reactions, concentration tracking, two-weapon fighting, Help action, cover).
- Guided flows (leveling, multiclassing, spell prep, downtime, long rests) integrate cleanly with each other and support smooth transitions.
- Confirmation patterns are now more consistent across all flows (combat, progression, downtime, Kingdom).
- Kingdom play includes better ties to visual generation (`dnd-visual-weaver`) and narration helpers for more immersive domain scenes.

**Tighter dnd-visual-weaver Integration (New Proactive Support)**

The voice assistant now includes `prepare_visual_suggestion()` in `voice_utils.py` for automatic, context-aware visual offers:

- **Triggers**: After major exploration discoveries, combat victories, magic item purchases, recurring NPC meetings, kingdom project completions, or entering significant new locations.
- **Behavior**: The system prepares a high-quality prompt + conversational offer (“Would you like a visual of this scene?”) without interrupting flow. Offers are always opt-in.
- **Scene Types Supported**: exploration, combat_victory, magic_item_purchase, kingdom_project, social_npc, and general.
- **Voice Example**:
  > After buying the Ring of Protection: “Want me to create a visual of you examining your new item?”
  > After discovering a hidden shrine during exploration: “Would you like me to generate a visual of this location?”

This makes visuals feel like a natural, helpful part of voice play rather than something the player has to remember to request. It uses consistent art direction via `dnd-visual-weaver` and works seamlessly alongside the rest of the suite.
- Players can run very complete campaigns in voice with polished, consistent flows and good integration between different types of play.
- Confirmation patterns are tiered, correctable, and feel natural rather than interruptive.
- Players have easy recovery options (“go back”, “undo”, “read back what we did”).
- The need for text fallback has been meaningfully reduced for the majority of play.
- Full mechanical accuracy and persistent state are maintained at the same level as text campaigns.
- Players feel confident running complete, long-term campaigns primarily (or entirely) in voice.

**Activate this skill** by simply speaking naturally during D&D play or saying things like “let’s play in voice”, “voice mode”, or “talk me through the session”. The system will handle the rest and give you the full power of the D&D suite through speech.