import structlog
import logging
import sys
import os

def configure_logging(app):
    """
    Configure structlog and standard logging.
    - Development: Pretty console output
    - Production: JSON output for observability
    """
    
    # Check environment
    env = os.environ.get("FLASK_ENV", "development")
    
    # Common processors
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]
    
    if env == "production":
        # JSON output for production
        processors.extend([
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ])
    else:
        # Pretty console for dev
        processors.extend([
            structlog.dev.ConsoleRenderer()
        ])
    
    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Attach to app for convenience (optional usage)
    app.structlog = structlog.get_logger()
    
    # Log startup
    app.structlog.info("logging_configured", env=env)
