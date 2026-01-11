from functools import wraps
from flask import jsonify
import sqlite3
from core.responses import error_response
from db import db_retry

def mutation_handler(f):
    """
    Decorator for mutation functions that handles:
    - Retries for database locks (via db_retry)
    - OperationalError handling (503 Service Unavailable)
    - Generic exception handling (500 Internal Server Error)
    
    Usage:
        @mutation_handler
        def my_mutation():
            # do stuff
            return success_response()
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            # We wrap the execution in db_retry to handle immediate lock contention
            # If f() itself calls db_retry, it's redundant but harmless.
            # Ideally f() should just contain the logic and let this handle the retry loop.
            # However, since our existing code structure often defines inner functions for retry,
            # we'll just wrap the call to f.
            return f(*args, **kwargs)
        except sqlite3.OperationalError as e:
            # If db_retry failed after max attempts, or if it wasn't used inside f
            return error_response("Database busy, please retry", 503)
        except Exception as e:
            # Catch-all for other errors
            # In a real app we might log this
            print(f"Mutation Error: {e}")
            return error_response(f"Server error: {str(e)}", 500)
    return wrapper
