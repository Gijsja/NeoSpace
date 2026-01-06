
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
    
    from routes.profiles import bp as profiles_bp
    app.register_blueprint(profiles_bp)

    @app.route("/")
    def index():
        if g.user is None:
             return redirect(url_for("auth.login"))
        return send_from_directory("ui/views", "app.html")

    @app.route("/desktop")
    def desktop():
        if g.user is None:
             return redirect(url_for("auth.login"))
        return send_from_directory("ui/views", "desktop.html")

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

    @app.route("/ui/prototypes/<path:filename>")
    def serve_prototypes(filename):
        return send_from_directory("ui/prototypes", filename)

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
    # SPRINT 6: DIRECT MESSAGES
    # =============================================
    from mutations.dm import send_dm, get_conversation, mark_dm_read, delete_dm, list_conversations
    from routes.scripts import bp as scripts_bp
    app.register_blueprint(scripts_bp)

    from routes.messages import bp as messages_bp
    app.register_blueprint(messages_bp)

    from routes.directory import bp as directory_bp
    app.register_blueprint(directory_bp)





    init_sockets(app)
    return app

