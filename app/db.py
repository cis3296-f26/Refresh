import os

from sqlalchemy import create_engine

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
