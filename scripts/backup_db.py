#!/usr/bin/env python3
"""
Hot Backup Script for NeoSpace (SQLite)
Uses `VACUUM INTO` to create a safe, consistent backup while the app is running.
"""
import sqlite3
import os
import sys
import glob
import datetime
from pathlib import Path

# Config
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "neospace.db")
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backups")
KEEP_BACKUPS = 5

def create_backup():
    """Create a hot backup of the database."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"neospace_backup_{timestamp}.db")
    
    print(f"[{datetime.datetime.now()}] Starting backup of {DB_PATH}...")
    
    try:
        # Connect to the live database
        conn = sqlite3.connect(DB_PATH)
        # Use VACUUM INTO to create a consistent backup copy
        conn.execute(f"VACUUM INTO '{backup_file}'")
        conn.close()
        print(f"✅ Backup created: {backup_file}")
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        sys.exit(1)
        
    return backup_file

def rotate_backups():
    """Keep only the N most recent backups."""
    backups = sorted(glob.glob(os.path.join(BACKUP_DIR, "neospace_backup_*.db")))
    
    if len(backups) > KEEP_BACKUPS:
        to_delete = backups[:-KEEP_BACKUPS]
        for f in to_delete:
            try:
                os.remove(f)
                print(f"🗑️ Rotated (deleted): {f}")
            except OSError as e:
                print(f"⚠️ Failed to delete {f}: {e}")

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        sys.exit(1)
        
    create_backup()
    rotate_backups()
