
from sqlalchemy import select, insert, update

from app.db import decks as db_decks
from app.db import progress as db_progress
from app.db import study_days as db_study_days


# Save the furthest card reached in a deck
def save_progress(conn, user_id, deck_name, cards_reached):
    deck_id = conn.execute(
        select(db_decks.c.id).where(
            db_decks.c.user_id == user_id,
            db_decks.c.name == deck_name,
        )
    ).scalar_one_or_none()

    if deck_id is None:
        raise ValueError(f"Deck not found: {deck_name}")

    existing = conn.execute(
        select(db_progress.c.cards_reached).where(
            db_progress.c.deck_id == deck_id
        )
    ).scalar_one_or_none()

    if existing is None:
        conn.execute(
            insert(db_progress).values(
                deck_id=deck_id,
                cards_reached=cards_reached,
            )
        )
    elif cards_reached > existing:
        conn.execute(
            update(db_progress)
            .where(db_progress.c.deck_id == deck_id)
            .values(cards_reached=cards_reached)
        )


# Save the date a user studied, without duplicates
def save_study_day(conn, user_id, today):
    conn.execute(
        insert(db_study_days)
        .prefix_with("OR IGNORE")
        .values(
            user_id=user_id,
            day=today,
        )
    )


# Restore saved progress and study days
def restore_study_data(conn, user_id, progress, study_days):
    saved_progress = conn.execute(
        select(db_decks.c.name, db_progress.c.cards_reached)
        .join(db_progress, db_decks.c.id == db_progress.c.deck_id)
        .where(db_decks.c.user_id == user_id)
    )

    progress.clear()
    progress.update({
        name: reached for name, reached in saved_progress
    })

    saved_days = conn.execute(
        select(db_study_days.c.day).where(
            db_study_days.c.user_id == user_id
        )
    )

    study_days.clear()
    study_days.update(row.day for row in saved_days)
