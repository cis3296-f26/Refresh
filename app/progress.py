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
        if not card.get("fsrs"):          # never reviewed: still to do
            left += 1
            continue

        fsrs = FsrsCard.from_dict(card["fsrs"])
        reviewed_today = fsrs.last_review is not None and fsrs.last_review >= start

        if fsrs.due <= now or (reviewed_today and fsrs.state in LEARNING):
            left += 1
        elif reviewed_today:
            done += 1

    total = left + done
    return {
        "left": left,
        "done": done,
        "total": total,
        "fraction_left": left / total if total else 0.0,
        "fraction_done": done / total if total else 1.0,
    }