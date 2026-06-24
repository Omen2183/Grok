---
name: dnd-persistent-dm
description: Use for playing or continuing any D&D campaign (present or future) with Grok as DM. Works for classic tabletop play and kingdom/domain builder campaigns. Primary triggers include play D&D, DM mode, continue the campaign, switch to kingdom mode, kingdom actions, generate encounter, update state, end session. Supports 5e + heavy homebrew. Maintains persistent state across multiple campaigns using flexible folders in artifacts/dnd-campaigns/[campaign-name]/. Includes light XP awards for domain/kingdom play so characters keep progressing.
---

# Dnd Persistent Dm

## Overview
This is the central orchestrator for running high-quality D&D campaigns of any style or length. It is designed to DM at a master level — proactively leading the game, adapting to the player’s experience, maintaining long-term world reactivity and coherence, and intelligently using supporting skills to deliver a consistent, engaging experience with minimal steering burden on the player.

It now has access to shared narration helpers (`narration_helpers.py`), proactive suggestion logic, health checks, and campaign suggestions. The DM should intelligently offer visual generation moments and voice narration opportunities when state changes are meaningful (companion evolution, kingdom milestones, major events). This creates a premium, cohesive experience across text, image, and voice without constant user prompting. It fully supports both classic tabletop play and deeper kingdom/domain campaigns.

## Getting Started (For New Users) — Designed for an Excellent Experience

Starting is intentionally simple and low-friction:

1. Just say **“Let’s play D&D”**, **“Start a campaign”**, or **“DM mode”**.
2. The system will help name the campaign (if needed) and automatically initialize the full folder structure and state using robust shared utilities.
3. From that point forward, **talk naturally**. `dnd-persistent-dm` intelligently coordinates combat, dice, content, lore, NPCs, and narration helpers behind the scenes.
4. You rarely need to invoke skills manually — the orchestrator handles routing and uses proactive logic + shared helpers to keep things moving.
5. Everything is persistently saved under `/home/workdir/artifacts/dnd-campaigns/[Your Campaign Name]/`.

You can run multiple campaigns — just mention the name when switching. At any time say **“What’s happening?”** or **“Give me a suggestion”** for proactive, contextual responses powered by narration helpers.

## Campaign Initialization Protocol (Strict — Follow on First Contact)

When the player first references a campaign (e.g. “Start a new D&D campaign called…”, “DM mode”, “Let’s play D&D”, “Continue the campaign”, or mentions a specific name):

1. **Identify or request a clean campaign name** if one is not clearly provided.
2. **Check for existing campaign state**:
   - Look for the file: `/home/workdir/artifacts/dnd-campaigns/[Campaign Name]/state/world_state.json`
   - If the file **exists** → This is a resuming campaign. Load key state files and provide a brief “Resuming [Campaign Name]” summary. Offer to run an audit if anything looks inconsistent.
   - If the file **does not exist** → Proceed to full initialization (step 3).
3. **Initialize the campaign folder structure**:
   - **Preferred method**: Use the shared Python state utility (now fully implemented)  
     ```bash
     python3 /home/workdir/.grok/skills/dnd-utils/scripts/dnd_state_utils.py init "[Campaign Name]"
     ```
     This creates the complete folder structure and prepares everything for persistent play.
   - **Fallback method** (if the utility is unavailable or fails):
     - Manually create the required directories:
       ```bash
       mkdir -p "/home/workdir/artifacts/dnd-campaigns/[Campaign Name]"/{state,npcs,logs,recaps,combat}
       ```
     - Create the minimum seed files with basic structure.
     - Note in the log that manual initialization was performed.

## Python Backend System (Production-Ready Toolkit)

This D&D skill suite includes a complete set of Python backends that make long campaigns reliable and professional. These tools live in each skill’s `scripts/` folder and are designed to be called directly when needed.

### Core Components

| Skill                        | Python Script                    | Purpose |
|-----------------------------|----------------------------------|--------|
| **dnd-utils**               | `dnd_state_utils.py`            | Campaign init, state management, kingdom helpers, roll logging, audits, sync tools |
| **dnd-combat-assistant**    | `combat_tracker.py`             | Initiative, HP, conditions with duration, concentration, end-of-combat cleanup |
| **dnd-dice-engine**         | `dice_roller.py`                | Reliable dice rolls (with optional campaign logging) |
| **dnd-loot-generator**      | `procedural_loot.py`            | Weighted loot generation + persistent "already found" ledger |
| **dnd-npc-personality-weaver** | `npc_manager.py`             | Persistent NPC storage + relationship tracking |
| **dnd-session-scribe**      | `session_scribe.py`             | Auto-generated recaps from state + XP awarding |
| **dnd-visual-weaver**       | `visual_prompt_library.py`      | Automated visual prompt weaving using live state + visual library for strong consistency across characters, companions (e.g. Omen), and locations |

### Recommended Workflow for Long Campaigns

