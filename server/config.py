import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SESSION_KEY = os.getenv("SESSION_KEY")
    API_HOST = os.getenv("API_HOST")
    APP_HOST = os.getenv("APP_HOST")
    PORT = os.getenv("PORT")
    SECRET = os.getenv("SECRET")
    HA_HOST = os.getenv("HA_HOST")
    HA_TOKEN = os.getenv("HA_TOKEN")
