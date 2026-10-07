from functools import lru_cache

from django.conf import settings
from pymongo import MongoClient
from pymongo.database import Database


@lru_cache(maxsize=None)
def get_database() -> Database:
    client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=3000, tz_aware=True)
    return client[settings.MONGO_DB_NAME]
