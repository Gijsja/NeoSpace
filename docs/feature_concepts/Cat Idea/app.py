from flask import Flask, request
from flask_socketio import SocketIO, emit
import time, random

from cats import CATS
from dialogue_factory import get_dialogue
from state import state, update_emotion

DEFAULT_MODE = "cute"

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on("event")
def handle_event(data):
    event = data.get("event")
    if not event:
        return

    mode = data.get("mode", DEFAULT_MODE)

    eligible = [c for c in CATS if event in c["triggers"] or c.get("global_observer")]
    weighted = []

    for cat in eligible:
        fam = min(state["familiarity"][cat["name"]], 10) * 0.5
        emo = state["emotions"][cat["name"]]
        emotion_mod = (
            emo["pleasure"] * cat.get("pleasure_weight", 1.0)
            + emo["arousal"] * cat.get("arousal_weight", 0.5)
            + emo["dominance"] * cat.get("dominance_weight", 1.0)
        )
        silence = cat["silence_bias"] * (2 if cat.get("global_observer") else 5)
        weight = cat["priority"] + fam + emotion_mod - silence

        if state["last_speaker"] != cat["name"]:
            weighted.append((weight, cat))

    if not weighted:
        emit("cat_response", {"cat": None, "avatar": None, "line": None})
        return

    weighted.sort(key=lambda x: x[0], reverse=True)
    cat = weighted[0][1]

    line = get_dialogue(cat, event, mode)
    if not line:
        emit("cat_response", {"cat": None, "avatar": None, "line": None})
        return

    state["last_speaker"] = cat["name"]
    state["familiarity"][cat["name"]] += 1
    update_emotion(cat["name"], event)

    emit("cat_response", {
        "cat": cat["name"],
        "avatar": cat["avatars"].get(mode),
        "line": line
    })

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)