import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    MONGO_ENDPOINT = os.getenv("MONGODB_ENDPOINT")
    MONGO_DATABASE = os.getenv("MONGODB_DATABASE")
    DEVICE_SECRET = os.getenv("DEVICE_SECRET")
    APP_SECRET = os.getenv("APP_SECRET")
    SESSION_KEY = os.getenv("SESSION_KEY")
    API_HOST = os.getenv("API_HOST")
    APP_HOST = os.getenv("APP_HOST")
    PORT = os.getenv("PORT")
    VERSION_UPDATE_CHECK_INTERVAL = os.getenv("VERSION_UPDATE_CHECK_INTERVAL")