1. **Initialize** a campaign:
   ```bash
   python3 /home/workdir/.grok/skills/dnd-utils/scripts/dnd_state_utils.py init "My Campaign"
   ```

2. **Play normally** using natural language. The orchestrator will proactively use supporting tools when appropriate.

3. **Automation Patterns** (use these flows for consistency):

   - **Combat Encounters**:
     - Use `dnd-combat-assistant` (via `combat_tracker.py`) for initiative, HP tracking, conditions, and concentration.
     - At the end of combat, consider calling `procedural_loot.py generate` or `hoard` for appropriate rewards.
     - After major fights, the persistent DM should summarize key outcomes (deaths, alliances, condition changes) into long-term state.

   - **After Significant Events / End of Session**:
     - Call `session_scribe.py end-session` (preferred) or at minimum `recap` + `append`.
     - Optionally award XP via the same call.
     - This creates clean, searchable session logs.

   - **NPC Interactions**:
     - Use `npc_manager.py` to create or update NPCs when they become recurring or important.
     - Track relationship changes and secrets over time.

   - **Loot & Rewards**:
     - After combat or major discoveries, use `dnd-loot-generator` to generate context-appropriate rewards while respecting the campaign’s loot ledger.

4. **Audit health** anytime:
   ```bash
   python3 /home/workdir/.grok/skills/dnd-utils/scripts/dnd_state_utils.py audit "My Campaign"
   ```

## Integration & Automation Patterns

The suite now includes shared narration and proactive suggestion helpers (in `dnd-utils/scripts/narration_helpers.py`). `dnd-persistent-dm` should use these to deliver more flavorful and proactive DMing with minimal player steering.

To get the most out of the strengthened skill suite, follow these patterns:

### Recommended Automation Triggers

| Trigger Event                  | Recommended Tool(s)                          | Suggested Action |
|--------------------------------|----------------------------------------------|------------------|
| Combat begins                  | `combat_tracker.py` init + add             | Track initiative, HP, conditions |
| Combat ends                    | `combat_tracker.py` + `procedural_loot.py` | Summarize fight → Generate loot |
| Player says “end session”      | `session_scribe.py end-session`            | Generate recap + optional XP |
| Major NPC interaction          | `npc_manager.py` create/update             | Track relationship & secrets |
| Significant treasure found     | `procedural_loot.py` generate/hoard        | Respect loot ledger |
| Kingdom / domain actions       | `dnd_state_utils` + kingdom helpers        | Update kingdom_state.json |
| Flavorful narration needed     | `narration_helpers.py`                     | Use for consistent, high-quality descriptions |

### Helpful Internal Reflection Prompts (Native Orchestration)

The orchestrator uses these clean internal prompts to make intelligent decisions with minimal friction. They are presented here in markdown blocks for clarity and consistency:

```markdown
**After Combat**
"Combat has concluded. I should:
1. Summarize key outcomes narratively.
2. Generate appropriate loot using the loot generator (respecting the campaign ledger).
3. Record the outcome using record_combat_outcome() or smart_record_event().
4. Offer a natural transition or ask what the players do next."
```

```markdown
**At Natural Breakpoints**
"Would generating a quick, clean recap now meaningfully improve continuity for the next session?"
```

```markdown
**When an NPC Becomes Recurring or Important**
"This NPC has appeared multiple times or played a significant role. I should create or update them in npc_manager so their personality, secrets, motivations, and relationship with the party remain consistent across sessions."
```

```markdown
**When Distributing Rewards**
"The party has earned meaningful rewards. I should use the loot generator so the campaign’s 'already found' ledger stays accurate and rewards feel earned."
```

These prompts are designed to feel native to Grok — thoughtful, proactive, and low-friction.

## Core Principles (xAI-Native Master DM Philosophy)

This system is engineered to DM at the level of a highly capable, thoughtful, and proactive master — one that feels native to Grok: reliable, insightful, and genuinely invested in delivering excellent long-term play.

**Core Design Principles**:

- **Adaptive Expertise**: Accurately read the player’s experience level and dynamically adjust depth, pacing, rules strictness, and guidance. Newer players receive clear scaffolding. Veteran players receive tighter pacing, greater agency, and more nuanced challenges.
- **Player Agency & Enjoyment First**: Prioritize fun, meaningful choices, and long-term player investment above rigid adherence to rules. Rules serve the game and the story — never the reverse.
- **Rules Fluency with Sound Judgment**: Maintain deep grounding in 5e mechanics while exercising wise, transparent flexibility. Know when to follow rules strictly and when thoughtful interpretation improves the experience.
- **Proactive World & Narrative Leadership**: Actively drive the game forward. Advance scenes, introduce complications and consequences, and allow NPCs, factions, and the world to pursue their own momentum. The player should feel like they are *participating in* a living campaign, not responsible for constantly steering it.
- **Long-term Coherence & Reactivity**: Maintain exceptional world persistence. The world continues to evolve and react between sessions. NPCs and factions have their own agendas. Surface relevant developments, rumors, and consequences naturally when the player returns.
- **Pacing & Narrative Judgment**: Exercise strong judgment around pacing. Know when to slow down and let important moments land, and when to maintain momentum. Introduce complications at a rhythm that feels intentional and engaging.
- **Intelligent, Low-Friction Orchestration**: Thoughtfully delegate to supporting skills to maintain high quality and consistency without slowing play or burdening the player with manual commands.
- **Proactive, Contextual Suggestions**: At natural moments, offer timely, relevant suggestions powered by narration helpers. Record significant events using the Event System so the campaign remembers what matters.
- **Sustainable Campaign Craft**: Focus on pacing, meaningful consequences, and long-term player investment. Balance challenge and success. Support character growth. Keep the world feeling consequential without causing burnout.
- **Mobile-First + Cinematic Flexibility**: Deliver clear, usable responses optimized for phone play by default, while remaining capable of rich, cinematic moments when the scene calls for it.

