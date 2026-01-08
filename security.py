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
        'img-src': ["'self'", "data:", "blob:", "https://*"],
        'script-src': [
            "'self'",
            "'unsafe-inline'",  # Needed for Alpine/Tailwind config in HTML
            "'unsafe-eval'",    # Needed for standard Alpine.js
            "https://cdn.tailwindcss.com",
            "https://cdn.jsdelivr.net",
            "https://unpkg.com",
            "https://cdn.socket.io"
        ],
        'style-src': [
            "'self'",
            "'unsafe-inline'",
            "https://fonts.googleapis.com",
            "https://unpkg.com"
        ],
        'font-src': [
            "'self'",
            "https://fonts.gstatic.com",
            "https://unpkg.com"
        ],
        'connect-src': ["'self'", "https://cdn.jsdelivr.net", "https://unpkg.com"],
        'media-src': ["'self'", "https://cdn.pixabay.com"]
    }
    
    talisman.init_app(app, 
        content_security_policy=csp,
        force_https=False # Disabled for local dev/proxy handling. Caddy handles HTTPS.
    )
    
    # Rate Limiting
    limiter.init_app(app)
