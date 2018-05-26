from flask import session
from functools import wraps
from .helpers import send_error_message

def login_required(f):
    """
    Decorator to protect routes from unauthorized use,
    as described at http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    Returns: decorator function for protecting route
    """
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if session.get("user_id") is None:
            return send_error_message("401") # Exception 401 - User is unauthorized to view the resource
        return f(*args, **kwargs)
    
    return decorated_func