MAX_NAME_LENGTH = 30

# Trim name and reject if it's empty or too long
def clean_display_name(name):
    cleaned = (name or "").strip()
    if not cleaned or len(cleaned) > MAX_NAME_LENGTH:
        return None
    return cleaned

# First letter for the avatar circle
def initials(name):
    return name[0].upper() if name else "?"
  
# Totals shown on the profile page(takes from deck and progress stores)
def profile_stats(decks, progress):
    total_cards = sum(len(cards) for cards in decks.values())
   
    # progress can't count past the end of a deck
    cards_reached = sum(min(progress.get(name, 0), len(cards)) for name, cards in decks.items())
    finished = sum(1 for name, cards in decks.items() if cards and progress.get(name, 0) >= len(cards))

    return {
        "decks": len(decks),
        "cards": total_cards,
        "cards_reached": cards_reached,
        "decks_finished": finished,
    }
