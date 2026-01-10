# Cat Service Facade - services/cats/__init__.py
# The public API for the CatSystem.
# Combines Brain (Logic), Store (DB), and Audio (Assets).

from typing import Dict, Any, Optional
import os
from .brain import CatBrain
from .store import CatStore
from .audio import CatAudio
from .dialogue import CatDialogue
from .semantics import get_faction_label, get_detailed_status, get_idle_vocalization

def get_all_cats():
    # Get all cats with their current emotional state.
    cats = CatStore.get_all_cats()
    for cat in cats:
        # Calculate Named State from PAD
        pad = (
            cat.get("pleasure") or 0.0,
            cat.get("arousal") or 0.0,
            cat.get("dominance") or 0.0
        )
        cat["state_name"] = CatBrain.get_named_state(pad)
    return cats

def get_cat_by_name(name: str):
    return CatStore.get_cat_by_name(name)

def trigger_event(cat_name: str, event: str, user_id: Optional[int] = None) -> Dict[str, Any]:
    # Trigger an event for a specific cat (or all watching cats).
    # Returns the reaction (lines, sound, mechanics).
    cat = CatStore.get_cat_by_name(cat_name)
    if not cat:
        return {"error": "Cat not found"}

    # 1. Get Current State & Faction
    current_pad = (
        cat.get("pleasure") or 0.0,
        cat.get("arousal") or 0.0,
        cat.get("dominance") or 0.0
    )
    faction_name = cat.get("faction_name", "The Concrete Sentinels")

    # 2. Calculate Impact
    # Returns ((pleasure, arousal, dominance), opinion_delta)
    impact_tuple = CatBrain.get_deed_impact(event, faction_name) 
    pad_impact, opinion_delta = impact_tuple
    
    # 3. Memory & Relationship (The Rimworld Part)
    affinity = 0.0
    if user_id:
        # Log the deed (Memory)
        CatStore.add_memory(cat["id"], user_id, event, opinion_delta)
        
        # Determine Affinity
        affinity = CatStore.get_relationship(cat["id"], user_id)
        
    # 4. Calculate New State (Global Mood)
    new_pad = CatBrain.calculate_new_pad(current_pad, pad_impact)
    
    # TODO: Save State (CatStore.update_cat_state)
    
    # 5. Determine Output
    state_name = CatBrain.get_named_state(new_pad)
    sound = CatAudio.get_sound_for_state(state_name)
    
    # Get Mode (default to cute if not in DB doc)
    mode = cat.get("mode", "cute")
    
    # 6. Dialogue Override based on Affinity/Love/Hate
    # Special Case: Idle calls use the Vocal Map
    if event == "idle":
        # Calculate interactions for idle too (if possible, though idle is usually broadcast)
        # If user_id is provided (e.g. user clicked idle?), use it. 
        # But 'idle' is often global. If global, interaction_count might be 0 relative to "everyone".
        # For now, if we have a user_id context, use it.
        i_count = 0
        if user_id:
            i_count = CatStore.get_interaction_count(cat["id"], user_id)
        line = get_idle_vocalization(faction_name, affinity, interactions=i_count)
    else:
        line = CatDialogue.get_line(event, mode)
        
        if affinity < -20:
            line = f"*Hisses at you* ({line})"
        elif affinity > 20:
            line = f"💖 {line} 💖"
        
    # 7. Get Faction Status Label & Detailed Tag
    # faction_name is already retrieved above
    interaction_count = 0
    if user_id:
        interaction_count = CatStore.get_interaction_count(cat["id"], user_id)
        
    rel_label = get_faction_label(faction_name, affinity, interaction_count=interaction_count) 
    rel_tag = get_detailed_status(affinity, interactions=interaction_count)
    
    return {
        "cat": cat_name,
        "state": state_name,
        "pad": new_pad,
        "sound": sound,
        # Default Avatar Logic with Dynamic State Fallback
        "avatar": (lambda: 
            f"/static/images/cats/{cat_name}_{state_name.lower()}.png" 
            if os.path.exists(os.path.join(os.getcwd(), f"static/images/cats/{cat_name}_{state_name.lower()}.png")) 
            else (cat.get("avatar_url") or f"/static/images/cats/{cat_name}.png")
        )(),
        "line": line,
        "affinity": affinity,
        "relationship_label": rel_label,
        "status_tag": rel_tag
    }

def seed_db():
    # Utility to seed the new tables.
    # Define Base Cats (Legacy/Core definitions)
    BASE_CATS = [
        {"name": "beans", "priority": 10, "triggers": ["login_attempt", "login_success"], "silence_bias": 0.1, "global_observer": False},
        {"name": "miso", "priority": 5, "triggers": ["timeout", "idle"], "silence_bias": 0.5, "global_observer": True},
        {"name": "tofu", "priority": 6, "triggers": ["page_load", "idle"], "silence_bias": 0.3, "global_observer": True},
        {"name": "ash", "priority": 4, "triggers": ["idle"], "silence_bias": 0.6, "global_observer": True},
        {"name": "delta", "priority": 7, "triggers": ["post_created"], "silence_bias": 0.3, "global_observer": False},
        {"name": "patch", "priority": 3, "triggers": ["idle"], "silence_bias": 0.7, "global_observer": True},
        {"name": "static", "priority": 8, "triggers": ["form_error"], "silence_bias": 0.1, "global_observer": False},
        {"name": "hex", "priority": 6, "triggers": ["page_load"], "silence_bias": 0.4, "global_observer": True},
        {"name": "null", "priority": 2, "triggers": ["idle"], "silence_bias": 0.9, "global_observer": True},
        {"name": "root", "priority": 9, "triggers": ["login_success"], "silence_bias": 0.2, "global_observer": False},
        {"name": "glitch", "priority": 7, "triggers": ["form_error"], "silence_bias": 0.2, "global_observer": True},
        {"name": "neon", "priority": 6, "triggers": ["post_created"], "silence_bias": 0.3, "global_observer": False}
    ]
    CatStore.seed_personalities(BASE_CATS)
    CatStore.seed_bot_users(BASE_CATS)
    return {"status": "seeded", "count": len(BASE_CATS)}
