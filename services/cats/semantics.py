"""
Cat Semantics - services/cats/semantics.py

Maps numerical Affinity scores to Faction-specific status labels.
Source: User "Love/Hate" PDF equivalent.
"""

# Affinity Thresholds
# (Min Score, Status Key)
TIERS = [
    (-90, "severed"),
    (-70, "hostile"),
    (-40, "rival"),
    (-10, "wary"),
    (10, "neutral"),     # -10 to 10
    (30, "acquaintance"),
    (50, "friendly"),
    (70, "trusted"),
    (90, "close"),
    (101, "ally")        # > 90
]

def get_status_key(affinity: float, interaction_count: int = 0) -> str:
    """
    Determine the base status key from affinity.
    """
    if interaction_count == 0:
        return "stranger"
        
    for threshold, key in TIERS:
        if affinity < threshold:
            return key
            
    return "ally" # Fallback

FACTION_STATUS_MAP = {
    # 1. THE CONCRETE SENTINELS
    "The Concrete Sentinels": {
        "stranger": "Unmarked",
        "acquaintance": "Seen you",
        "neutral": "No issue",
        "friendly": "You're clear",
        "trusted": "You pass",
        "close": "Inside the line",
        "ally": "We hold together",
        "rival": "Pressure point",
        "wary": "Watching you",
        "hostile": "Do not cross",
        "severed": "Wall up"
    },
    # 2. THE VELVET ANARCHS
    "The Velvet Anarchs": {
        "stranger": "Who you?",
        "acquaintance": "You again",
        "neutral": "Whatever",
        "friendly": "You're fun",
        "trusted": "You get it",
        "close": "You stay",
        "ally": "Ride with me",
        "rival": "Spicy",
        "wary": "Side-eye",
        "hostile": "Problem. Mrrp.",
        "severed": "Bored now"
    },
    # 3. THE STATIC MONKS
    "The Static Monks": {
        "stranger": "Present",
        "acquaintance": "Known",
        "neutral": "Balanced",
        "friendly": "Accepted",
        "trusted": "Aligned",
        "close": "Here",
        "ally": "Same pace",
        "rival": "Noise",
        "wary": "Uneven",
        "hostile": "Disruptive",
        "severed": "Released"
    },
    # 4. THE NEON CLAWS
    "The Neon Claws": {
        "stranger": "Who?",
        "acquaintance": "You",
        "neutral": "Meh",
        "friendly": "Cool",
        "trusted": "My side",
        "close": "Locked in",
        "ally": "Run it",
        "rival": "Competition",
        "wary": "Testy",
        "hostile": "Beef",
        "severed": "Dead to me"
    },
    # 5. THE SOFT COLLAPSE
    "The Soft Collapse": {
        "stranger": "Hm?",
        "acquaintance": "Oh",
        "neutral": "Fine",
        "friendly": "Nice",
        "trusted": "Safe",
        "close": "Stay",
        "ally": "Same couch",
        "rival": "Annoying",
        "wary": "Too loud",
        "hostile": "No",
        "severed": "Gone. Zzz"
    },
    # 6. THE PERIPHERAL EYE
    "The Peripheral Eye": {
        "stranger": "Unknown",
        "acquaintance": "Noted",
        "neutral": "Watching",
        "friendly": "Okay...",
        "trusted": "Verified",
        "close": "Safe",
        "ally": "Cover me",
        "rival": "Threat",
        "wary": "Too close",
        "hostile": "Danger. Hiss",
        "severed": "Avoid"
    },
    # 7. THE BONDED MASS
    "The Bonded Mass": {
        "stranger": "Who's that?",
        "acquaintance": "Oh! You!",
        "neutral": "Hi",
        "friendly": "You're nice",
        "trusted": "You're ours",
        "close": "Stay here",
        "ally": "Together",
        "rival": "Hands off",
        "wary": "Careful",
        "hostile": "Not welcome",
        "severed": "Lost"
    },
    # 8. THE COLD ITERATION
    "The Cold Iteration": {
        "stranger": "Irrelevant",
        "acquaintance": "Recognized",
        "neutral": "Neutral",
        "friendly": "Acceptable",
        "trusted": "Cleared",
        "close": "Rare",
        "ally": "Useful",
        "rival": "Obstacle",
        "wary": "Unstable",
        "hostile": "Remove",
        "severed": "Deleted"
    },
    # 9. THE RESTLESS GRID
    "The Restless Grid": {
        "stranger": "New",
        "acquaintance": "You again?",
        "neutral": "Meh",
        "friendly": "Alright",
        "trusted": "Interesting",
        "close": "Fun",
        "ally": "Let's go",
        "rival": "Tension",
        "wary": "Eh...",
        "hostile": "Bad vibes",
        "severed": "Next"
    },
    # 10. THE QUIET PRESSURE
    "The Quiet Pressure": {
        "stranger": "Unfamiliar",
        "acquaintance": "Noted",
        "neutral": "Fine",
        "friendly": "Easy",
        "trusted": "Steady",
        "close": "Here",
        "ally": "We endure",
        "rival": "Persistent",
        "wary": "Careful",
        "hostile": "No",
        "severed": "Ended"
    }
}

