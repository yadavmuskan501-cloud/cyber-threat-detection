import os

from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv
from pymongo import MongoClient, ReturnDocument

load_dotenv(Path(__file__).resolve().parent / ".env")

username = quote_plus(os.environ["MONGODB_USERNAME"])
password = quote_plus(os.environ["MONGODB_PASSWORD"])
host = os.environ["MONGODB_HOST"]
db_name = os.environ["MONGODB_DB_NAME"]

uri = (
    f"mongodb+srv://{username}:{password}@{host}/"
    "?retryWrites=true&w=majority&authSource=admin"
)

client = MongoClient(
    uri,
    serverSelectionTimeoutMS=30000,
    connectTimeoutMS=20000
)

db = client[db_name]

users_collection = db["users"]
counters_collection = db["counters"]


def init_database():

    users_collection.create_index(
        "username", unique=True
    )

    users_collection.create_index(
        "email", unique=True
    )

    users_collection.create_index(
        "id", unique=True
    )

    latest_user = users_collection.find_one(
        {},
        {"id": 1},
        sort=[("id", -1)]
    )

    max_id = latest_user["id"] if latest_user else 0

    counters_collection.update_one(
        {"_id": "users"},
        {"$max": {"sequence": max_id}},
        upsert=True
    )


def get_next_user_id():

    counter = counters_collection.find_one_and_update(
        {"_id": "users"},
        {"$inc": {"sequence": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )

    return counter["sequence"]