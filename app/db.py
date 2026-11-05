import os

from sqlalchemy import (
    Column, Date, ForeignKey, Integer, MetaData, String, Table, Text, UniqueConstraint, create_engine, event,
)

# Used when DATABASE_URL is not set (local development and tests)
LOCAL_URL = os.environ.get("REFRESH_LOCAL_DB_URL", "sqlite:///data/refresh.db")


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
    engine = create_engine(url, pool_pre_ping=True)

    # SQLite ignores foreign keys (and so ON DELETE CASCADE) unless asked to enforce them
    if engine.dialect.name == "sqlite":
        @event.listens_for(engine, "connect")
        def enable_foreign_keys(dbapi_connection, _):
            dbapi_connection.execute("PRAGMA foreign_keys = ON")

    return engine


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

# `position` keeps the card order the user chose when dragging cards around
cards = Table(
    "cards", metadata,
    Column("id", Integer, primary_key=True),
    Column("deck_id", ForeignKey("decks.id", ondelete="CASCADE"), nullable=False),
    Column("position", Integer, nullable=False),
    Column("question", Text, nullable=False),
    Column("answer", Text, nullable=False),
)

# How many cards of a deck the user has reached
progress = Table(
    "progress", metadata,
    Column("deck_id", ForeignKey("decks.id", ondelete="CASCADE"), primary_key=True),
    Column("cards_reached", Integer, nullable=False, default=0),
)

# One row per day the user studied at least one card
study_days = Table(
    "study_days", metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("day", Date, primary_key=True),
)

metadata.create_all(engine)
