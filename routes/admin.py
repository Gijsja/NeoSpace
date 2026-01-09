import functools
from flask import Blueprint, g, render_template, abort
from db import get_db
from mutations.moderation import resolve_report, submit_report as submit_report_mutation

bp = Blueprint('admin', __name__, url_prefix='/admin')

# Public-ish route (Authenticated Users)
@bp.route('/report', methods=['POST'])
def submit_report():
    return submit_report_mutation()

# Staff-Only Middleware
def staff_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.user:
            return "Unauthorized", 401
        if not g.user['is_staff']:
            return "Forbidden", 403
        return view(**kwargs)
    return wrapped_view

@bp.route('/')
@staff_required
def dashboard():
    db = get_db()
    pending_count = db.execute("SELECT COUNT(*) as c FROM reports WHERE status = 'pending'").fetchone()['c']
    users_count = db.execute("SELECT COUNT(*) as c FROM users").fetchone()['c']
    reports = db.execute("SELECT r.*, u.username as reporter_name FROM reports r JOIN users u ON r.reporter_id = u.id ORDER BY r.created_at DESC LIMIT 50").fetchall()
    
    return render_template('admin/dashboard.html', 
        pending_count=pending_count, 
        users_count=users_count, 
        reports=reports
    )

@bp.route('/resolve', methods=['POST'])
@staff_required
def resolve():
    return resolve_report()
