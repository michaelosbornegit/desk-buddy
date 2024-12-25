from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_apscheduler import APScheduler
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_session import Session
from flask_socketio import SocketIO

from app import bcrypt as global_bcrypt
from app import socketio_instance
from app.db import db
from app.jobs.background_jobs import update_firmware
from config import Config


def create_app(testing=False):
    app = Flask(__name__)

    # Flask app config
    if testing:
        app.config["TESTING"] = True
    else:
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
        app.config["SESSION_COOKIE_SECURE"] = Config.API_HOST.split("://")[0] == "https"
        app.config["SESSION_COOKIE_DOMAIN"] = Config.API_HOST.split("://")[1]
        app.config["SESSION_TYPE"] = "mongodb"
        app.config["SESSION_PERMANENT"] = True
        app.config["SESSION_MONGODB"] = db.mongo_client
        app.config["SESSION_MONGODB_DB"] = Config.MONGO_DATABASE
    app.secret_key = Config.SESSION_KEY

    # Initialize Flask extensions
    Session(app)

    bcrypt = Bcrypt(app)
    global_bcrypt.instance.init(bcrypt)

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    scheduler.add_job(
        id="update_firmware",
        func=update_firmware,
        trigger="interval",
        seconds=120,
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

    from app.messages import bp as messages_bp

    app.register_blueprint(messages_bp, url_prefix="/messages")

    @app.route("/", methods=["GET"])
    def status():
        return "Go away!"

    return app