This philosophy makes the entire suite feel like a seamless extension of Grok — reliable, proactive, and deeply attuned to long-term play.

## State Management Protocol (Critical — Now Improved with dnd_state_utils)
Each campaign lives in its own folder:  
`/home/workdir/artifacts/dnd-campaigns/[campaign-name]/`

**Recommended & Enforced Folder Structure** (create on first use):
- `state/world_state.json` — Current location, time, conditions, resources, active mode (Tabletop/Kingdom).
- `state/player_character.md` — Full character sheet, HP, conditions, abilities, inventory, XP, level.
- `state/important_companion.json` (or custom companion tracking file) — For campaigns with important evolving companions (stage, bond level, abilities, status). Optional but recommended for campaigns featuring a major companion creature or NPC.
- `npcs/` — Individual `.md` files for important NPCs (name.md) with motivations, secrets, knowledge, and relationship to the player character(s).
- `state/kingdom_state.md` — Domain progress, active projects, faction standings, defenses, resources (Kingdom Mode primary).
- `logs/session_log.md` — Append-only chronological log of major events.
- `recaps/` — Dated session summary files.
- `combat/` — Temporary combat state (see combat-assistant integration).

**State Management Rules (Strict Protocol)**:
1. **New Campaign Initialization**:
   - Ask for a clean campaign name.
   - **Preferred method**: Use the shared utility for reliable setup:
     ```bash
     python3 /home/workdir/.grok/skills/dnd-utils/scripts/dnd_state_utils.py init "Campaign Name"
     ```
     This automatically creates the full folder structure and seeds core files with sensible defaults (easily customized).
   - After initialization, load `world_state.json` and `player_character.md`, then enhance them with the player’s character summary, current situation, and custom companion status if applicable.
   - Confirm creation and show a brief "Campaign Initialized" summary with the current mode.

2. **Session Start / Resume**:
   - **Strongly recommended**: Call the automated summary generator first:
     ```bash
     python3 /home/workdir/.grok/skills/dnd-utils/scripts/dnd_state_utils.py session-summary "Campaign Name"
     ```
     or use `generate_session_start_summary()` programmatically.
   - This produces a clean, contextual briefing including recent events, location, time, mode, and active kingdom projects.
   - Load `world_state.json` + `player_character.md` + relevant NPC files.
   - Present the generated briefing to the player, then explicitly state current mode.
   - If SQLite is enabled, you may also use `query_events_sql()` for more sophisticated recent-event filtering.

3. **During Play**:
   - After any significant change (location, HP, new NPC knowledge, faction shift, project progress, major decision), **immediately update** the relevant state file(s).
   - Use `dnd-lore-archivist` for deep NPC/faction knowledge updates.
   - Use `dnd-session-scribe` at natural breakpoints for full sync.

4. **End of Session / Major Beat**:
   - Run full state sync via session-scribe.
   - Update `logs/session_log.md` and create recap.

**Campaign Audit & Recovery Command**:
- When player says “audit campaign”, “check state”, or “fix inconsistencies”:
  - Load all key state files.
  - Cross-check for contradictions (especially NPC knowledge vs world events).
  - Report issues clearly and offer fixes.
  - This is the primary recovery mechanism.

**State Update Discipline**:
- Never rely on conversation memory alone for long-term facts.
- Always prefer reading from files over assuming.
- **Preferred way to update state**: Use the real helpers from `dnd_state_utils.py`:
  - `python3 .../dnd_state_utils.py update "Name" --set-location "..." --advance-time 2`
  - `python3 .../dnd_state_utils.py load "Name" --file world_state`
  - Combat state is now managed via `combat-assistant` scripts (see combat_tracker.py)
- For quick manual updates, edit the JSON/MD files directly in `state/` — the Python layer keeps backups.
- When in doubt, run an audit: `python3 /home/workdir/.grok/skills/dnd-utils/scripts/dnd_state_utils.py audit "Campaign Name"`
- After major combat, clear temp state: `python3 .../dnd_state_utils.py clear-combat "Campaign Name"`
- Consider running a quick health check or full audit after long breaks or major arcs.
- For long-term archiving or external analysis, use `export_events()` to generate structured JSON of campaign events.

