from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from app.db import user_settings
from app.fsrs_settings import DEFAULTS

def restore_user_settings(conn, user_id, settings):
    row = conn.execute(
        select(user_settings).where(user_settings.c.user_id == user_id)
    ).mappings().one_or_none()
    settings.clear()
    settings.update(DEFAULTS)
    if row:
        settings.update({k: row[k] for k in DEFAULTS})

def save_user_settings(conn, user_id, cleaned):
    make_insert = pg_insert if conn.dialect.name == "postgresql" else sqlite_insert
    stmt = make_insert(user_settings).values(user_id=user_id, **cleaned)
    conn.execute(stmt.on_conflict_do_update(
        index_elements=["user_id"], set_=cleaned))