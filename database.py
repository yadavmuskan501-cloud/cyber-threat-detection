import os

from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv
from pymongo import MongoClient

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


def init_database():
    users_collection.create_index(
        "username", unique=True
    )

    users_collection.create_index(
        "email", unique=True
    )