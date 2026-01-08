"""
Security extensions configuration.
"""
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

csrf = CSRFProtect()
talisman = Talisman()
limiter = Limiter(key_func=get_remote_address)

def init_security(app):
    """Initialize security extensions."""
    
    # CSRF
    csrf.init_app(app)
    
    # CSP
    csp = {
        'default-src': ["'self'"],
        'img-src': ["'self'", "data:", "blob:"],
        'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'"], # unsafe-eval needed for some libs? check later. unsafe-inline for juiced UI.
        'style-src': ["'self'", "'unsafe-inline'"],
        'connect-src': ["'self'", "ws:", "wss:"], # WebSockets
        'worker-src': ["'self'", "blob:"],
        'media-src': ["'self'"]
    }
    
    talisman.init_app(app, 
        content_security_policy=csp,
        force_https=False # Disabled for local dev/proxy handling. Caddy handles HTTPS.
    )
    
    # Rate Limiting
    limiter.init_app(app)
