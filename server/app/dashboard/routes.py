from flask import request

from app.dashboard import bp
from app.middlewares import device_auth
from app.dashboard import services


@bp.route("raw/<device_id>", methods=["GET"])
@device_auth()
def get_dashboard(device_id):
    return services.get_dashboard(device_id)
