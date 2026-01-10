"""
The Song Studio Routes
"""

from flask import Blueprint, jsonify, request, g, render_template, abort
from auth import login_required
from db import get_db
from mutations.song import save_song, delete_song
import msgspec

bp = Blueprint('song', __name__, url_prefix='/song')

@bp.route("/", strict_slashes=False)
@login_required
def studio():
    """Render the Song Studio interface."""
    return render_template("song.html")

@bp.route("/list")
@login_required
def list_songs():
    """List current user's songs."""
    db = get_db()
    user_id = g.user['id']
    
    rows = db.execute(
        "SELECT id, title, updated_at, created_at, is_public FROM songs WHERE user_id=? ORDER BY updated_at DESC",
        (user_id,)
    ).fetchall()
    
    songs = [dict(row) for row in rows]
    return jsonify(ok=True, songs=songs)

@bp.route("/get/<int:song_id>")
def get_song(song_id):
    """Get a song by ID (Public or Owned)."""
    db = get_db()
    row = db.execute("SELECT * FROM songs WHERE id=?", (song_id,)).fetchone()
    
    if not row:
        return jsonify(ok=False, error="Not found"), 404
        
    is_owner = g.user and row['user_id'] == g.user['id']
    if not row['is_public'] and not is_owner:
         return jsonify(ok=False, error="Private song"), 403

    # Decode JSON data
    song_data = dict(row)
    try:
        song_data['data'] = msgspec.json.decode(row['data_json'].encode('utf-8'))
    except:
        song_data['data'] = {}
    del song_data['data_json']
    
    return jsonify(ok=True, song=song_data)

@bp.route("/save", methods=["POST"])
@login_required
def save():
    return save_song()

@bp.route("/delete", methods=["POST"])
@login_required
def delete():
    return delete_song()
