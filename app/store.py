# In-memory deck storage: {deck_name: [{"question": str, "answer": str}, ...]}
decks = {}

# Furthest progress per deck: {deck_name: number of cards reached}
progress = {}

# Current user's profile: display name and the date it was created
profile = {"name": "", "joined": None}
