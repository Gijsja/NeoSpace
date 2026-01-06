
from flask import Flask, g, request, send_from_directory, session, redirect, url_for
from db import get_db, close_db, init_db
from sockets import socketio, init_sockets
from mutations.message_mutations import send_message, edit_message, delete_message
from mutations.file_mutations import upload_file
from queries.backfill import backfill_messages
from queries.unread import unread_count
import secrets
import os

def create_app(test_config=None):
    app = Flask(__name__)
    # Secure secret key (in production should be env var)
    app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key_DO_NOT_USE_IN_PROD")
    
    if test_config:
        app.config.from_mapping(test_config)

    from auth import auth_bp, login_required
    app.register_blueprint(auth_bp)

    @app.route("/")
    def index():
        if g.user is None:
             return redirect(url_for("auth.login"))
        return send_from_directory("ui/views", "app.html")

    @app.route("/ui/css/<path:filename>")
    def serve_css(filename):
        return send_from_directory("ui/css", filename)

    @app.route("/ui/js/<path:filename>")
    def serve_js(filename):
        return send_from_directory("ui/js", filename)

    @app.route("/ui/views/<path:filename>")
    def serve_views(filename):
        return send_from_directory("ui/views", filename)

    @app.route("/static/uploads/<path:filename>")
    def serve_uploads(filename):
        return send_from_directory("static/uploads", filename)

    @app.route("/static/avatars/<path:filename>")
    def serve_avatars(filename):
        return send_from_directory("static/avatars", filename)

    @app.route("/static/voice_intros/<path:filename>")
    def serve_voice_intros(filename):
        return send_from_directory("static/voice_intros", filename)

    @app.before_request
    def load_user():
        user_id = session.get('user_id')
        if user_id is None:
            g.user = None
        else:
            g.user = get_db().execute(
                'SELECT * FROM users WHERE id = ?', (user_id,)
            ).fetchone()

    # Initialize database on app creation
    with app.app_context():
        init_db()

    @app.teardown_appcontext
    def teardown(e=None):
        close_db(e)

    # =============================================
    # CHAT ENDPOINTS (Protected with login_required)
    # =============================================
    app.add_url_rule("/send", "send", login_required(send_message), methods=["POST"])
    app.add_url_rule("/edit", "edit", login_required(edit_message), methods=["POST"])
    app.add_url_rule("/delete", "delete", login_required(delete_message), methods=["POST"])
    app.add_url_rule("/upload", "upload", login_required(upload_file), methods=["POST"])
    app.add_url_rule("/backfill", "backfill", backfill_messages)  # Read-only, can remain public
    app.add_url_rule("/unread", "unread", unread_count)  # Read-only

    # =============================================
    # SPRINT 6: PROFILES
    # =============================================
    from mutations.profile import get_profile, update_profile, upload_avatar, upload_voice_intro
    app.add_url_rule("/profile", "get_profile", get_profile, methods=["GET"])
    app.add_url_rule("/profile/update", "update_profile", login_required(update_profile), methods=["POST"])
    app.add_url_rule("/profile/avatar", "upload_avatar", login_required(upload_avatar), methods=["POST"])
    app.add_url_rule("/profile/voice/upload", "upload_voice_intro", login_required(upload_voice_intro), methods=["POST"])

    # =============================================
    # SPRINT 7: PROFILE STICKERS
    # =============================================
    from mutations.profile import add_sticker, update_sticker, remove_sticker
    app.add_url_rule("/profile/sticker/add", "add_sticker", login_required(add_sticker), methods=["POST"])
    app.add_url_rule("/profile/sticker/update", "update_sticker", login_required(update_sticker), methods=["POST"])
    app.add_url_rule("/profile/sticker/remove", "remove_sticker", login_required(remove_sticker), methods=["POST"])

    # =============================================
    # SPRINT 6: DIRECT MESSAGES
    # =============================================
    from mutations.dm import send_dm, get_conversation, mark_dm_read, delete_dm, list_conversations
    app.add_url_rule("/dm/send", "send_dm", login_required(send_dm), methods=["POST"])
    app.add_url_rule("/dm/conversation", "get_conversation", login_required(get_conversation), methods=["GET"])
    app.add_url_rule("/dm/read", "mark_dm_read", login_required(mark_dm_read), methods=["POST"])
    app.add_url_rule("/dm/delete", "delete_dm", login_required(delete_dm), methods=["POST"])
    app.add_url_rule("/dm/list", "list_conversations", login_required(list_conversations), methods=["GET"])

    # =============================================
    # SPRINT 6: USER DIRECTORY
    # =============================================
    from queries.directory import list_users, get_user_by_username
    app.add_url_rule("/users", "list_users", login_required(list_users), methods=["GET"])
    app.add_url_rule("/users/lookup", "get_user_by_username", login_required(get_user_by_username), methods=["GET"])

    # =============================================
    # SPRINT 8: THE SANDBOX
    # =============================================
    from mutations.scripts import save_script, list_scripts, get_script, delete_script
    app.add_url_rule("/scripts/save", "save_script", login_required(save_script), methods=["POST"])
    app.add_url_rule("/scripts/list", "list_scripts", login_required(list_scripts), methods=["GET"])
    app.add_url_rule("/scripts/get", "get_script", get_script, methods=["GET"]) # Public read allowed
    app.add_url_rule("/scripts/delete", "delete_script", login_required(delete_script), methods=["POST"])


    init_sockets(app)
    return app

