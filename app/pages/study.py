
from datetime import date
from urllib.parse import quote, unquote

from nicegui import ui

from app.colors import BLUE, BORDER, MUTED, NEGATIVE, TEXT
from app.components import nav_button, progress_indicator
from app.progress import record_viewed
from app.store import decks, progress, study_days
from app.streak import record_study_day
from app.db import engine
from app.dev_user import get_test_user_id
from app.study_storage import save_progress, save_study_day, restore_study_data


# Study page: flip through a deck one card at a time, recording how far the user got
@ui.page("/study/{deck_name}")
def study_page(deck_name: str):
    deck_name = unquote(deck_name)

    user_id = get_test_user_id()

    with engine.connect() as conn:
        restore_study_data(conn, user_id, progress, study_days)

    cards = decks.get(deck_name, [])
    state = {"index": 0, "show_answer": False}

    ui.colors(primary=BLUE, negative=NEGATIVE)
    ui.query("body").classes(f"bg-white text-[{TEXT}]")
    ui.query(".nicegui-content").classes("p-0")

    # Save study activity to SQLite
    def save_study_activity(index):
        reached = record_viewed(progress, deck_name, index, len(cards))
        today = date.today()

        with engine.begin() as conn:
            save_progress(conn, user_id, deck_name, reached)
            save_study_day(conn, user_id, today)

        record_study_day(study_days, today)

    # Show the card at `index` and count it as reached
    def go_to(index):
        state["index"] = index
        state["show_answer"] = False
        save_study_activity(index)
        study_card.refresh()

    def flip():
        state["show_answer"] = not state["show_answer"]
        study_card.refresh()

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

        index = state["index"]
        card = cards[index]

        with ui.column().classes("w-full p-8 gap-6"):
            progress_indicator(progress.get(deck_name, 0), len(cards))
            ui.label(f"Card {index + 1} of {len(cards)}").classes(f"text-sm text-[{MUTED}]")

            with ui.card().classes(f"w-full p-6 gap-3 rounded-xl border border-[{BORDER}]"):
                ui.label(card["question"]).classes("text-xl font-semibold")
                if state["show_answer"]:
                    ui.label(card["answer"]).classes(f"text-lg text-[{MUTED}]")

            with ui.row().classes("w-full gap-2 no-wrap"):
                ui.button("Previous", on_click=lambda: go_to(index - 1)).props(
                    "flat no-caps"
                ).set_enabled(index > 0)
                ui.button(
                    "Hide answer" if state["show_answer"] else "Show answer", on_click=flip
                ).props("rounded no-caps unelevated").classes("flex-1")
                ui.button("Next", on_click=lambda: go_to(index + 1)).props(
                    "flat no-caps"
                ).set_enabled(index < len(cards) - 1)

    with ui.row().classes("w-full justify-center no-wrap gap-0"):
        with ui.column().classes("w-52 sticky top-0 h-screen p-3 gap-1"):
            ui.icon("style", size="lg").classes(f"text-[{BLUE}] m-3")
            nav_button("Home", "home").on("click", lambda: ui.navigate.to("/"))
            nav_button("Deck details", "list").on(
                "click", lambda: ui.navigate.to(f"/deck_details/{quote(deck_name)}")
            )
        with ui.column().classes(f"w-full max-w-xl min-h-screen gap-0 border-x border-[{BORDER}]"):
            if cards:
                save_study_activity(0)
            study_card()