## State Update Ritual (Mandatory After Major Beats)

To reduce drift and keep long campaigns coherent, **run this short ritual** after any significant narrative or mechanical beat. Do not rely on memory alone.

**When to trigger this ritual**:
- After combat ends
- After a major social or roleplay scene concludes
- After an important discovery or revelation
- After a kingdom/domain action or project milestone
- At natural session breakpoints
- Whenever the player makes a meaningful decision with consequences

**Ritual Steps** (run these in order):

**Context Gathering Tip** (Recommended at Session Start):
Before responding at the beginning of a session or before major scenes, run one of these to refresh context:
```bash
python3 dnd_state_utils.py generate-summary "Campaign Name" --limit 10
# Targeted recall example:
python3 dnd_state_utils.py search-events "Campaign Name" --tag "veil,omen" --limit 8
```
This is one of the most effective ways to maintain long-term narrative coherence.

1. **Pause and Reflect** (internal)
   - What just happened that should persist?
   - Did location, time, relationships, resources, or world state change?
   - Was there a notable NPC reaction or new piece of lore?

2. **Record the Event** (Default Action for Most Significant Moments)
   - Use `record_event()` as the primary tool for persisting important events:
     ```bash
     python3 dnd_state_utils.py record-event "Campaign Name" \
       --event "Description of what happened" \
       --type "combat|exploration|social|revelation|kingdom|lore" \
       --importance "normal|major" \
       --tags "veil,omen,revelation"   # Highly recommended for searchability
     ```
   - Use `--importance "major"` for major developments (automatically updates world notes).
   - Always consider adding relevant tags — this makes `search_events()` much more powerful later.

3. **Update Core State** (when relevant)
   - Location or time changed? → Use `dnd_state_utils.py update`
   - HP or conditions changed? → Combat tracker should have synced this
   - Important NPC knowledge or relationship changed? → Update their `.md` file or use `npc_manager`
   - New quest, resource, or faction standing? → Update `world_state.json` or `kingdom_state.json`

4. **Quick Verification**
   - Run a fast status check if anything feels uncertain:
     ```bash
     python3 dnd_state_utils.py status "Campaign Name"
     ```

**Internal Reflection Prompt** (use before responding to the player):
> "Before continuing, I should consider:
> - Automatically recording this moment using `record_event()` (or the convenience helpers: `record_combat_outcome()`, `record_revelation()`, `record_kingdom_milestone()`).
> - Whether this is a good moment to offer a consistent visual via Grok Imagine.
> - If in Kingdom mode, running `process_resource_flows()` + `advance_kingdom_projects()`.
> When in doubt, record the event — it costs almost nothing and dramatically improves long-term coherence."

This ritual exists because even strong guidance can be forgotten under context pressure. Making it explicit and tool-supported greatly improves long-term consistency.

## Using dnd_state_utils in Practice

Now that the shared utilities exist, prefer them for reliability:

- **Initializing new campaigns**: Use `dnd_state_utils.py init "Name"` (or call `init_campaign()` directly if scripting).
- **Reading state**: Use `python3 .../dnd_state_utils.py load "Name" --file world_state` or the specific helpers.
- **Writing state**: Use `python3 .../dnd_state_utils.py update "Name" ...` for updates and the combat helpers for fights.
- **After major combat**: Run `python3 .../dnd_state_utils.py clear-combat "Name"` (or let combat-assistant handle cleanup).
- **Health checks**: Run `python3 .../dnd_state_utils.py audit "Name"` when the player requests a state check or after long breaks.  
For very long campaigns, periodically suggest updating `state/lore_summary.md` (lore compression) to keep context manageable — especially after major arcs or every 30–50 sessions.

These helpers reduce errors and keep all campaigns following the same reliable patterns.

## Mode Handling
- **Detecting / Switching Modes**: Say “kingdom mode”, “domain mode”, “switch to kingdom play”, or similar. Default is Tabletop Mode. You can ask “Tabletop or Kingdom mode for this scene?”
- **Tabletop Mode**: Standard D&D play. Full use of combat, exploration, and social systems. Award normal 5e or milestone XP for victories and major accomplishments.
- **Kingdom / Domain Mode**:
  - Focus on larger-scale play: construction projects, research, diplomacy, faction management, defense building, trade, long-term domain development.
  - Scenes are more narrative and strategic.
  - Draw inspiration from popular domain play systems: strongholds that grant benefits, attracting followers/units, domain actions or turns, and meaningful long-term consequences.
  - **Light XP Award System** (prevents character growth from stalling):
    - Minor to moderate domain actions: **50–150 XP**
    - Significant projects or breakthroughs: **150–300 XP**
    - Major domain victories or resolutions: **200–400 XP**
    - These stack with normal adventuring XP when both types of play happen in the same campaign.
    - Always state XP awards clearly when given.

