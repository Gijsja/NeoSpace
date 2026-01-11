import random

TEMPLATES = {
    "cute": {
        "ack": ["hi {name}.", "meow. go ahead.", "hey friend."],
        "approval": ["yay. welcome.", "hi. good to see.", "meow. you're in."],
        "deny": ["aw. try again.", "oops. no.", "meow. not yet."],
        "signup": ["hi new friend.", "yay. join us.", "meow. welcome."],
        "post": ["nice post.", "yay. shared.", "meow. cool."],
        "observe": ["still here.", "meow. waiting.", "hi. lurking."],
        "load": ["hi. system on.", "meow. loading."],
        "approve": ["yes. proceed.", "meow. access granted."]
    },
    "pirate": {
        "ack": ["ahoy {name}.", "arr. try yer luck."],
        "approval": ["yo ho. welcome.", "arr. aboard."],
        "deny": ["avast. no entry.", "blimey. denied."],
        "signup": ["ahoy new mate.", "join the crew."],
        "post": ["fine booty.", "yo ho. shared."],
        "observe": ["still adrift.", "watching seas."],
        "load": ["ship ready.", "yo ho. loading."],
        "approve": ["aye. proceed.", "arr. granted."]
    },
    "formal": {
        "ack": ["greetings {name}.", "indeed. proceed."],
        "approval": ["welcome. access granted.", "splendid. enter."],
        "deny": ["regrettably. denied.", "alas. no access."],
        "signup": ["welcome. please register.", "indeed. join us."],
        "post": ["fine contribution.", "splendid. noted."],
        "observe": ["standing by.", "indeed. observing."],
        "load": ["system operational.", "indeed. initialized."],
        "approve": ["approval granted.", "indeed. proceed."]
    }
}

def generate_dialogues(name):
    return {
        mode: {
            intent: [l.format(name=name) for l in lines]
            for intent, lines in intents.items()
        }
        for mode, intents in TEMPLATES.items()
    }

def get_dialogue(cat, event, mode):
    intent = cat["intents"].get(event)
    if not intent:
        return None

    allowed = cat.get("allowed_modes")
    if allowed and mode not in allowed:
        mode = allowed[0]

    pool = cat["dialogues"].get(mode, {}).get(intent)
    if not pool:
        return None

    return random.choice(pool)