"""
Security extensions configuration.
"""
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

csrf = CSRFProtect()
talisman = Talisman()
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://"
)

def init_security(app):
    """Initialize security extensions."""
    
    # CSRF
    csrf.init_app(app)
    
    # CSP - Tightened since assets are now vendored locally
    csp = {
        'default-src': ["'self'"],
        'img-src': ["'self'", "data:", "blob:", "https://http.cat", "https://i.pravatar.cc"],
        'script-src': [
            "'self'",
            "'unsafe-inline'",  # Needed for Alpine/Tailwind config in HTML
            "'unsafe-eval'",    # Needed for standard Alpine.js
            "blob:",            # Needed for Tone.js workers
            "https://cdn.jsdelivr.net",  # Fallback for emoji-picker only
            "https://cdnjs.cloudflare.com",
            "https://cdn.tailwindcss.com"
        ],
        'style-src': [
            "'self'",
            "'unsafe-inline'",
            "https://fonts.googleapis.com",
            "https://cdnjs.cloudflare.com",
            "https://cdn.tailwindcss.com"
        ],
        'font-src': [
            "'self'",
            "https://fonts.gstatic.com",
            "https://cdnjs.cloudflare.com"
        ],
        'connect-src': ["'self'", "blob:", "wss:", "ws:", "https://*"],  # Allow outgoing API/Websocket and blob: for Tone.js
        'media-src': ["'self'", "blob:", "data:", "https://*", "http://*"],  # Allow external audio streams
        'frame-src': ["'self'", "blob:"],  # For script sandboxes
        'worker-src': ["'self'", "blob:"]   # For Tone.js audio worklets
    }
    
    talisman.init_app(app, 
        content_security_policy=csp,
        force_https=False # Disabled for local dev/proxy handling. Caddy handles HTTPS.
    )
    
    # Rate Limiting
    limiter.init_app(app)
