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
    return services.send_message(message_from, message_to, message)


@bp.route("get-read", methods=["GET"])
@app_auth()
def get_read_messages():
    display_name = session.get("displayName")
    limit = int(request.args.get("limit", 5))
    offset = int(request.args.get("offset", 0))
    return services.get_read_messages(display_name, limit, offset)
