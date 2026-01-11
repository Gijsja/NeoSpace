from dialogue_factory import generate_dialogues

BASE_CATS = [
    ("beans", 10, ["login_attempt","login_success","login_failure","friend_added"], False, 0.1),
    ("miso", 5, ["timeout","idle","form_error","message_sent"], True, 0.5),
    ("tofu", 6, ["page_load","idle","login_success","post_created"], True, 0.3),
    ("ash", 4, ["idle","timeout"], True, 0.6),
    ("delta", 7, ["post_created","message_sent"], False, 0.2),
    ("patch", 3, ["idle"], True, 0.8),
    ("static", 8, ["form_error","system_error"], False, 0.2),
    ("hex", 6, ["page_load","idle"], True, 0.4),
    ("null", 2, ["idle"], True, 0.9),
    ("root", 9, ["page_load","login_success","login_failure"], False, 0.1),
]

INTENTS = {
    "login_attempt": "ack",
    "login_success": "approval",
    "login_failure": "deny",
    "friend_added": "approval",
    "timeout": "observe",
    "idle": "observe",
    "form_error": "deny",
    "message_sent": "post",
    "post_created": "post",
    "page_load": "load",
    "system_error": "deny"
}

CATS = []

for name, priority, triggers, observer, silence in BASE_CATS:
    cat = {
        "name": name,
        "priority": priority,
        "triggers": triggers,
        "global_observer": observer,
        "silence_bias": silence,
        "intents": {k:v for k,v in INTENTS.items() if k in triggers},
        "avatars": {
            "cute": "https://placecats.com/200/200",
            "pirate": "https://placecats.com/200/200?random=pirate",
            "formal": "https://placecats.com/200/200?random=tuxedo"
        }
    }

    if name == "root":
        cat["dominance_weight"] = 1.5
        cat["allowed_modes"] = ["formal","pirate"]

    cat["dialogues"] = generate_dialogues(name)
    CATS.append(cat)