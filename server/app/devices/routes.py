from urllib.parse import unquote

from flask import abort, request, session

from app.devices import bp, services
from app.middlewares import device_auth
from app.utils import get_property_if_exists


@bp.route("login", methods=["GET", "POST"])
def login():
    if session.get("pairingCode"):
        return services.login(session.get("pairingCode"))
    if request.method == "POST":
        request_data = request.get_json()
        pairing_code = get_property_if_exists(request_data, "pairingCode")
        display_name = get_property_if_exists(request_data, "displayName")
        force_associate = get_property_if_exists(request_data, "forceAssociate")
        return services.register(pairing_code, display_name, force_associate)
    return abort(401, "Failed to authenticate")


@bp.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return "logged out"


@bp.route("register", methods=["POST"])
@device_auth()
def device_register():
    request_data = request.get_json()
    device_config = services.get_config(request_data["deviceId"])
    print(device_config)
    if device_config["displayName"] is None:
        return abort(400, "Device not registered")
    return device_config


@bp.route("config/<device_id>", methods=["GET"])
@device_auth()
def get_config(device_id):
    return services.get_config(device_id)


@bp.route("firmware/<relative_path>", methods=["GET"])
@device_auth()
def get_firmware_contents(relative_path):
    unencoded_relative_path = unquote(relative_path)
    # Do our custom unencoding for slashes
    unencoded_relative_path = unencoded_relative_path.replace("^$#", "/")
    print(unencoded_relative_path)
    file = services.get_firmware_contents(unencoded_relative_path)
    return file["contents"]
