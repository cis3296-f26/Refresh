import os
import tempfile

# Runs before any test imports app.db, so tests get a throwaway database and
# never touch the real local file (data/refresh.db) or the Neon database.
os.environ.pop("DATABASE_URL", None)
_test_db = os.path.join(tempfile.mkdtemp(), "test.db").replace("\\", "/")
os.environ["REFRESH_LOCAL_DB_URL"] = f"sqlite:///{_test_db}"
os.environ["REFRESH_SKIP_LOGIN"] = "1"

import pytest  # noqa: E402

from app.db import engine, metadata  # noqa: E402


# Start every test with empty tables so one test's decks can't affect the next
@pytest.fixture(autouse=True)
def empty_tables():
    with engine.begin() as conn:
        for table in reversed(metadata.sorted_tables):
            conn.execute(table.delete())
    yield