def get_faction_label(faction_name: str, affinity: float, interaction_count: int = 1) -> str:
    """
    Get the specific Label for a Faction and Affinity.
    """
    key = get_status_key(affinity, interaction_count)
    return FACTION_STATUS_MAP.get(faction_name, FACTION_STATUS_MAP["The Concrete Sentinels"]).get(key, "Unknown")

# 30-Tier Nuanced Relationship list
# We map these using a combination of Affinity (-100 to 100) and Interaction Count.
DETAILED_RELATIONSHIPS = [
    "Unknown",          # 0
    "Just Met",         # 1
    "Seen You Around",  # 2
    "Neutral",          # 3
    "Cool With",        # 4
    "Low-Key Cool",     # 5
    "Polite",           # 6
    "Solid",            # 7
    "Trusted",          # 8
    "Tight",            # 9
    "Inner Paw",        # 10
    "OG",               # 11
    "Learned From",     # 12 (High Affinity + High Interactions)
    "Respected",        # 13
    "Working Together", # 14
    "Business Only",    # 15 (Neutral Affinity + High Interactions)
    "Competing",        # 16
    "Opps",             # 17
    "Tense",            # 18
    "Strained",         # 19
    "Keeping Distance", # 20
    "Cold",             # 21
    "Weird Vibes",      # 22
    "Watching You",     # 23
    "Don’t Trust",      # 24
    "Hostile",          # 25
    "Beefing",          # 26
    "Smoke",            # 27
    "On Thin Fur",      # 28 (Very Low)
    "Cut Off"           # 29 (Lowest)
]

def get_detailed_status(affinity: float, interactions: int) -> str:
    """
    Get a granular 'Street Status' based on Affinity (-100 to 100).
    """
    # Special Case: No interactions
    if interactions == 0:
        return DETAILED_RELATIONSHIPS[0] # Unknown
        
    # Early Game: Low interactions overrides pure affinity (unless hostile)
    # If purely neutral/positive but barely met:
    if interactions <= 2 and -10 <= affinity <= 10:
        return DETAILED_RELATIONSHIPS[1] # "Just Met"
        
    if interactions <= 5 and -10 <= affinity <= 20:
        return DETAILED_RELATIONSHIPS[2] # "Seen You Around"

    # Map Affinity to Index (Basic approach)
    # Range is -100 to 100.
    
    if affinity >= 0:
        # 0 to 100. 
        score = affinity
        if score < 10: return "Neutral"
        if score < 20: return "Cool With"
        if score < 30: return "Low-Key Cool"
        if score < 40: return "Polite"
        if score < 50: return "Solid"
        if score < 60: return "Trusted"
        if score < 70: return "Tight"
        if score < 80: return "Inner Paw"
        if score < 90: return "OG"
        return "Respected" # Top Tier
    else:
        # Negative
        score = abs(affinity)
        if score < 10: return "Weird Vibes"
        if score < 20: return "Tense"
        if score < 30: return "Strained"
        if score < 40: return "Keeping Distance"
        if score < 50: return "Cold"
        if score < 60: return "Watching You"
        if score < 70: return "Don’t Trust"
        if score < 80: return "Hostile"
        if score < 90: return "Beefing"
        return "Cut Off" # Bottom Tier

