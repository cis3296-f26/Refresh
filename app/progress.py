# Pure progress helpers (no UI); `reached` is how many cards the user has got to


def progress_label(reached, total):
    return f"{reached} of {total} cards"


def progress_fraction(reached, total):
    return reached / total if total else 0
