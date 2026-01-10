"""
Cat Brain - services/cats/brain.py

Pure logic for Emotional Intelligence.
Handles PAD (Pleasure, Arousal, Dominance) calculations and State determination.
"""
from typing import Tuple, Dict, Optional

# PAD Values: -1.0 to 1.0
PAD = Tuple[float, float, float]

class CatBrain:
    def __init__(self):
        pass

    @staticmethod
    def calculate_new_pad(current_pad: PAD, deed_impact: PAD, decay: float = 0.1) -> PAD:
        """
        Calculate new PAD state based on a deed and natural decay.
        
        Args:
            current_pad: (Pleasure, Arousal, Dominance)
            deed_impact: The emotional impact of the event (delta P, A, D)
            decay: How much the emotion returns to neutral (0,0,0) per tick/event.
        """
        p, a, d = current_pad
        dp, da, dd = deed_impact

        # Apply Impact
        p += dp
        a += da
        d += dd

        # Apply Decay (Return to 0)
        # We only decay if no impact? Or always? Let's say always.
        p = p * (1 - decay)
        a = a * (1 - decay)
        d = d * (1 - decay)

        # Clamp to -1.0 to 1.0
        return (
            max(-1.0, min(1.0, p)),
            max(-1.0, min(1.0, a)),
            max(-1.0, min(1.0, d))
        )

    @staticmethod
    def get_named_state(pad: PAD) -> str:
        """
        Map PAD values to one of the 50 Named States.
        This is a simplified distance-based mapping to centroids.
        """
        p, a, d = pad
        
        # Simplified logic for now - we will expand this to full 50 map later
        # For now, quadrant based:
        
        if p > 0.3:
            if a > 0.3: return "Playful"    # High P, High A
            if a < -0.3: return "Relaxed"   # High P, Low A
            return "Content"                # High P, Mid A
        elif p < -0.3:
            if a > 0.3: return "Irritated"  # Low P, High A
            if a < -0.3: return "Grumpy"    # Low P, Low A
            return "Moody"                  # Low P, Mid A
        else:
            # Mid Pleasure
            if a > 0.5: return "Alert"
            if a < -0.5: return "Sleepy"
            return "Zen"

    @staticmethod
    def get_deed_impact(event: str, faction_name: str) -> Tuple[PAD, float]:
        """
        Determine impact based on Event + Faction.
        """
        # Return: (PAD Tuple, Opinion Delta for User)
        # Opinion Delta: How much this event makes the cat like/dislike the USER.
        base_impacts = {
            "login_success": ((0.3, 0.1, 0.1), 5.0),    # They showed up! +5
            "login_failure": ((-0.1, 0.2, 0.0), -2.0),  # Clumsy. -2
            "system_error": ((-0.4, 0.1, -0.2), -10.0), # You broke it! -10
            "timeout": ((-0.1, -0.3, 0.0), -1.0),       # Boring. -1
            "friend_added": ((0.4, 0.2, 0.1), 10.0),    # Networking! +10
            "post_created": ((0.2, 0.2, 0.1), 5.0),     # Content! +5
            "idle": ((0.0, -0.1, 0.0), 0.0),
        }
        
        base_pad, base_op = base_impacts.get(event, ((0,0,0), 0.0))
        p, a, d = base_pad
        op = base_op

        # FACTION MODIFIERS
        if faction_name == "The Velvet Anarchs":
            # Anarchs love chaos (errors) and hate boredom (timeout)
            if event == "system_error":
                p += 0.5 # They find it funny
                d += 0.2
                op = 5.0 # They like you for breaking it
            if event == "timeout":
                op = -5.0 # Bore them and they hate you
                
        elif faction_name == "The Concrete Sentinels":
            # Sentinels value stability. Hate errors. Love login/presence.
            if event == "system_error":
                d -= 0.5 # They feel loss of control
                op = -20.0 # Strict punishment
            if event == "login_success":
                op = 10.0 # Promptness rewarded

        elif faction_name == "The Static Monks":
            # Dampen all emotional reactions
            p *= 0.5
            a *= 0.5
            d *= 0.5
            # They don't care much
            op *= 0.5

        elif faction_name == "The Neon Claws":
            # Aggressive. 
            if event == "post_created":
                d += 0.3 # Competition excites them
            if event == "login_failure":
                d += 0.4 # They laugh at your weakness
                op = -5.0 # Disdain

        return ((p, a, d), op)
