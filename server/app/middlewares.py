from functools import wraps
from flask import abort, request

from config import Config


# Auth middleware
def require_auth():
    def _require_auth(f):
        @wraps(f)
        def __require_auth(*args, **kwargs):
            if request.headers.get("Authorization") != Config.SECRET:
                abort(401, description="Invalid authorization header")
            result = f(*args, **kwargs)
            return result

        return __require_auth

    return _require_auth
