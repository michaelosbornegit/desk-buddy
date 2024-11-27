from flask import abort, request, session, redirect
from app.errors import bad_request
import subprocess
import json
import requests

from app.dashboard import bp
from config import Config
from app.middlewares import require_auth
from app.dashboard import services

@bp.route("dog/<platform>", methods=["GET"])
@require_auth()
def dog_dashboard(platform):
    if platform == "two-screens-four-buttons":
        return services.get_dog_dashboard_two_screens_four_buttons()
    elif platform == "two-screens-readonly":
        return services.get_dog_dashboard_two_screens_readonly()
    return "Platform not supported"

@bp.route("dog/<platform>", methods=["POST"])
@require_auth()
def dog_dashboard_post(platform):
    if platform == "two-screens-four-buttons":
        button = request.json.get('button')
        return services.post_dog_dashboard_two_screens_four_buttons(button)
    return "Platform not supported"