from functools import wraps

from flask import abort, request, session

from config import Config


# Auth middleware
def app_auth():
    def _require_auth(f):
        @wraps(f)
        def __require_auth(*args, **kwargs):
            if request.headers.get("Authorization") != Config.APP_SECRET:
                abort(401, description="Invalid authorization header")
            if "pairingCode" not in session:
                abort(401, description="Need to be authorized for route")
            result = f(*args, **kwargs)
            return result

        return __require_auth

    return _require_auth


# Device Auth middleware
def device_auth():
    def _require_auth(f):
        @wraps(f)
        def __require_auth(*args, **kwargs):
            if request.headers.get("Authorization") != Config.DEVICE_SECRET:
                abort(401, description="Invalid authorization header")
            result = f(*args, **kwargs)
            return result

        return __require_auth

    return _require_auth
