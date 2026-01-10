"""
Cat Store - services/cats/store.py

Persistence layer.
Handles DB interactions for Cat Personalities, States, and Relationships.
"""
from typing import List, Dict, Optional, Any
import json
import time
from db import get_db, execute_with_retry

class CatStore:
    @staticmethod
    def get_all_cats() -> List[Dict]:
        """Fetch all cat personalities with their current global state."""
        query = """
        SELECT 
            p.*, 
            s.pleasure, s.arousal, s.dominance, s.last_deed_id,
            f.name as faction_name
        FROM cat_personalities p
        LEFT JOIN cat_states s ON p.id = s.cat_id
        LEFT JOIN cat_factions f ON p.faction_id = f.id
        ORDER BY p.priority DESC
        """
        rows = execute_with_retry(query, fetchall=True)
        return [dict(row) for row in rows] if rows else []

    @staticmethod
    def get_cat_by_name(name: str) -> Optional[Dict]:
        query = """
        SELECT 
            p.*, 
            s.pleasure, s.arousal, s.dominance, s.last_deed_id,
            f.name as faction_name
        FROM cat_personalities p
        LEFT JOIN cat_states s ON p.id = s.cat_id
        LEFT JOIN cat_factions f ON p.faction_id = f.id
        WHERE p.name = ?
        """
        row = execute_with_retry(query, (name,), fetchone=True)
        return dict(row) if row else None

    @staticmethod
    def seed_personalities(base_cats: List[Dict]):
        """Insert default cat personalities."""
        db = get_db()
        for cat in base_cats:
            db.execute('''
                INSERT OR IGNORE INTO cat_personalities 
                (name, priority, triggers, mode, silence_bias, global_observer, 
                 pleasure_weight, arousal_weight, dominance_weight, avatar_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cat["name"],
                cat["priority"],
                json.dumps(cat["triggers"]),
                "cute",
                cat["silence_bias"],
                1 if cat.get("global_observer") else 0,
                1.0, 0.5, 1.0, 
                f"/static/images/cats/{cat['name']}.png"
            ))
        db.commit()

    @staticmethod
    def seed_bot_users(base_cats: List[Dict]):
        """Create actual user accounts for each cat."""
        from werkzeug.security import generate_password_hash
        import secrets
        
        db = get_db()
        
        for cat in base_cats:
            # Check if user exists
            existing = db.execute(
                "SELECT id FROM users WHERE username = ?",
                (cat["name"],)
            ).fetchone()
            
            if existing:
                db.execute("UPDATE users SET is_bot = 1 WHERE username = ?", (cat["name"],))
                continue
            
            # Create new bot user
            password_hash = generate_password_hash(secrets.token_hex(32))
            cursor = db.execute('''
                INSERT INTO users (username, password_hash, is_bot, avatar_color, created_at)
                VALUES (?, ?, 1, ?, CURRENT_TIMESTAMP)
            ''', (cat["name"], password_hash, "#" + secrets.token_hex(3)[:6]))
            
            user_id = cursor.lastrowid
            
            # Link Personality
            personality = db.execute(
                "SELECT id FROM cat_personalities WHERE name = ?",
                (cat["name"],)
            ).fetchone()
            
            if personality:
                db.execute(
                    "UPDATE users SET bot_personality_id = ? WHERE id = ?",
                    (personality["id"], user_id)
                )
            
            # Create profile
            db.execute('''
                INSERT OR IGNORE INTO profiles (user_id, display_name, bio, theme_preset)
                VALUES (?, ?, ?, ?)
            ''', (
                user_id,
                cat["name"].upper(),
                f"🐱 SYSTEM BIT: {cat['name'].upper()}",
                "term"
            ))
        
        db.commit()

    @staticmethod
    def update_cat_state(cat_id: int, pad: tuple, last_deed_id: str = None):
        """Update or Insert Global State"""
        p, a, d = pad
        query = """
        INSERT INTO cat_states (cat_id, pleasure, arousal, dominance, last_updated)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(cat_id) DO UPDATE SET
            pleasure = excluded.pleasure,
            arousal = excluded.arousal,
            dominance = excluded.dominance,
            last_updated = CURRENT_TIMESTAMP
        """
        execute_with_retry(query, (cat_id, p, a, d))

    @staticmethod
    def ensure_db_tables():
        pass 

    @staticmethod
    def add_memory(cat_id: int, user_id: int, memory_type: str, impact: float, duration_hours: int = 24):
        """
        Log a memory.
        """
        query = """
        INSERT INTO cat_memories (source_cat_id, target_user_id, memory_type, opinion_modifier, expires_at)
        VALUES (?, ?, ?, ?, datetime('now', ?))
        """
        execute_with_retry(query, (cat_id, user_id, memory_type, impact, f'+{duration_hours} hours'))
        
        # Trigger recalculation of relationship
        CatStore.recalculate_relationship(cat_id, user_id)

    @staticmethod
    def recalculate_relationship(cat_id: int, user_id: int):
        """
        Sum up active memories to determine affinity.
        Also calculates Faction Compatibility if target is a Cat Bot.
        """
        db = get_db()
        
        # 1. Sum Memories
        query_sum = """
        SELECT SUM(opinion_modifier) 
        FROM cat_memories 
        WHERE source_cat_id = ? AND target_user_id = ? AND expires_at > datetime('now')
        """
        row = execute_with_retry(query_sum, (cat_id, user_id), fetchone=True)
        affinity_memories = row[0] if row and row[0] else 0.0

        # 2. Get Compatibility (Faction Based)
        compatibility = 0.0
        
        try:
            # Check source faction
            src_row = db.execute("SELECT faction_id FROM cat_personalities WHERE id = ?", (cat_id,)).fetchone()
            
            # Check target faction (is it a bot with a personality?)
            tgt_row = db.execute("""
                SELECT cp.faction_id 
                FROM users u 
                JOIN cat_personalities cp ON u.bot_personality_id = cp.id 
                WHERE u.id = ?
            """, (user_id,)).fetchone()
            
            if src_row and tgt_row and src_row[0] and tgt_row[0]:
                if src_row[0] == tgt_row[0]:
                    compatibility = 30.0 # Same Faction Bonus
                else:
                    compatibility = -10.0 # Rival Faction (Generic)
        except Exception:
            pass
        
        # 3. Update Table
        total_affinity = max(-100, min(100, affinity_memories + compatibility))
        
        update_query = """
        INSERT INTO cat_relationships (source_cat_id, target_user_id, affinity, compatibility, last_updated)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(source_cat_id, target_user_id) DO UPDATE SET
            affinity = excluded.affinity,
            compatibility = excluded.compatibility,
            last_updated = CURRENT_TIMESTAMP
        """
        execute_with_retry(update_query, (cat_id, user_id, total_affinity, compatibility))

    @staticmethod
    def get_relationship(cat_id: int, user_id: int) -> float:
        """
        Get current affinity (-100 to 100). Returns 0.0 if None.
        """
        query = "SELECT affinity FROM cat_relationships WHERE source_cat_id = ? AND target_user_id = ?"
        row = execute_with_retry(query, (cat_id, user_id), fetchone=True)
        return row[0] if row else 0.0 
