# Pure progress helpers (no UI); `reached` is how many cards the user has got to


def progress_label(reached, total):
    return f"{reached} of {total} cards"


def progress_fraction(reached, total):
    return reached / total if total else 0


# Record that the card at `index` (0-based) was just shown; progress only moves forward
def record_viewed(progress, deck_name, index, total):
    progress[deck_name] = min(max(progress.get(deck_name, 0), index + 1), total)
    return progress[deck_name]
