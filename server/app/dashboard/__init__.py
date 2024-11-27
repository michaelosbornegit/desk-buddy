from flask import Blueprint

bp = Blueprint("dashboards", __name__)

from app.dashboard import routes
from app.dashboard import services
