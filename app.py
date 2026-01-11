
from flask import Flask, g, request, send_from_directory, session, redirect, url_for, render_template
from db import get_db, close_db, init_db
from sockets import socketio, init_sockets
from mutations.message_mutations import send_message, edit_message, delete_message
from mutations.file_mutations import upload_file
from queries.backfill import backfill_messages
from queries.unread import unread_count
import secrets
import os
from core import __version__

def create_app(test_config=None):
    app = Flask(__name__)
    
    # Inject version into all templates
    @app.context_processor
    def inject_version():
        return dict(version=__version__)
    
    # Inject version into all templates
    @app.context_processor
    def inject_version():
        return dict(version=__version__)
    
    # Load Configuration
    from config import config
    env_name = os.environ.get("FLASK_ENV", "development")
    app_config = config.get(env_name, config["default"])
    
    # Instantiate config (runs init checks like secret key validation)
    if env_name == 'production':
        conf_instance = app_config()
        app.config.from_object(conf_instance)
    else:
        app.config.from_object(app_config)

    # Manual override for property-based config keys if needed, 
    # but from_object handles properties if they are on the class/instance.
    # Check if SESSION_COOKIE_SECURE property is picked up. 
    # flask.Config.from_object scans dir(obj), so properties work if on instance or class.
    # However, property on class works better if instanced? 
    # Actually simpler: we can just set it explicitly if mapped.
    # Let's trust from_object for now, but ensure we instantiate for prod check.

    if test_config:
        app.config.from_mapping(test_config)

    # Security Hardening (Sprint 18)
    from core.security import init_security
    init_security(app)

    # Structured Logging (Sprint 27)
    from core.logs import configure_logging
    configure_logging(app)

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
                '''
                SELECT u.*, p.display_name, p.bio, p.avatar_path 
                FROM users u 
                LEFT JOIN profiles p ON u.id = p.user_id 
                WHERE u.id = ?
                ''', (user_id,)
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

    from routes.feed import bp as feed_bp
    app.register_blueprint(feed_bp)

    from routes.search import bp as search_bp
    app.register_blueprint(search_bp)

    from routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    from routes.cats import cats_bp
    app.register_blueprint(cats_bp)

    from routes.song import bp as song_bp
    app.register_blueprint(song_bp)

    from routes.files import bp as files_bp
    app.register_blueprint(files_bp)

    # =============================================
    # ERROR HANDLERS (Cat Error Pages)
    # =============================================
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.after_request
    def add_header(response):
        if request.path.startswith('/static/'):
            # Default static cache: 1 week
            response.cache_control.max_age = 604800
            
            # Avatars/Uploads with hash/UUIDs: 1 year
            if request.path.startswith('/static/avatars/') or request.path.startswith('/static/uploads/'):
                response.cache_control.max_age = 31536000
                response.cache_control.public = True
                
        return response

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')

    init_sockets(app)
    return app

# Reload trigger 2026-01-10
