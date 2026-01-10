import random
import os
import glob

# Heuristic mapping based on observed prefixes
# B = Base? F = Friendly? I = Intense?
# Code mapping (Hypothetical based on sound names):
# ANI = Animation/Anime? (Cute)
# BRA = Brawl? (Aggressive/Playful)
# BAC = Back? (Neutral)
# SPI = Spy? (Suspicious/Alert)
# WHO = Who? (Curious/Sleepy owl sounds?)
# NUL = Null (Zen/Void)

PREFIX_MAP = {
    "Playful": ["B_BRA", "B_ANI", "I_MEG"],
    "Content": ["B_CAN", "B_MAT", "I_CAN"],
    "Relaxed": ["B_MAT", "I_MAT", "B_NUL"],
    "Grumpy": ["I_BAC", "F_BAC", "I_MAG"],
    "Sleepy": ["B_WHO", "F_WHO", "I_WHO"],
    "Alert": ["B_SPI", "I_SPI", "F_SPI"],
    "Zen": ["B_NUL", "I_NUL"],
    "Irritated": ["B_MAG", "F_MAG"],
    "Moody": ["B_MIN", "F_MIN"],
    "Curious": ["B_JJX", "B_DAK"],
    "Mischievous": ["B_NIG", "I_NIG"],
}

class CatAudio:
    _cached_files = []

    @classmethod
    def _scan_files(cls):
        """Scan definitions once."""
        if cls._cached_files:
            return
        
        # In a real app we might use `os.listdir` on startup
        # For now, we assume the static dir exists at a relative path
        base_dir = os.path.join(os.getcwd(), "static/catsounds")
        if os.path.exists(base_dir):
            cls._cached_files = [f for f in os.listdir(base_dir) if f.endswith(".wav")]

    @classmethod
    def get_sound_for_state(cls, state: str) -> str:
        """
        Get a random sound file path for a given state.
        Default to a comprehensive 'Meow' if state unknown.
        """
        cls._scan_files()
        
        prefixes = PREFIX_MAP.get(state, ["B_ANI", "B_CAN"])
        
        # Filter candidates
        candidates = [
            f for f in cls._cached_files 
            if any(f.startswith(p) for p in prefixes)
        ]
        
        if not candidates:
            # Fallback to any file if specific ones missing
            if cls._cached_files:
                return random.choice(cls._cached_files)
            return "B_ANI01_MC_FN_SIM01_101.wav" # Ultimate fallback
            
        return random.choice(candidates)

