import sqlite3

DB_PATH = "app.db"

# Faction IDs (from manual migration):
# 1: Concrete Sentinels
# 2: Velvet Anarchs
# 3: Static Monks
# 4: Neon Claws
# 5: Soft Collapse
# 6: Peripheral Eye
# 7: Bonded Mass
# 8: Cold Iteration
# 9: Restless Grid
# 10: Quiet Pressure

MAPPING = {
    "beans": 1,   # Sentinel
    "ash": 1,     # Sentinel
    "root": 2,    # Anarch (likes chaos)
    "glitch": 2,  # Anarch
    "miso": 3,    # Monk
    "tofu": 3,    # Monk
    "neon": 4,    # Claws (Aggro)
    "delta": 4,   # Claws
    "null": 5,    # Soft Collapse (Lazy)
    "patch": 6,   # Peripheral Eye (Anxious)
    "static": 8,  # Cold Iteration (Aloof)
    "hex": 9,     # Restless Grid (Bored)
}

def assign_factions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    count = 0
    for name, fid in MAPPING.items():
        cursor.execute("UPDATE cat_personalities SET faction_id = ? WHERE name = ?", (fid, name))
        if cursor.rowcount > 0:
            count += 1
            print(f"Assigned {name} -> Faction {fid}")
            
    conn.commit()
    conn.close()
    print(f"Done. Assigned {count} cats.")

if __name__ == "__main__":
    assign_factions()
