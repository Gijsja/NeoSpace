"""
Sentinel - Admin & Security Queries
Provides real-time metrics for the Security & Stability Dashboard.
"""

import os
from db import get_db

def get_system_metrics():
    """
    Returns high-level system metrics.
    """
    db = get_db()
    
    # Active/Total Personnel
    users_count = db.execute("SELECT COUNT(*) as c FROM users").fetchone()['c']
    banned_count = db.execute("SELECT COUNT(*) as c FROM users WHERE is_banned = 1").fetchone()['c']
    
    # Pending Reports
    pending_reports = db.execute("SELECT COUNT(*) as c FROM reports WHERE status = 'pending'").fetchone()['c']
    
    # Scripts Executed (using profile_scripts as a proxy for 'active code')
    script_count = db.execute("SELECT COUNT(*) as c FROM scripts").fetchone()['c']
    
    # Memory Usage (DB Size on disk)
    db_path = "neospace.db" # Standard path
    db_size_bytes = 0
    if os.path.exists(db_path):
        db_size_bytes = os.path.getsize(db_path)
    
    db_size_mb = round(db_size_bytes / (1024 * 1024), 2)

    return {
        "users_total": users_count,
        "users_banned": banned_count,
        "pending_reports": pending_reports,
        "scripts_total": script_count,
        "db_size_mb": db_size_mb
    }

def get_security_audit_log(limit=10):
    """
    Returns recent administrative actions from the audit log.
    """
    db = get_db()
    
    query = """
        SELECT a.*, u.username as admin_name
        FROM admin_ops a
        JOIN users u ON a.admin_id = u.id
        ORDER BY a.created_at DESC
        LIMIT ?
    """
    rows = db.execute(query, (limit,)).fetchall()
    
    logs = []
    for row in rows:
        logs.append(dict(row))
        
    return logs
