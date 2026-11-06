import json
from datetime import datetime
from app.db import cards as db_cards, review_logs
from app.deck_storage import get_deck_id
from sqlalchemy import insert, delete, select, update, func

def add_card(conn, user_id, deck_name, question, answer):
    deck_id = get_deck_id(conn, user_id, deck_name)

    position = conn.execute(
        select(func.coalesce(func.max(db_cards.c.position), -1) + 1)
        .where(db_cards.c.deck_id == deck_id)
    ).scalar_one()

    result = conn.execute(
        insert(db_cards).values(
            deck_id=deck_id,
            position=position,
            question=question,
            answer=answer,
        )
    )

    return {
        "id": result.inserted_primary_key[0],
        "question" : question,
        "answer" : answer,
        "fsrs" : None,
    }


def update_card_text(conn, card_id, question, answer):
    conn.execute(
        update(db_cards)
        .where(db_cards.c.id == card_id)
        .values(question=question, answer=answer)
    )
    

def delete_card(conn, card_id):
    conn.execute(
        delete(db_cards)
        .where(db_cards.c.id == card_id)
    )
    

def save_order(conn, cards):
    for position, card in enumerate(cards):
        conn.execute(
            update(db_cards)
            .where(db_cards.c.id == card["id"])
            .values(position=position)
        )


def save_review(conn, card_id, fsrs_state, rating, log):
    conn.execute(
        update(db_cards)
        .where(db_cards.c.id == card_id)
        .values(fsrs=json.dumps(fsrs_state))
    )

    conn.execute(
        insert(review_logs).values(
            card_id=card_id,
            rating=int(rating),
            reviewed_at=datetime.fromisoformat(log["review_datetime"]),
            log=json.dumps(log)
        )
    )
 