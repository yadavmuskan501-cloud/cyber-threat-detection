import sqlite3
from pathlib import Path
from database import users_collection, init_database

SQLITE_DB = Path(__file__).resolve().parent / "sentinel.db"


def migrate_users():

    if not SQLITE_DB.exists():
        raise FileNotFoundError("SQLite database not found.")

    init_database()

    conn = sqlite3.connect(
        SQLITE_DB.as_uri() + "?mode=ro",
        uri=True
    )

    conn.row_factory = sqlite3.Row

    try:
        rows = conn.execute("""
            SELECT id, username, email,
                   hashed_password, role, created_at
            FROM users
            ORDER BY id
        """).fetchall()
    finally:
        conn.close()

    print(f"SQLite users found: {len(rows)}")

    users_collection.create_index("id", unique=True)

    migrated = 0
    skipped = 0
    conflicts = 0

    for row in rows:

        user = dict(row)

        existing = list(users_collection.find({
            "$or": [
                {"id": user["id"]},
                {"username": user["username"]},
                {"email": user["email"]}
            ]
        }, {"_id": 0}))

        if existing:
            if len(existing) == 1 and all(
                existing[0].get(key) == value
                for key, value in user.items()
            ):
                skipped += 1
            else:
                conflicts += 1
                print(f"Conflict found for user ID: {user['id']}")
            continue

        users_collection.insert_one(user.copy())
        migrated += 1

    verified = 0

    for row in rows:
        expected = dict(row)

        actual = users_collection.find_one(
            {"id": expected["id"]},
            {"_id": 0}
        )

        if actual and all(
            actual.get(key) == value
            for key, value in expected.items()
        ):
            verified += 1

    print("\n===== MIGRATION REPORT =====")
    print("SQLite users:", len(rows))
    print("Newly migrated:", migrated)
    print("Already migrated:", skipped)
    print("Conflicts:", conflicts)
    print("Verified users:", verified)
    print("Total MongoDB users:",
          users_collection.count_documents({}))

    if verified == len(rows) and conflicts == 0:
        print("Migration completed successfully!")
    else:
        raise RuntimeError("Migration verification failed.")


if __name__ == "__main__":
    migrate_users()