import random

state = {
    "familiarity": {},
    "emotions": {},
    "last_speaker": None
}

EVENT_DELTAS = {
    "login_success": {"pleasure": 0.1, "arousal": 0.05, "dominance": 0.1},
    "login_failure": {"pleasure": -0.1, "arousal": 0.1, "dominance": -0.05},
    "friend_added": {"pleasure": 0.15, "arousal": 0.1, "dominance": 0.05},
    "form_error": {"pleasure": -0.05, "arousal": 0.05, "dominance": -0.1},
}

def init_cat(name):
    state["familiarity"][name] = 0
    state["emotions"][name] = {"pleasure": 0, "arousal": 0, "dominance": 0}

def update_emotion(name, event):
    delta = EVENT_DELTAS.get(event, {})
    for k in ["pleasure", "arousal", "dominance"]:
        state["emotions"][name][k] = max(
            -1, min(1, state["emotions"][name][k] + delta.get(k, 0) + random.uniform(-0.01, 0.01))
        )

for name in [
    "beans","miso","tofu","ash","delta","patch","static","hex","null","root"
]:
    init_cat(name)