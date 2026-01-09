#!/usr/bin/env python3
"""Seed 10 cat companion bot users."""

import sys
sys.path.insert(0, '.')

from app import create_app

app = create_app()

with app.app_context():
    from services.cat_service import seed_cat_personalities, seed_cat_bot_users
    
    print("Seeding cat personalities...")
    seed_cat_personalities()
    
    print("Creating cat bot users...")
    seed_cat_bot_users()
    
    print("✅ 10 cats seeded successfully!")
    
    # Verify
    from db import get_db
    db = get_db()
    cats = db.execute("SELECT id, name FROM cat_personalities").fetchall()
    print(f"\nCat personalities: {[dict(c) for c in cats]}")
    
    bots = db.execute("SELECT id, username, is_bot FROM users WHERE is_bot = 1").fetchall()
    print(f"Bot users: {[dict(b) for b in bots]}")
