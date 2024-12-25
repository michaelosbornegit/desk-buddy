from flask import Blueprint

bp = Blueprint("dashboards", __name__)

from app.dashboard import routes as routes
from app.dashboard import services as services
