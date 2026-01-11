import os
from datetime import timedelta

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret_key_DO_NOT_USE_IN_PROD")
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")
    DATABASE = os.environ.get("DATABASE", "app.db")
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_REFRESH_EACH_REQUEST = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Security -- Restrict CORS to configured origins
    ALLOWED_ORIGINS = os.environ.get(
        "ALLOWED_ORIGINS", 
        "http://localhost:5000,http://127.0.0.1:5000"
    ).split(",")
    
    # SocketIO
    SOCKETIO_ASYNC_MODE = os.environ.get("SOCKETIO_ASYNC_MODE", None)

    @property
    def SESSION_COOKIE_SECURE(self):
        """Secure cookies only in production (HTTPS)."""
        return self.FLASK_ENV == 'production'

class DevelopmentConfig(Config):
    """Development specifics."""
    DEBUG = True

class ProductionConfig(Config):
    """Production specifics."""
    DEBUG = False
    
    def __init__(self):
        # Enforce production requirements
        if not self.SECRET_KEY or self.SECRET_KEY.startswith('dev_'):
            raise ValueError("CRITICAL SECURITY ERROR: SECRET_KEY must be set to a secure value in production!")

# Config selector
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
