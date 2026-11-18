# Pure progress helpers (no UI); `reached` is how many cards the user has got to

from datetime import date, datetime, time, timezone

from fsrs import Card as FsrsCard, State

LEARNING = (State.Learning, State.Relearning)

def progress_label(reached, total):
    return f"{reached} of {total} cards studied"


def progress_fraction(reached, total):
    return reached / total if total else 0


# Record that the card at `index` (0-based) was just shown; progress only moves forward
def record_viewed(progress, deck_name, index, total):
    progress[deck_name] = min(max(progress.get(deck_name, 0), index + 1), total)
    return progress[deck_name]

def today_progress(cards, now=None, start=None):
    now = now or datetime.now(timezone.utc)
    start = start or datetime.combine(date.today(), time.min).astimezone().astimezone(timezone.utc)
    left = done = 0
    for card in cards:
        fsrs = FsrsCard.from_dict(card["fsrs"]) if card.get("fsrs") else None
        if fsrs and fsrs.last_review and fsrs.last_review >= start:
            done += 1   #rated today
        elif fsrs is None or fsrs.due <= now:
            left +=1 #new or due
    total = left + done
    return {
        "left": left,
        "done": done,
        "total": total,
        "fraction_done": done / total if total else 1.0,
    }