
from flask import Flask, g, request, send_from_directory
from db import get_db, close_db, init_db
from sockets import socketio, init_sockets
from mutations.message_mutations import send_message, edit_message, delete_message
from queries.backfill import backfill_messages
from queries.unread import unread_count

def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
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

    @app.before_request
    def load_user():
        g.user = request.headers.get("X-User", "anonymous")

    # Initialize database on app creation (replaces deprecated before_first_request)
    with app.app_context():
        init_db()

    @app.teardown_appcontext
    def teardown(e=None):
        close_db(e)

    app.add_url_rule("/send", "send", send_message, methods=["POST"])
    app.add_url_rule("/edit", "edit", edit_message, methods=["POST"])
    app.add_url_rule("/delete", "delete", delete_message, methods=["POST"])
    app.add_url_rule("/backfill", "backfill", backfill_messages)
    app.add_url_rule("/unread", "unread", unread_count)

    init_sockets(app)
    return app
