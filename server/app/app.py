from flask import Flask
from flask_cors import CORS
from flask_apscheduler import APScheduler
from flask_socketio import SocketIO

from config import Config
from app import socketio_instance


def create_app(testing=False):
    app = Flask(__name__)

    # Flask app config
    if testing:
        app.config["TESTING"] = True
    else:
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
        app.config["SESSION_COOKIE_SECURE"] = Config.API_HOST.split("://")[0] == "https"
        app.config["SESSION_COOKIE_DOMAIN"] = Config.API_HOST.split("://")[1]
    app.secret_key = Config.SESSION_KEY

    # Initialize Flask extensions
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")
    socketio_instance.instance.init(socketio)

    CORS(
        app,
        supports_credentials=True,
    )

    # Register blueprints
    from app.dashboard import bp as dashboard_bp

    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

    @app.route("/", methods=["GET"])
    def status():
        return "Go away!"

    return app
