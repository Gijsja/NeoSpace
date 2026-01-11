
import sqlite3
import json

DB_PATH = "neospace.db"

FACTIONS = [
    (1, "The Concrete Sentinels", "Hypervigilant, territorial, and watchful; guardians of rigid boundaries and silent observation."),
    (2, "The Velvet Anarchs", "Mischievous, playful, and opportunistic; disrupt systems for stimulation and curiosity."),
    (3, "The Static Monks", "Zen, stoic, and relaxed; reject excess action in favor of minimal reaction."),
    (4, "The Neon Claws", "Bold, aggressive, and dominant; thrive on confrontation and visible control."),
    (5, "The Soft Collapse", "Sleepy, lazy, and satisfied; embody entropy, rest, and intentional disengagement."),
    (6, "The Peripheral Eye", "Anxious, alert, and defensive; exist on edges, scanning for threats and changes."),
    (7, "The Bonded Mass", "Affectionate, clingy, and protective; value proximity, loyalty, and collective warmth."),
    (8, "The Cold Iteration", "Aloof, confident, and proud; independent operators with strict personal sovereignty."),
    (9, "The Restless Grid", "Bored, restless, and overstimulated; constantly seeking new input to escape stagnation."),
    (10, "The Quiet Pressure", "Patient, demure, and gentle; exert influence subtly over long durations.")
]

# Tentative Mapping of Standard Cats to Factions
CAT_MAPPING = {
    "beans": 2, # Velvet Anarch (Playful/Chaotic)
    "miso": 6,  # Peripheral Eye (Anxious/Observer)
    "tofu": 7,  # Bonded Mass (Friendly)
    "ash": 5,   # Soft Collapse (Lazy)
    "delta": 9, # Restless Grid (Chaotic/Active)
    "patch": 6, # Peripheral Eye (Scared?)
    "static": 2, # Velvet Anarch (Chaotic)
    "hex": 3,   # Static Monk (Stoic/Observer?) or Neon Claw?
    "null": 3,  # Static Monk (Zen/Lazy)
    "root": 1,  # Concrete Sentinel (Control)
    "glitch": 2, # Velvet Anarch
    "neon": 4,  # Neon Claw (Dominant)
}

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Seeding Factions...")
for f in FACTIONS:
    cursor.execute("""
        INSERT OR REPLACE INTO cat_factions (id, name, description)
        VALUES (?, ?, ?)
    """, f)

print("Updating Cat Factions...")
for name, fid in CAT_MAPPING.items():
    cursor.execute("UPDATE cat_personalities SET faction_id = ? WHERE name = ?", (fid, name))

conn.commit()
conn.close()
print("Seeding Complete.")
