from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt
from apscheduler.schedulers.background import BackgroundScheduler
from flask_apscheduler import APScheduler

from config import Config
from app import socketio_instance
from app import bcrypt as global_bcrypt
from app.jobs.background_jobs import update_firmware


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
    bcrypt = Bcrypt(app)
    global_bcrypt.instance.init(bcrypt)

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    scheduler.add_job(
        id="update_firmware",
        func=update_firmware,
        trigger="interval",
        seconds=2,
    )

    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")
    socketio_instance.instance.init(socketio)

    CORS(
        app,
        supports_credentials=True,
    )

    # Register blueprints
    from app.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix="/dashboards")
    from app.devices import bp as devices_bp
    app.register_blueprint(devices_bp, url_prefix="/devices")

    @app.route("/", methods=["GET"])
    def status():
        return "Go away!"

    return app
