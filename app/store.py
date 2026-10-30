# In-memory deck storage: {deck_name: [{"question": str, "answer": str}, ...]}
decks = {}

# Furthest progress per deck: {deck_name: number of cards reached}
progress = {}

# Dates the user studied at least one card: {datetime.date, ...}
study_days = set()

# Current user's profile: display name and the date it was created
profile = {"name": "", "joined": None}
