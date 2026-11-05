import os
from datetime import date

from sqlalchemy import insert, select

from app.db import engine, users


def get_test_user_id():
    # Temporary account for local development only.
    # Replace with the real logged-in user when authentication is ready.
    if os.environ.get("DATABASE_URL"):
        raise RuntimeError(
            "Temporary test user is disabled when DATABASE_URL is configured. "
            "Connect persistence to the real authenticated user."
        )

    with engine.begin() as conn:
        user_id = conn.execute(
            select(users.c.id).where(
                users.c.username == "local_persistence_test"
            )
        ).scalar_one_or_none()

        if user_id is not None:
            return user_id

        result = conn.execute(
            insert(users).values(
                username="local_persistence_test",
                password_hash="testing_only_no_login",
                display_name="Test User",
                joined=date.today()
            )
        )

        return result.inserted_primary_key[0]