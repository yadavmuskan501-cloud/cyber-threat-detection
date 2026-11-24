import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(override=True)

username = quote_plus(os.environ["MONGODB_USERNAME"])
password = quote_plus(os.environ["MONGODB_PASSWORD"])
host = os.environ["MONGODB_HOST"]
db_name = os.environ["MONGODB_DB_NAME"]

uri = (
    f"mongodb+srv://{username}:{password}@{host}/"
    "?retryWrites=true&w=majority&authSource=admin"
)

client = None

try:
    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=30000,
        connectTimeoutMS=20000
    )

    client.admin.command("ping")

    print("MongoDB connected successfully!")
    print("Database:", client[db_name].name)

except Exception as e:
    print("MongoDB connection failed!")
    print("Error type:", type(e).__name__)
    print("Error:", str(e))

finally:
    if client is not None:
        client.close()