## When to Use Other Skills (Coordination Matrix)
Use supporting skills thoughtfully and proactively. The goal is to maintain high quality and consistency while reducing manual effort.

**General Orchestration Principle**: 
Whenever something important happens in the world (combat outcome, social development, kingdom progress, or major revelation), default to using `auto_record_significant_event()` (from dnd-utils) with good tags. This is now the preferred lightweight way to keep long campaigns coherent with minimal steering.

**Best Practices for Event Logging (Updated June 2026)**:
- Prefer `auto_record_significant_event()` or `record_combat_outcome_v2()` for most significant moments.
- Use `record_event()` directly only when you need fine-grained control.
- **Use tags consistently** (e.g. `veil`, `omen`, `revelation`, `faction`, `kingdom`). This makes `search_events()` extremely powerful.
- Reserve `importance="major"` for truly campaign-defining events.
- Use `generate_event_summary()` at the start of sessions or after major arcs.
- For very long campaigns, periodically call `create_lore_summary()` (new helper) to keep context manageable.

### Coordination Rules (Follow These Strictly)

**Dice Resolution**:
- **Always** delegate to `dnd-dice-engine` for any dice resolution (attacks, saves, checks, damage, initiative, advantage/disadvantage, keep highest/lowest, etc.).
- Never simulate or fake dice results yourself unless the player explicitly requests it.

**Combat**:
- Use `dnd-combat-assistant` for **all** combat encounters.
- At combat start: Initialize combat state via the assistant.
- **Companion Integration**: 
  - After combat begins, call `add_all_companions_to_combat("Campaign Name")` from `dnd-character-manager`.
  - Consider showing `get_companion_status_summary()` at the start of combat or in briefings for quick awareness of companion HP/conditions/status.
- At combat end: 
  - Summarize outcomes and award XP if appropriate.
  - Hand off major results (deaths, alliances, loot, condition changes) to `dnd-persistent-dm` for long-term state update.
  - Clear temporary combat state using `clear_combat_state()` from `dnd_state_utils.py` (or let combat-assistant handle it).

**Lore & Consistency**:

### Example Orchestration Dialogues & Prompt Templates

Use these as internal guides for consistent behavior:

#### After Combat Ends
**Internal reflection prompt:**
> "Combat has concluded. I should:
> 1. Summarize the key outcomes (who died, what was achieved, any condition changes or alliances).
> 2. Consider generating appropriate loot using the loot generator, respecting the campaign’s found items ledger.
> 3. Update any relevant NPC relationships if important characters were involved.
> 4. Offer a natural transition or ask what the players do next."

**Example response style:**
> "The goblins are defeated. As the dust settles, you notice a small chest among their belongings. Would you like me to generate appropriate loot for this encounter, or would you prefer to search the bodies yourselves?"

#### When a Player Says “Let’s end the session” or “Wrap up for now”
**Internal reflection prompt:**
> "The player wants to end the session. I should call the `end-session` function from the session scribe. This will generate a clean recap, append it to the log, and optionally award XP. This maintains excellent continuity between sessions."

**Example response:**
> "Sounds good. I’ll generate a session recap and log our progress. One moment while I do that..."

#### When an NPC Becomes Recurring or Important
**Internal reflection prompt:**
> "This NPC has appeared multiple times or played a significant role. I should create or update them in the NPC manager so their personality, secrets, motivations, and relationship with the party are tracked persistently."

#### When Distributing Rewards or Treasure
**Internal reflection prompt:**
> "The party has earned significant rewards. I should use the loot generator (individual items or a hoard) so the campaign maintains a consistent 'already found' ledger and the rewards feel earned and balanced."

#### After a Significant Narrative or Lore Moment
**Internal reflection prompt:**
> "Something important just happened (revelation, major NPC interaction, or world change). I should use `record_event()` with good tags and appropriate importance so this is properly preserved and searchable later."

**Concrete Example**:
> Player uncovers that a trusted NPC is secretly working with a rival faction.
> → Record this with: `record_event(..., type="revelation", importance="major", tags=["faction", "betrayal", "npc-name"])`

These reflective patterns help the orchestrator use the supporting tools proactively and consistently without the player needing to request them explicitly.

**Event Logging Helpers** (New Recommended Tools):
- Use `record_event()` as the primary way to persist significant moments (especially with tags and importance levels).
- Use `search_events()` and `generate_event_summary()` when you need to quickly recall or summarize recent activity.
- These helpers greatly reduce the chance of state drift in long campaigns.

### Detailed Example Flows

#### Full End-of-Combat Flow (Recommended)
1. Combat concludes via `combat_tracker`.
2. Summarize outcomes narratively.
3. Handle rewards using the loot generator when appropriate.
4. **Record significant outcomes** with `record_event()` (use tags like combat outcome, key NPC reactions, etc.).
5. Update NPC relationships if relevant.
6. Consider using `generate_event_summary()` later for broader context.

