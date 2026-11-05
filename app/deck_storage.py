
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
    cursor = conn.execute(
        "INSERT INTO decks (user_id, name) VALUES (?, ?)",
        (user_id, deck_name)
    )

    deck_id = cursor.lastrowid

    for position, card in enumerate(cards):
        conn.execute(
            """INSERT INTO cards (deck_id, question, answer, position)
               VALUES (?, ?, ?, ?)""",
            (deck_id, card["question"], card["answer"], position)
        )

    conn.commit()

# Delete a deck and all its cards from the db
def delete_saved_deck(conn, user_id, deck_name):
    conn.execute("""
        DELETE FROM decks
        WHERE user_id = ? AND name = ?
    """, (user_id, deck_name))

    conn.commit()

# Update the cards in an existing deck
def update_saved_deck(conn, user_id, deck_name, cards):
    cursor = conn.execute(
        "SELECT id FROM decks WHERE user_id = ? AND name = ?",
        (user_id, deck_name)
    )

    deck = cursor.fetchone()

    if deck is None:
        return

    deck_id = deck[0]

    conn.execute("DELETE FROM cards WHERE deck_id = ?", (deck_id,))

    for position, card in enumerate(cards):
        conn.execute(
            """INSERT INTO cards (deck_id, question, answer, position)
               VALUES (?, ?, ?, ?)""",
            (deck_id, card["question"], card["answer"], position)
        )

    conn.commit()