"""Structured 5e rules reference data for rules_cheatsheet.py."""

from __future__ import annotations

from typing import Any, Dict

CHEATSHEET: Dict[str, Dict[str, Any]] = {
    "advantage": {
        "summary": "Roll 2d20, take the higher result.",
        "details": [
            "Multiple sources of advantage still roll only 2d20.",
            "Advantage and disadvantage on the same roll cancel out.",
        ],
        "tags": ["rolls", "combat"],
    },
    "disadvantage": {
        "summary": "Roll 2d20, take the lower result.",
        "details": [
            "Multiple sources of disadvantage still roll only 2d20.",
            "Advantage and disadvantage cancel — roll a single d20.",
        ],
        "tags": ["rolls", "combat"],
    },
    "concentration": {
        "summary": "One concentration spell at a time; CON save DC 10 or half damage taken (whichever higher).",
        "details": [
            "Lose concentration when incapacitated or when you cast another concentration spell.",
            "DM may call for CON save on environmental hazards while concentrating.",
        ],
        "tags": ["spells", "combat"],
    },
    "death_saves": {
        "summary": "At 0 HP: roll d20 each turn — 10+ success, 9- failure; 3 of either stabilizes or kills.",
        "details": [
            "Natural 20: regain 1 HP. Natural 1: counts as 2 failures.",
            "Damage while at 0 HP causes 1 failure (2 on crit).",
        ],
        "tags": ["combat", "survival"],
    },
    "opportunity_attack": {
        "summary": "When a creature you can see leaves your reach, one melee attack as a reaction.",
        "details": [
            "Disengage prevents opportunity attacks from that creature.",
            "Forced movement does not provoke unless the mover uses its own movement.",
        ],
        "tags": ["combat", "reactions"],
    },
    "grapple": {
        "summary": "Special melee attack: Athletics vs Athletics or Acrobatics; target is grappled (speed 0).",
        "details": [
            "Escape: action, Athletics or Acrobatics vs grappler's Athletics.",
            "Moving a grappled creature costs double movement.",
        ],
        "tags": ["combat", "conditions"],
    },
    "cover": {
        "summary": "Half cover +2 AC/DEX saves; three-quarters +5; total cover cannot be targeted.",
        "details": ["DM adjudicates line of sight and obstruction."],
        "tags": ["combat"],
    },
    "conditions": {
        "summary": "Standard conditions include Blinded, Charmed, Frightened, Grappled, Incapacitated, and more.",
        "details": [
            "Incapacitated: can't take actions or reactions.",
            "Unconscious: incapacitated, drops items, auto-fail STR/DEX saves, attacks have advantage.",
        ],
        "tags": ["conditions"],
    },
    "unconscious": {
        "summary": "Incapacitated, can't move or speak, drops held items, auto-fails STR/DEX saves, attacks against have advantage.",
        "details": ["Any hit within 5 ft is a critical hit if the attacker is within 5 feet."],
        "tags": ["conditions"],
    },
    "prone": {
        "summary": "Melee attacks against have advantage; ranged attacks have disadvantage.",
        "details": ["Standing costs half movement. Crawling costs 1 ft per 1 ft moved."],
        "tags": ["conditions"],
    },
    "stunned": {
        "summary": "Incapacitated, can't move, can speak falteringly, auto-fails STR/DEX saves, attacks have advantage.",
        "details": [],
        "tags": ["conditions"],
    },
    "paralyzed": {
        "summary": "Incapacitated, can't move or speak, auto-fails STR/DEX saves, attacks have advantage.",
        "details": ["Any hit within 5 ft is a critical hit."],
        "tags": ["conditions"],
    },
    "restrained": {
        "summary": "Speed 0, disadvantage on attacks and DEX saves, attacks against have advantage.",
        "details": [],
        "tags": ["conditions"],
    },
    "invisible": {
        "summary": "Heavily obscured for hiding; attacks against have disadvantage, your attacks have advantage.",
        "details": ["Ends when you attack or cast a spell."],
        "tags": ["conditions"],
    },
    "exhaustion": {
        "summary": "Six levels with escalating penalties; long rest removes 1 level (with exceptions).",
        "details": [
            "Level 1: disadvantage on ability checks.",
            "Level 3: disadvantage on attacks and saves.",
            "Level 6: death.",
        ],
        "tags": ["survival"],
    },
    "short_rest": {
        "summary": "At least 1 hour; spend Hit Dice to heal; regain some class resources per class features.",
        "details": ["You can spend one or more Hit Dice, up to your maximum."],
        "tags": ["rest"],
    },
    "long_rest": {
        "summary": "At least 8 hours; regain all HP, half level in Hit Dice (min 1), restore spell slots per class.",
        "details": ["Only one long rest per 24 hours."],
        "tags": ["rest"],
    },
    "spell_slots": {
        "summary": "Casters have a table of slots by level; casting uses a slot of that level or higher.",
        "details": ["Cantrips don't use slots. Upcasting uses higher slot for stronger effect."],
        "tags": ["spells"],
    },
    "saving_throw": {
        "summary": "d20 + ability modifier + proficiency (if proficient) vs DC.",
        "details": ["Natural 1 is not an auto-fail on saves in 5e (unless a house rule)."],
        "tags": ["rolls"],
    },
    "ability_check": {
        "summary": "d20 + ability modifier + proficiency (if proficient in skill) vs DC.",
        "details": ["Group checks: half the party must succeed for group success (typical)."],
        "tags": ["rolls"],
    },
    "critical_hit": {
        "summary": "Natural 20 on attack roll hits and you roll extra damage dice (not modifiers twice).",
        "details": ["Some features expand crit range (e.g. 19-20)."],
        "tags": ["combat"],
    },
    "two_weapon_fighting": {
        "summary": "Bonus action off-hand attack when wielding light melee weapons in each hand.",
        "details": ["Off-hand doesn't add ability modifier to damage unless you have the fighting style."],
        "tags": ["combat"],
    },
    "ready_action": {
        "summary": "Use your action to Ready; trigger uses your reaction with the chosen action.",
        "details": ["Spell readied uses concentration until triggered or start of next turn."],
        "tags": ["combat", "actions"],
    },
    "help_action": {
        "summary": "Grant ally advantage on one ability check or attack against a foe within 5 ft of you.",
        "details": ["Must be before the ally rolls."],
        "tags": ["combat", "actions"],
    },
    "dash": {
        "summary": "Gain extra movement equal to your speed for the turn.",
        "details": [],
        "tags": ["combat", "actions"],
    },
    "disengage": {
        "summary": "Your movement doesn't provoke opportunity attacks for the rest of the turn.",
        "details": [],
        "tags": ["combat", "actions"],
    },
    "hide": {
        "summary": "Dexterity (Stealth) check opposed by passive Perception.",
        "details": ["Need obscurement or cover; moving out of hide may reveal you."],
        "tags": ["exploration"],
    },
    "surprise": {
        "summary": "Creatures unaware at start of combat are surprised and can't act/move on first turn.",
        "details": ["Surprise ends after each creature's first turn in combat."],
        "tags": ["combat"],
    },
    "initiative": {
        "summary": "Dexterity check sets turn order; ties: DM decides or reroll.",
        "details": ["Some features add bonuses to initiative."],
        "tags": ["combat"],
    },
    "attunement": {
        "summary": "Most magic items require attunement; max 3 attuned items unless feature says otherwise.",
        "details": ["Attuning takes a short rest with the item in hand."],
        "tags": ["items"],
    },
    "darkvision": {
        "summary": "See in dim light as bright light within range; darkness as dim light.",
        "details": ["No color in darkness-only areas."],
        "tags": ["exploration"],
    },
}

CONDITION_ALIASES = {
    "blinded": "conditions",
    "charmed": "conditions",
    "frightened": "conditions",
    "grappled": "grapple",
    "incapacitated": "conditions",
    "poisoned": "conditions",
    "petrified": "conditions",
}

TOPIC_ALIASES = {
    "adv": "advantage",
    "disadv": "disadvantage",
    "death_save": "death_saves",
    "opportunity_attacks": "opportunity_attack",
    "grappling": "grapple",
    "oa": "opportunity_attack",
    "crit": "critical_hit",
    "twf": "two_weapon_fighting",
    "help": "help_action",
}