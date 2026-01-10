"""
Cat Dialogue - services/cats/dialogue.py

Handles text generation for cat responses based on 'Mode' and 'Intent'.
Modes: cute, pirate, formal, chaotic (and potentially Faction-based later).
"""
import random

DIALOGUE_TEMPLATES = {
    "cute": {
        "login_success": ["yay! welcome back friend! 😺", "hi human! i missed you!", "purrrr... hello! ✨"],
        "login_failure": ["oh no! try again?", "are you sure that's you?", "scary... access denied!"],
        "friend_added": ["new frens!! amazing!", "yay! friendship is magic!", "wow so popular!"],
        "post_created": ["ooo good post!", "typing sounds! click clack!", "i leik this content."],
        "message_sent": ["zoom! message sent!", "flying words!", "hope they reply soon!"],
        "idle": ["*stares at cursor*", "meow?", "zZz...", "is it food time?"],
        "system_error": ["ouh... something broke.", "scary glitch!", "help me human!"],
        "default": ["meow!", "purrr...", "hi!"]
    },
    "pirate": {
        "login_success": ["Ahoy matey! Welcome aboard!", "Yarrr! Systems online!", "Deck verified. Enter!"],
        "login_failure": ["Walk the plank! Access denied!", "Nay! Try again ye scallywag!", "Passwords be tricky treasures."],
        "friend_added": ["Another crewmate joined!", "The crew grows larger!", "A fine addition to the roster!"],
        "post_created": ["A fine scroll ye posted!", "Marked in the captain's log!", "Words of a true sailor!"],
        "message_sent": ["Message in a bottle... away!", "Carrier parrot deployed!", "Signal sent across the seven seas!"],
        "idle": ["Polishing me hook...", "Where be the grog?", "Calm seas today...", "Yarrr..."],
        "system_error": ["Man the bilge pumps! Error!", "Kraken attack! System down!", "Abandon ship! (Just kidding)"],
        "default": ["Yarrr!", "Aye aye!", "Ahoy!"]
    },
    "formal": {
        "login_success": ["Greetings, Administrator.", "Authentication successful. Welcome.", "Systems nominal. Hello."],
        "login_failure": ["Authentication failed.", "Access denied. Please verify credentials.", "Security alert. Invalid login."],
        "friend_added": ["Social network expanded.", "Connection established.", "Associate added to registry."],
        "post_created": ["Content published successfully.", "Database entry acknowledged.", "Submission archived."],
        "message_sent": ["Transmission complete.", "Packet delivered.", "Communication initiated."],
        "idle": ["Standby mode.", "Awaiting input.", "Monitoring systems.", "Operating within normal parameters."],
        "system_error": ["Critical exception occurred.", "System anomaly detected.", "Please contact support."],
        "default": ["Acknowledged.", "Affirmative.", "Standby."]
    },
    "chaotic": {
        "login_success": ["ACCESS GRANTED // CHAOS INIT", "YOU ARE HERE. WHY.", "SYSTEM_BREACH_SUCCESSFUL"],
        "login_failure": ["NO. NO. NO.", "EJECT! EJECT!", "WRONG. TRY HARDER."],
        "friend_added": ["MORE SOULS FOR THE WEB.", "CONNECT. INTWINE. CONSUME.", "LINK ESTABLISHED."],
        "post_created": ["THE VOID HAS HEARD YOU.", "DATA_SCREAM_UPLOADED.", "MORE NOISE."],
        "message_sent": ["IT IS GONE. FOREVER?", "SENT INTO THE ABYSS.", "YELLING AT CLOUDS."],
        "idle": ["entropy_level: rising...", "do you hear the hum?", "010010110...", "glitching..."],
        "system_error": ["REALITY FAILURE.", "AAAAAAAHHHH!!!", "KERNEL PANIC!!"],
        "default": ["???", "ERROR", "VOID"]
    }
}

class CatDialogue:
    @staticmethod
    def get_line(event: str, mode: str = "cute") -> str:
        """
        Get a dialogue line for the given event and mode.
        """
        mode_templates = DIALOGUE_TEMPLATES.get(mode.lower(), DIALOGUE_TEMPLATES["cute"])
        
        # Try specific event, then default, then fallback
        options = mode_templates.get(event, mode_templates.get("default", ["..."]))
        
        return random.choice(options)
