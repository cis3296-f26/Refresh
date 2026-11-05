from sqlalchemy import insert, delete, select
from app.db import decks as db_decks, cards as db_cards

#get deck and return name and cards
def get_deck_data(deck_name, decks):
    if deck_name not in decks:
        return None

    return {
        "name": deck_name,
        "cards": decks[deck_name].copy()
    }

#get all decks and their cards
def get_all_decks(decks):
    all_decks = []

    for deck_name in decks:
        deck_data = get_deck_data(deck_name, decks)
        all_decks.append(deck_data)

    return all_decks

#Load saved decks and cards back into the app
def load_decks(saved_decks, decks):
    decks.clear()

    for deck in saved_decks:
        decks[deck["name"]] = deck["cards"].copy()

# Save a deck and its cards to the database
def save_deck(conn, user_id, deck_name, cards):
    result = conn.execute(
        insert(db_decks).values(user_id=user_id, name=deck_name)
    )

    deck_id = result.inserted_primary_key[0]

    for position, card in enumerate(cards):
        conn.execute(
            insert(db_cards).values(
                deck_id=deck_id,
                question=card["question"],
                answer=card["answer"],
                position=position
            )
        )

# Delete a deck and all its cards from the db
def delete_saved_deck(conn, user_id, deck_name):
    conn.execute(
        delete(db_decks).where(
            db_decks.c.user_id == user_id,
            db_decks.c.name == deck_name
        )
    )


# Update the cards in an existing deck
def update_saved_deck(conn, user_id, deck_name, cards):
    result = conn.execute(
        select(db_decks.c.id).where(
            db_decks.c.user_id == user_id,
            db_decks.c.name == deck_name
        )
    )

    deck_id = result.scalar_one_or_none()

    if deck_id is None:
        return

    #eemove old cards
    conn.execute(
        delete(db_cards).where(db_cards.c.deck_id == deck_id)
    )

    #save updated cards
    for position, card in enumerate(cards):
        conn.execute(
            insert(db_cards).values(
                deck_id=deck_id,
                question=card["question"],
                answer=card["answer"],
                position=position
            )
        )
