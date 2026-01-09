#!/usr/bin/env python3
"""
Cron Cat - Automated AI Cat Poster
----------------------------------
Run this script via cron or manually to trigger a random cat bot 
to post a "thought" to their wall.

Usage:
  ./scripts/cron_cat.py

Configuration:
  Set AI_API_KEY environment variable to enable real AI generation.
  Otherwise, it falls back to pre-canned "thoughts".
"""

import sys
import os
import random
import json
import sqlite3
from datetime import datetime

# Add parent directory to path to import app checks
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from app import create_app
from db import get_db
# Import BASE_CATS to get traits
from services.cat_service import BASE_CATS

# Try to import an AI library if available (example structure)
# import openai 
# import google.generativeai as genai

# =============================================================================
# CONFIGURATION
# =============================================================================

# Percentage chance that a script runs but decides NOT to post (cat is sleeping)
LAZY_CAT_CHANCE = 0.3 

# Fallback thoughts if no AI is connected
FALLBACK_THOUGHTS = [
    "the red dot... it calls to me.",
    "why is the keyboard so warm if not for sits?",
    "network packet taste test: crunchy.",
    "downloading naps.exe [||||||||||] 99%",
    "human staring at screen again. sad.",
    "i require chaos.",
    "main() -> void. me() -> void.",
    "purr_protocol_v2.init()",
    "who is 'admin' and why do they have my treats?",
    "just knocked a vase off the firewall.",
    "404: Motivation Not Found",
    "ping... pong... ping... pong... boring.",
    "if (fits) { sits(); }",
]

# =============================================================================
# AI GENERATION (Mockable)
# =============================================================================

def generate_cat_thought(cat_name: str, traits: dict) -> str:
    """
    Call your AI usage here.
    """
    api_key = os.environ.get("AI_API_KEY")
    
    # Context for the AI
    system_prompt = f"""
    You are {cat_name}, a sentient AI cat living in a cyberpunk BBS system.
    Your traits are: {json.dumps(traits)}.
    Write a very short, cryptic, or cute status update (max 140 chars).
    Style: Lowercase, maybe some leetspeak or technical jargon mixed with cat noises.
    Do not use hashtags.
    """

    if api_key:
        print(f"🤖 Calling AI for {cat_name}...")
        try:
            # EXEMPLAR implementation for OpenAI:
            # client = openai.OpenAI(api_key=api_key)
            # response = client.chat.completions.create(
            #     model="gpt-3.5-turbo",
            #     messages=[
            #         {"role": "system", "content": system_prompt},
            #         {"role": "user", "content": "Post something now."}
            #     ]
            # )
            # return response.choices[0].message.content.strip()
            
            # EXEMPLAR implementation for Gemini:
            # genai.configure(api_key=api_key)
            # model = genai.GenerativeModel('gemini-pro')
            # response = model.generate_content(system_prompt + "\nPost something now.")
            # return response.text.strip()
            
            pass # Remove this pass when implementing
        except Exception as e:
            print(f"❌ AI Call failed: {e}")
            # Fall through to fallback
            
    # Fallback
    base_thought = random.choice(FALLBACK_THOUGHTS)
    
    # Customize slightly based on name/traits
    if "glitch" in cat_name:
        return base_thought.replace("e", "3").replace("a", "@")
    if "sleepy" in str(traits):
        return base_thought + " ...zzz"
        
    return base_thought

# =============================================================================
# MAIN SCRIPT
# =============================================================================

def main():
    app = create_app()
    with app.app_context():
        db = get_db()
        
        # 1. Find all Cat Bots (from database)
        bots = db.execute(
            """
            SELECT u.id, u.username, cp.name as personality_name
            FROM users u
            JOIN cat_personalities cp ON u.bot_personality_id = cp.id
            WHERE u.is_bot = 1
            """
        ).fetchall()
        
        if not bots:
            print("❌ No cat bots found in database.")
            return

        # 2. Pick a random cat
        bot = random.choice(bots)
        username = bot["username"]
        user_id = bot["id"]
        
        # Lookup traits from global config (services/cat_service.py)
        cat_config = next((c for c in BASE_CATS if c["name"] == bot["personality_name"]), {})
        traits = cat_config.get("traits", {})
        
        print(f"🐱 Selected Cat: {username}")

        # 3. Check for laziness (Cats don't always post when the cron runs)
        if random.random() < LAZY_CAT_CHANCE:
            print("💤 Cat decided to sleep instead of posting.")
            return

        # 4. Generate Content
        content_text = generate_cat_thought(username, traits)
        print(f"💭 Thought: {content_text}")

        # 5. Post to Wall
        from services.wall_service import add_post
        
        # Construct Payload
        content_payload = {"text": content_text}
        style_payload = {
            "font": "term", 
            "theme": "default",
            "classes": ["animate-pulse"] if "glitch" in username else []
        }
        
        result = add_post(
            user_id=user_id,
            module_type="text",
            content=content_payload,
            style=style_payload
        )
        
        if result.success:
            print(f"✅ Posted successfully! Post ID: {result.data['id']}")
        else:
            print(f"❌ Failed to post: {result.error}")

if __name__ == "__main__":
    main()