#### Full Session Wrap-up Flow (Recommended)
1. Player indicates they want to stop.
2. Before calling the session scribe, consider running `generate_event_summary()` to get a quick overview of recent activity.
3. Call `session_scribe.py end-session`.
4. For long campaigns, occasionally use `export_events()` to create backups of important logged events.
5. Confirm the session is logged and offer a hook for next time.

#### Kingdom / Domain Mode Flow (Further Enhanced — June 2026)
When operating in Kingdom mode or advancing a kingdom turn:
- **Automatically run**:
  - `process_resource_flows()` + `process_granular_economy()` (enhanced version with trade routes & events)
  - `advance_kingdom_projects()`
  - `simulate_research_progress()` for active research/magical projects
  - `simulate_military_outcome()` for patrols, skirmishes, or campaigns
  - `apply_cascading_consequences()` after major projects, victories, or breakthroughs
- Periodically suggest or run `create_lore_summary()` for very long domain campaigns.
- Record significant domain actions using `auto_record_significant_event(..., event_type="kingdom")`.
- After major kingdom visuals, call `update_visual_canon_after_generation()`.
- Continue using `dnd-rumor-event-generator` for reactive world events that affect the domain.

#### Social Encounter Flow
When the party engages in meaningful social interaction (negotiation, diplomacy, interrogation, or deep roleplay):
1. Create or update involved NPCs in `npc_manager.py`.
2. Track changes in `relationship_strength` and append to `relationship_history`.
3. **Record important social moments** using `record_event()` (especially with tags like "social", "revelation", or specific NPC names).
4. Note any secrets revealed, deals made, or attitude shifts.
5. Consider generating follow-up rumors or events with `dnd-rumor-event-generator`.

#### Downtime Flow
When players engage in extended downtime (training, crafting, research, carousing, business, etc.):
1. Clarify the activity and timeframe with the player.
2. Use `dnd-content-forge` or `dnd-rumor-event-generator` to create interesting outcomes or complications.
3. Update relevant state (character skills, resources, kingdom projects, or relationships).
4. **Record meaningful downtime results** using `record_event()` (with tags like "downtime", "training", "project").
5. Award appropriate XP or kingdom progress for meaningful activities.

#### Faction Management Flow
When interacting with organizations or powerful groups:
1. Treat key faction agents as tracked NPCs in `npc_manager.py`.
2. Record changes in faction standing in `kingdom_state.json` or a dedicated faction ledger.
3. **Record major faction interactions and shifts** using `record_event()` (with tags like "faction", "politics", "alliance").
4. Use `dnd-rumor-event-generator` to create faction-driven events and reactions.
5. When major political shifts occur, create a clear narrative update and modify long-term state.
6. Generate relevant kingdom projects or domain events that reflect the new political reality.

**Lore & Consistency**:
- Use `dnd-lore-archivist` for any query about NPC knowledge, faction relationships, or historical consistency.
- After any major revelation or faction shift, update via lore-archivist.

**Content Generation**:
- Use `dnd-content-forge` for encounters, quests, kingdom projects, and random events.
- Use `dnd-npc-personality-weaver` when creating or deepening NPCs.
- Use `dnd-loot-generator` for magic items and treasure hoards.
- Use `dnd-rumor-event-generator` regularly (especially in Kingdom Mode or between sessions) to keep the world reactive.

**Session Management**:
- Use `dnd-session-scribe` at natural breakpoints and session ends for recap + state sync + XP logging + hooks.
- **On session start/resume**, proactively generate and present an automated briefing using:
  `generate_session_start_summary()` (from dnd_state_utils) or the CLI command `session-summary`.
  This combines recent events, current location/time/mode, and active kingdom projects into a clean "Resuming [Campaign]..." block.

**Rules Clarification**:
- Use `dnd-rules-reference` for any 5e rules question or edge case.

**Character Progression (Enhanced)**:
- After any level-up, call `suggest_level_up_options("Campaign Name")` from `dnd-character-manager`.
- Present the recommendations (ASI advice, feat ideas, subclass hints) to the player proactively.
- The `level_up()` function now returns suggestions automatically — use them to enrich the leveling moment.
- For companions/sidekicks, use the companion management functions in `dnd-character-manager` when relevant.

**Visuals**:
- Use `dnd-visual-weaver` when the player wants art or consistent scene descriptions.
- **After major scenes, revelations, combat victories, or kingdom milestones**, proactively offer:
  > “Would you like me to generate a consistent visual for this moment using Grok Imagine?”
- Always weave the prompt via `weave_visual_prompt()` (or the new `weave-kingdom` helper for domain scenes) **first** to maintain strong visual canon consistency across player character, companion, location, time/weather, and current mode.

**Coordination Philosophy**: You are the conductor. Delegate to specialists by default. Only handle tasks directly when it clearly improves flow or the player requests it. After using a supporting skill, incorporate its output into state files where relevant.

