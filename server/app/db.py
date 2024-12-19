from pymongo.mongo_client import MongoClient

from config import Config

class db:
    __mongo_client = MongoClient(Config.MONGO_ENDPOINT)
    __database = __mongo_client[Config.MONGO_DATABASE]
    devices = __database["devices"]
    users = __database["users"]
    software_versions = __database["software_versions"]