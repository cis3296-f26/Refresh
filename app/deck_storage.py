
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