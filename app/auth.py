import os
from datetime import datetime

import bcrypt
from nicegui import app, ui
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from app.db import engine, users

MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 30
MIN_PASSWORD_LENGTH = 6


# Clean up
def clean_username(username):
    username = (username or "").strip().lower()
    if not MIN_USERNAME_LENGTH <= len(username) <= MAX_USERNAME_LENGTH:
        return None
    if not all(c.isalnum() or c in "_." for c in username):
        return None
    return username


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password, password_hash):
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError:
        return False


# Make new account
def create_user(username, password):
    cleaned = clean_username(username)
    if cleaned is None:
        return None, (
            f"Username must be {MIN_USERNAME_LENGTH} to {MAX_USERNAME_LENGTH} characters "
            "(letters, numbers, _ or .)"
        )
    if len(password or "") < MIN_PASSWORD_LENGTH:
        return None, f"Password must be at least {MIN_PASSWORD_LENGTH} characters"

    try:
        with engine.begin() as conn:
            result = conn.execute(
                insert(users).values(
                    username=cleaned,
                    password_hash=hash_password(password),
                    display_name=cleaned,
                    joined=datetime.now(),
                )
            )
            return result.inserted_primary_key[0], None
    except IntegrityError:
        return None, "That username is taken"


# Check a login
def verify_user(username, password):
    cleaned = clean_username(username)
    if cleaned is None or not password:
        return None

    with engine.connect() as conn:
        row = conn.execute(
            select(users.c.id, users.c.password_hash).where(users.c.username == cleaned)
        ).one_or_none()

    if row is None or not check_password(password, row.password_hash):
        return None
    return row.id


# browser's session(app.storage.user is saved per browser by NiceGUI)
def session():
    try:
        return app.storage.user
    except Exception:
        return None


def log_in(user_id):
    app.storage.user["user_id"] = user_id


def log_out():
    app.storage.user.pop("user_id", None)
    ui.navigate.to("/login")


def current_user_id():
    storage = session()
    if storage is not None and storage.get("user_id") is not None:
        return storage["user_id"]

    if os.environ.get("REFRESH_SKIP_LOGIN") == "1":
        from app.dev_user import get_test_user_id
        return get_test_user_id()

    return None


# logged out visitors --> login
def require_login():
    user_id = current_user_id()

    if user_id is not None:
        with engine.connect() as conn:
            exists = conn.execute(select(users.c.id).where(users.c.id == user_id)).first()
        if exists is None:
            storage = session()
            if storage is not None:
                storage.pop("user_id", None)
            user_id = None

    if user_id is None:
        ui.navigate.to("/login")
    return user_id