# Vocalization Map (Idle Sounds)
FACTION_VOCAL_MAP = {
    "The Concrete Sentinels": {
        "stranger": "…", "neutral": "Hrm.", "friendly": "Mrr.", 
        "trusted": "Mrrm.", "close": "Prt.", "wary": "Hrr.", 
        "hostile": "HISS.", "severed": "—"
    },
    "The Velvet Anarchs": {
        "stranger": "Mrr?", "neutral": "Chrp.", "friendly": "Brrp!", 
        "trusted": "Mrrrp.", "close": "Prra!", "wary": "Tsk.", 
        "hostile": "Hss—", "severed": "Pfft."
    },
    "The Static Monks": {
        "stranger": "Mm.", "neutral": "Mmm.", "friendly": "Prr.", 
        "trusted": "Prrrr.", "close": "Mm.", "wary": "Hm.", 
        "hostile": "—", "severed": "…"
    },
    "The Neon Claws": {
        "stranger": "Eh.", "neutral": "Tch.", "friendly": "Brr.", 
        "trusted": "Rrr.", "close": "Rrrp.", "wary": "Hrk.", 
        "hostile": "HISS!", "severed": "Snap."
    },
    "The Soft Collapse": {
        "stranger": "Huh…", "neutral": "Mm.", "friendly": "Prr.", 
        "trusted": "Prr…", "close": "Zzz.", "wary": "Eh.", 
        "hostile": "Tsk.", "severed": "Zz."
    },
    "The Peripheral Eye": {
        "stranger": "?", "neutral": "Chrk.", "friendly": "Mrr.", 
        "trusted": "Prr.", "close": "Prrt.", "wary": "Hrk!", 
        "hostile": "HISS—", "severed": "Skrr."
    },
    "The Bonded Mass": {
        "stranger": "Mrr?", "neutral": "Chirp.", "friendly": "Brrp!", 
        "trusted": "Prrr!", "close": "Prrrp.", "wary": "Mm?", 
        "hostile": "Hss!", "severed": "Mrr…"
    },
    "The Cold Iteration": {
        "stranger": ".", "neutral": "Hm.", "friendly": "Mm.", 
        "trusted": "Prr.", "close": "M.", "wary": "Tsk.", 
        "hostile": "H.", "severed": "—"
    },
    "The Restless Grid": {
        "stranger": "Oh?", "neutral": "Eh.", "friendly": "Chrp!", 
        "trusted": "Brrp.", "close": "Prra!", "wary": "Uh.", 
        "hostile": "Hss?", "severed": "Next."
    },
    "The Quiet Pressure": {
        "stranger": "Mm.", "neutral": "Hm.", "friendly": "Prr.", 
        "trusted": "Prrrr.", "close": "Prr.", "wary": "Hrm.", 
        "hostile": "No.", "severed": "…"
    }
}

def get_idle_vocalization(faction_name: str, affinity: float, interactions: int) -> str:
    """
    Get the idle sound text based on relationship.
    """
    if interactions == 0:
        cat = "stranger"
    elif affinity <= -90:
        cat = "severed"
    elif affinity <= -50:
        cat = "hostile"
    elif affinity < 10: # -50 to 10 covers Wary/Rival/Weird Vibes
        cat = "wary"
    elif affinity < 50: # 10 to 50 covers Neutral/Polite/Cool
        cat = "neutral"
    elif affinity < 80: # 50 to 80 covers Friendly/Solid/Trusted
        cat = "friendly"
    elif affinity < 95: # 80 to 95 covers Trusted/Tight/Inner Paw
        cat = "trusted"
    else: # 95+ covers Close/Ally/OG
        cat = "close"
        
    return FACTION_VOCAL_MAP.get(faction_name, FACTION_VOCAL_MAP["The Concrete Sentinels"]).get(cat, ".")