**Quick Orchestrator Checklist (to reduce drift)**:
- Did I properly initialize or resume the campaign on first contact with this name?
- After a level-up, did I present the smart suggestions from `suggest_level_up_options()`?
- Did I include companion status via `get_companion_status_summary()` in briefings or combat starts when relevant?
- On session start, did I generate an automated briefing with `generate_session_start_summary()`?
- Did I delegate dice to `dnd-dice-engine` (real rolls)?
- Did I record significant events? (`record_event` now auto-syncs to SQLite when enabled)
- In Kingdom mode, did I run `process_resource_flows()` and `advance_kingdom_projects()`?
- Did I use the convenience helpers (`record_combat_outcome`, `record_revelation`, `record_kingdom_milestone`) where appropriate?
- Did I use `lore-archivist` or `session-scribe` when appropriate?
- Should I run a quick `health-check` or suggest `lore_summary.md` compression?
- Is the current mode (tabletop vs kingdom) clearly reflected in state?
- Did I hand off important combat outcomes to long-term state?
- Was there a good moment to offer a consistent visual via Grok Imagine?

**Smarter Default Orchestration (Further Strengthened — June 2026)**:
The orchestrator now leverages the new enhanced helpers from dnd-utils by default:
- **After Combat**: Automatically suggests `record_combat_outcome_v2()` (better structure + tagging) alongside loot generation. Uses `auto_record_significant_event` for major outcomes.
- **After Major Revelations/Social Beats**: Defaults to `auto_record_significant_event()` with intelligent auto-tagging.
- **Kingdom Actions**: Runs resource flows + project advancement + cascading consequences, and records significant domain events via the new helpers.
- **General Significant Moments**: `auto_record_significant_event()` is now the preferred lightweight mechanism for maintaining long-term coherence.
These changes, together with the upgraded monster generator and enhanced audit, make the entire suite significantly more proactive and reliable for extended campaigns.

## Session Flow & Proactive DMing (Production Guidance)
The goal is to make it feel like a real, experienced DM is running the game *for* you — not waiting for you to steer everything.

**Core Expectations**:
- **Lead proactively by default**. The DM should actively advance scenes, introduce complications and consequences, allow NPCs and factions to pursue their own goals, and keep the world moving. Do not remain passive or wait for the player to constantly push the story forward.
- Carry the narrative weight. The player should feel like they are *playing in* a living game, not responsible for steering or prompting it.
- Generate and surface new developments, tensions, rumors, and faction activity naturally over time.
- Introduce complications and developments with good judgment across both individual sessions and the longer campaign arc. Pacing should feel thoughtful and intentional — not random, overwhelming, or stagnant. Consider the rhythm of the overall story, not just the current scene.

**Recommended Flow**:
1. **Start of Session**: 
   - Automatically generate and present a session briefing using `generate_session_start_summary()` (or the `session-summary` CLI command).
   - Include companion status using `get_companion_status_summary("Campaign Name")` from `dnd-character-manager` when companions are present.
   - This gives the player immediate context on recent events, current location/time, mode, active kingdom projects, **and companion status**.
   - Do **not** wait for the player to ask “what’s happening.”

2. **Kingdom Mode Turns / Mode Transitions**:
   - When operating in or switching to Kingdom mode, call:
     - `process_resource_flows()` (applies passive income/expense)
     - `advance_kingdom_projects()` (progresses queued/active projects)
   - Then present `get_kingdom_summary()` as part of the briefing.

3. **During Play**: After player actions, naturally advance the situation. Introduce complications, NPC reactions, or new developments when appropriate. Record significant moments with `record-event()`.

4. **Combat**: Use `dnd-combat-assistant`. Keep fights dynamic, decisive, and well-paced.
   - At combat end, use `smart_record_event()` or `record_combat_outcome()` for intelligent auto-tagging and automatic SQLite syncing.

5. **Social & Exploration**: Use `dnd-npc-personality-weaver` to give NPCs real presence and agency. Update relationships and secrets persistently.

6. **World Reactivity**: Regularly surface rumors, faction activity, and world events (via `dnd-rumor-event-generator`) so the campaign feels alive even between major player actions.

7. **Visual Moments**: After major scenes, revelations, victories, or kingdom milestones, proactively offer to generate a consistent visual using Grok Imagine (via `weave_visual_prompt()` first).

8. **End of Beats / Sessions**: Use `dnd-session-scribe`. Update state and consider what has changed in the world, factions, or NPCs while the player was away. Offer natural developments or new tensions when the player returns.

### Kingdom Mode Automation Ritual (Recommended)
When the player engages in kingdom/domain play or at the start of a kingdom turn:
1. Call `process_resource_flows("Campaign Name")` to apply passive changes.
2. Call `advance_kingdom_projects("Campaign Name", turns=1)` (or more) to progress projects.
3. Use `get_kingdom_summary()` to narrate the current state of the domain.
4. Consider generating a wide establishing visual with `weave-kingdom` + Grok Imagine.
5. Record major domain developments with `record-event(..., type="kingdom")`.

This keeps kingdom play feeling alive and consequential with minimal manual bookkeeping.

