from flask import request

from app.devices import bp
from app.middlewares import device_auth
from app.devices import services

@bp.route("register", methods=["POST"])
@device_auth()
def register_device():
    request_data = request.get_json()
    return services.register_device(request_data)

@bp.route("config/<device_id>", methods=["GET"])
@device_auth()
def get_config(device_id):
    return services.get_config(device_id)