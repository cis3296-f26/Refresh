from datetime import datetime, timezone
from fsrs import Card as FsrsCard, Rating, Scheduler

scheduler = Scheduler()
RATINGS = (Rating.Again, Rating.Hard, Rating.Good, Rating.Easy)

def load(card: dict) -> FsrsCard:
    return FsrsCard.from_dict(card["fsrs"]) if card.get("fsrs") else FsrsCard()

def due_cards(cards: list[dict]) -> list[dict]:
    now = datetime.now(timezone.utc)
    reviews, new = [], []
    for card in cards:
        if not card.get("fsrs"):
            new.append(card)
            continue
        due = FsrsCard.from_dict(card["fsrs"]).due
        if due <= now:
            reviews.append((due, card))
    reviews.sort(key=lambda pair: pair[0])
    return [card for _, card in reviews] + new

def next_due(cards: list[dict]):
    dues = [FsrsCard.from_dict(c["fsrs"]).due for c in cards if c.get("fsrs")]
    return min(dues, default=None)

def review(card: dict, rating: Rating):
    fsrs_card, log = scheduler.review_card(load(card), rating)
    return fsrs_card.to_dict(), log.to_dict()

def format_interval(delta) -> str:
    seconds = max(0, int(delta.total_seconds()))
    if seconds < 3600:
        return f"{max(1, round(seconds / 60))}m"
    if seconds < 86400:
        return f"{round(seconds / 3600)}h"
    days = round(seconds / 86400)
    if days < 30:
        return f"{days}d"
    if days < 365:
        return f"{round(days / 30)}mo"
    return f"{round(days / 365, 1)}y"

def preview_intervals(card: dict) -> dict:
    now = datetime.now(timezone.utc)
    current = load(card)
    return {
        rating: format_interval(scheduler.review_card(current, rating, now)[0].due-now)for rating in RATINGS
    }