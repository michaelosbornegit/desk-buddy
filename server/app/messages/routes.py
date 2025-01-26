from flask import abort, request, session

from app.messages import bp, services
from app.middlewares import app_auth, device_auth
from app.utils import get_property_if_exists


@bp.route("send", methods=["POST"])
@app_auth()
def send_message():
    request_data = request.get_json()
    message_from = session.get("displayName")
    message_to = get_property_if_exists(request_data, "to")
    message = get_property_if_exists(request_data, "message")
    centerLines = get_property_if_exists(request_data, "centerLines")
    return services.send_message(message_from, message_to, message, centerLines)


@bp.route("get-for-user", methods=["GET"])
@app_auth()
def get_messages_for_user():
    display_name = session.get("displayName")
    # pagination is not implemented
    limit = int(request.args.get("limit", 5))
    offset = int(request.args.get("offset", 0))
    return services.get_messages(display_name, limit, offset)


@bp.route("get-recipients", methods=["GET"])
@app_auth()
def get_recipients():
    return services.get_recipients()


@bp.route("read-message", methods=["POST"])
@device_auth()
def read_message():
    request_data = request.get_json()
    message_id = get_property_if_exists(request_data, "messageId")
    device_id = get_property_if_exists(request_data, "deviceId")
    return services.read_message(message_id, device_id)
