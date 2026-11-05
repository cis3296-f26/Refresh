import os

from sqlalchemy import (
    Column, Date, ForeignKey, Integer, MetaData, String, Table, UniqueConstraint, create_engine,
)

# Used when DATABASE_URL is not set (local development and tests)
LOCAL_URL = "sqlite:///data/refresh.db"


# Hosts hand out postgres:// or postgresql:// URLs; SQLAlchemy needs to be told to use psycopg
def database_url():
    url = os.environ.get("DATABASE_URL") or LOCAL_URL
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


def make_engine(url=None):
    url = url or database_url()
    if url.startswith("sqlite:///") and ":memory:" not in url:
        os.makedirs(os.path.dirname(url[len("sqlite:///"):]) or ".", exist_ok=True)
    return create_engine(url, pool_pre_ping=True)


engine = make_engine()

metadata = MetaData()

users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(50), nullable=False, unique=True),
    Column("password_hash", String(255), nullable=False),
    Column("display_name", String(30), nullable=False, default=""),
    Column("joined", Date, nullable=False),
)

# A user's deck names are unique, but two users can each have a deck called "Bio"
decks = Table(
    "decks", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("name", String(100), nullable=False),
    UniqueConstraint("user_id", "name"),
)
