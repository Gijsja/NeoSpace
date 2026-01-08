
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
    # BLUEPRINTS
    # =============================================
    from routes.chat import bp as chat_bp
    app.register_blueprint(chat_bp)

    from routes.views import bp as views_bp
    app.register_blueprint(views_bp)

    from routes.scripts import bp as scripts_bp
    app.register_blueprint(scripts_bp)

    from routes.messages import bp as messages_bp
    app.register_blueprint(messages_bp)

    from routes.directory import bp as directory_bp
    app.register_blueprint(directory_bp)

    from routes.wall import bp as wall_bp
    app.register_blueprint(wall_bp)

    from routes.rooms import bp as rooms_bp
    app.register_blueprint(rooms_bp)

    from routes.friends import bp as friends_bp
    app.register_blueprint(friends_bp)

    from routes.notifications import bp as notifications_bp
    app.register_blueprint(notifications_bp)


    init_sockets(app)
    return app

