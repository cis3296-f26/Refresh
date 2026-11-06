from datetime import date,datetime,timezone
from urllib.parse import quote, unquote

from fsrs import Rating
from nicegui import ui

from app.colors import BLUE, BORDER, MUTED, NEGATIVE, TEXT
from app.components import nav_button, progress_indicator, today_indicator
from app.progress import record_viewed
from app.store import decks, progress, study_days
from app.streak import record_study_day
from app.card_schedule import due_cards, review, next_due, format_interval, preview_intervals
from app.card_storage import save_review
from app.db import engine



RATING_BUTTONS = [
    (Rating.Again, "Again"),
    (Rating.Hard, "Hard"),
    (Rating.Good, "Good"),
    (Rating.Easy, "Easy")
]

# Study page: flip through a deck one card at a time, recording how far the user got
@ui.page("/study/{deck_name}")
def study_page(deck_name: str):
    deck_name = unquote(deck_name)
    cards = decks.get(deck_name, [])

    queue = due_cards(cards)

    state = {"card": queue[0] if queue else None, "show_answer": False, "reviewed":0,}

    ui.colors(primary=BLUE, negative=NEGATIVE)
    ui.query("body").classes(f"bg-white text-[{TEXT}]")
    ui.query(".nicegui-content").classes("p-0")

    # Show the card at `index` and count it as reached
    def advance():
        queue = due_cards(cards)
        state["card"] = queue[0] if queue else None
        state["show_answer"] = False
        record_study_day(study_days, date.today())
        study_card.refresh()

    def flip():
        state["show_answer"] = not state["show_answer"]
        study_card.refresh()

    def rate(rating):
        card = state["card"]
        if card is None:
            return

        new_state, log = review(card, rating)

        try:
            with engine.begin() as conn:
                save_review(conn, card["id"], new_state, rating, log)
        except Exception as e:
            print("Database review error:", repr(e))
            ui.notify("Could not save review", color="negative")
            return

        card["fsrs"] = new_state
        state["reviewed"] += 1
        advance()

    def poll():
        if state["card"] is None and due_cards(cards):
            advance()

    def caught_up_view():
        upcoming = next_due(cards)
        with ui.column().classes("w-full items-center p-8 gap-6"):
            ui.label("All caught up!").classes("text-3xl font-extrabold")
            ui.label(f"Reviewed {state['reviewed']} cards this session.").classes(
                f"text-[{MUTED}]"
            )
            if upcoming:
                wait = format_interval(upcoming - datetime.now(timezone.utc))
                ui.label(f"Next card due in {wait}").classes(f"text-[{MUTED}]")


    @ui.refreshable
    def study_card():
        ui.label(f"Studying {deck_name}").classes(
            f"w-full text-xl font-bold p-4 border-b border-[{BORDER}]"
        )

        if not cards:
            with ui.column().classes("w-full items-center p-8 gap-6"):
                ui.label("No cards to study").classes("text-3xl font-extrabold")
                ui.label("Add some cards to this deck first.").classes(f"text-[{MUTED}]")
            return

        
        card = state["card"]

        if card is None:
            caught_up_view()
            return

        with ui.column().classes("w-full p-8 gap-6"):
            today_indicator(cards)
            ui.label(f"{len(due_cards(cards))} due").classes(f"text-sm text-[{MUTED}]")
            with ui.card().classes(f"w-full p-6 gap-3 rounded-xl border border-[{BORDER}]"):
                ui.label(card["question"]).classes("text-xl font-semibold")
                if state["show_answer"]:
                    ui.label(card["answer"]).classes(f"text-lg text-[{MUTED}]")

            if not state["show_answer"]:
                ui.button("Show answer", on_click=flip).props("rounded no-caps unelevated").classes("flex-1")
            

            else:
                intervals = preview_intervals(card)
                with ui.row().classes("w-full gap-2 no-wrap"):
                    for rating, label in RATING_BUTTONS:
                        with ui.column().classes("flex-1 items-center gap-1"):
                            ui.button(
                                label, on_click=lambda r=rating: rate(r)
                            ).props("no-caps unelevated").classes("w-full")
                            ui.label(intervals[rating]).classes(f"text-xs text-[{MUTED}]")

    with ui.row().classes("w-full justify-center no-wrap gap-0"):
        with ui.column().classes("w-52 sticky top-0 h-screen p-3 gap-1"):
            ui.icon("style", size="lg").classes(f"text-[{BLUE}] m-3")
            nav_button("Home", "home").on("click", lambda: ui.navigate.to("/"))
            nav_button("Deck details", "list").on(
                "click", lambda: ui.navigate.to(f"/deck_details/{quote(deck_name)}")
            )
        with ui.column().classes(f"w-full max-w-xl min-h-screen gap-0 border-x border-[{BORDER}]"):
            study_card()
    ui.timer(15, poll)
    


    