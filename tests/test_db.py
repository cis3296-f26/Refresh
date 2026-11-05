from datetime import date

import pytest
from sqlalchemy import func, insert, select
from sqlalchemy.exc import IntegrityError

from app.db import cards, decks, make_engine, metadata, progress, users


def add_user(conn, username):
    return conn.execute(
        insert(users).values(username=username, password_hash="x", joined=date(2026, 11, 5))
    ).inserted_primary_key[0]


def test_duplicate_username_rejected():
    engine = make_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    row = dict(username="dagem", password_hash="x", joined=date(2026, 11, 5))
    with engine.begin() as conn:
        conn.execute(insert(users).values(**row))
    with pytest.raises(IntegrityError):
        with engine.begin() as conn:
            conn.execute(insert(users).values(**row))


def test_two_users_can_share_a_deck_name():
    engine = make_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(insert(decks).values(user_id=add_user(conn, "a"), name="Bio"))
        conn.execute(insert(decks).values(user_id=add_user(conn, "b"), name="Bio"))
        assert conn.execute(select(func.count()).select_from(decks)).scalar() == 2


def test_same_user_cannot_repeat_a_deck_name():
    engine = make_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    with engine.begin() as conn:
        user_id = add_user(conn, "a")
        conn.execute(insert(decks).values(user_id=user_id, name="Bio"))
    with pytest.raises(IntegrityError):
        with engine.begin() as conn:
            conn.execute(insert(decks).values(user_id=user_id, name="Bio"))


def test_deleting_a_deck_removes_its_cards_and_progress():
    engine = make_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    with engine.begin() as conn:
        deck_id = conn.execute(
            insert(decks).values(user_id=add_user(conn, "a"), name="Bio")
        ).inserted_primary_key[0]
        conn.execute(insert(cards).values(deck_id=deck_id, position=0, question="Q", answer="A"))
        conn.execute(insert(progress).values(deck_id=deck_id, cards_reached=1))
        conn.execute(decks.delete().where(decks.c.id == deck_id))
        assert conn.execute(select(func.count()).select_from(cards)).scalar() == 0
        assert conn.execute(select(func.count()).select_from(progress)).scalar() == 0