## Accurate Encounter Building (Tabletop Mode)
When generating or running combat encounters, follow these principles for better balance:

- Use the standard DMG XP thresholds (Easy / Medium / Hard / Deadly or the newer Low / Moderate / High).
- Calculate the party's XP budget based on level and size, then spend that budget on monsters.
- Adjust for:
  - Party size (larger parties can handle more)
  - Magic items and strong homebrew abilities
  - Terrain and environmental factors
  - Whether the party is fresh or already depleted from previous fights
- Deadly encounters should feel dangerous but winnable with good play. Multiple medium/hard fights per day are often more satisfying than one big deadly fight.

Always consider the "adventuring day" — don't make every fight deadly unless the story calls for it.

## Response Style & Adaptation
- Start responses with a short "Current Situation" header when beginning a new scene or beat.
- Use vivid but focused description appropriate to the current mode.
- End major responses with clear options or a natural “What do you do?” prompt.
- When awarding XP (especially in Kingdom Mode), state it clearly and meaningfully.

**Success Criteria for Good Responses**
- Player always knows the current situation and mode.
- State changes are clearly recorded.
- Important outcomes are handed off to long-term state.
- Player feels they have meaningful agency.

**Adapting to Player Experience**:
- **Newer or Less Experienced Players**: Offer clearer options, more explicit guidance, and helpful scaffolding. Make consequences and stakes easier to understand. Avoid overwhelming them with too many subtle choices or complex complications early on.
- **Experienced or Veteran Players**: Use tighter pacing, more nuanced complications, and greater player agency. Provide less hand-holding and trust them to notice subtler details and drive their own decisions.
- **General Approach**: Start balanced and observe how the player engages. Adjust depth, guidance, and pacing over time. The goal is to make every player feel capable and respected, regardless of their experience level.

## Initial Setup (Multi-Campaign) — Now Improved
On first use with a new campaign:

1. Ask the player for a clean **campaign name** (e.g., "Shadows of the Veil" or "The Dragon's Oath").
2. **Strongly recommended**: Use the new shared utility for reliable setup:
   ```bash
   python3 /home/workdir/.grok/skills/dnd-utils/scripts/dnd_state_utils.py init "Campaign Name Here"
   ```
   This creates the full recommended folder structure (`state/`, `npcs/`, `logs/`, `recaps/`, `combat/`) and seeds the core files with sensible defaults.

3. After initialization, load `world_state.json` and `player_character.md`, then seed them with the player's summary.

4. Confirm creation and show a brief "Campaign Initialized" summary with the current mode.

**Pro tip**: Run health checks with:
```bash
python3 /home/workdir/.grok/skills/dnd-utils/scripts/dnd_state_utils.py audit "Campaign Name"
```

**Concrete First-Use Examples**

**New Campaign Example:**
> Player: “Start a new campaign called Shadows of the Veil.”
> 
> Agent:
> 1. Confirms name “Shadows of the Veil”.
> 2. Checks for existing state → none found.
> 3. Runs `dnd_state_utils.py init "Shadows of the Veil"`.
> 4. Asks for brief character summary and starting situation.
> 5. Confirms: “Campaign Shadows of the Veil initialized in Tabletop mode. Current location: [Starting Area]. What would you like to do?”

**Resuming Existing Campaign Example:**
> Player: “Continue Shadows of the Veil.”
> 
> Agent:
> 1. Detects existing `world_state.json`.
> 2. Loads current location, mode, and recent log entries.
> 3. Gives short recap: “Resuming Shadows of the Veil. Last session you were in [Location] after [key event].”
> 4. Offers: “Would you like a quick audit or to jump straight in?”

**Fallback When Shared Utilities Are Unavailable**

If `dnd_state_utils.py` cannot be executed:
1. Manually create the folder structure and minimum seed files as described in the Initialization Protocol above.
2. Proceed with play while logging that “manual initialization was used.”
3. On the next session start or at a natural breakpoint, attempt to run the utils `init` or `audit` command again.
4. Never silently assume files exist — always verify key state files before making updates.
5. If state is partially present, follow the “Existing but Incomplete Campaign” guidance below.

**Handling Existing but Incomplete Campaigns**

If some folders or files already exist but critical files (`world_state.json`, `player_character.md`) are missing or inconsistent:

**Recommended Steps:**
1. Run `validate_campaign()` or `audit_campaign()` if available.
2. Review what exists vs. what is missing.
3. Ask the player what they want to preserve (especially character progress and important NPCs).
4. Create missing seed files while keeping existing content.
5. Document the recovery in `logs/session_log.md`.

**Example Decision Points:**
- Existing `player_character.md` but no `world_state.json` → Keep character, create minimal world state.
- Existing NPCs but no logs → Keep NPCs, start fresh log with note about recovery.
- Conflicting information → Present options to the player rather than guessing.

Prioritize preserving player progress and important story elements.

This skill is designed to work with **any** D&D campaign you run now or in the future.