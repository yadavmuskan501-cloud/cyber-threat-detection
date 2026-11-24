import os

from pathlib import Path
from urllib.parse import quote_plus
from dotenv import dotenv_values
from pymongo import MongoClient, ReturnDocument

BASE_DIR = Path(__file__).resolve().parent

APP_ENV = os.getenv("SENTINEL_ENV", "development")

if APP_ENV not in {"development", "test"}:
    raise RuntimeError("Invalid SENTINEL_ENV value.")

ENV_FILE = ".env.test" if APP_ENV == "test" else ".env"

jenkins_env_file = os.getenv("MONGODB_TEST_ENV_FILE")

if jenkins_env_file:
    if APP_ENV != "test":
        raise RuntimeError(
            "Jenkins test credentials require test mode."
        )

    env_path = Path(jenkins_env_file)
else:
    env_path = BASE_DIR / ENV_FILE

if not env_path.is_file():
    raise RuntimeError("MongoDB configuration file not found.")

config = dotenv_values(env_path)

required_keys = [
    "MONGODB_USERNAME",
    "MONGODB_PASSWORD",
    "MONGODB_HOST",
    "MONGODB_DB_NAME"
]

for key in required_keys:
    if not config.get(key):
        raise RuntimeError(f"Missing configuration: {key}")

db_name = config["MONGODB_DB_NAME"]

# Prevent accidental access to application data during testing.
if APP_ENV == "test":
    if db_name != "sentinelai_test":
        raise RuntimeError("Unsafe test database configuration.")

    if config["MONGODB_USERNAME"] != "sentinelai_test_user":
        raise RuntimeError("Invalid testing database user.")

username = quote_plus(config["MONGODB_USERNAME"])
password = quote_plus(config["MONGODB_PASSWORD"])
host = config["MONGODB_HOST"]

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