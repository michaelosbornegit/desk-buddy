from flask import Blueprint

bp = Blueprint("users", __name__)

from app.users import routes as routes
from app.users import services as services
