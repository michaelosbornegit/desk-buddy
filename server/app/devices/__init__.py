from flask import Blueprint

bp = Blueprint("devices", __name__)

from app.devices import routes as routes
from app.devices import services as services
