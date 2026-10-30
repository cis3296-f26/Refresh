
import re
from datetime import date
from html import escape
from urllib.parse import quote

from nicegui import ui

from app.components import nav_button, progress_indicator
from app.colors import BLUE, BORDER, MUTED, NEGATIVE, TEXT
from app.deck_actions import (
    add_card_dialog,
    create_deck_dialog,
    delete_deck_dialog,
    import_deck_dialog,
)
from app.store import decks, progress, study_days
from app.streak import current_streak


# Highlight matching letters in search results
def highlight_match(text, search_text):
    if not search_text:
        return escape(text)

    pattern = re.compile(re.escape(search_text), re.IGNORECASE)

    return pattern.sub(
        lambda match: (
            '<mark style="background-color: #fff2a8; font-weight: bold;">'
            + match.group()
            + '</mark>'
        ),
        escape(text),
    )


# Search flashcards
def search_cards(search_text):
    matching_cards = []

    if not search_text:
        return decks

    for deck_name, cards in decks.items():
        for card in cards:
            question = card["question"]
            answer = card["answer"]

            if (
                search_text.lower() in question.lower()
                or search_text.lower() in answer.lower()
            ):
                matching_cards.append({
                    "deck": deck_name,
                    "question": question,
                    "answer": answer,
                })

    return matching_cards


# Refresh dashboard and deck list together
def refresh_dashboard():
    study_dashboard.refresh()
    display_decks.refresh()


# Study Dashboard
@ui.refreshable
def study_dashboard():
    total_decks = len(decks)

    total_cards = sum(
        len(cards) for cards in decks.values()
    )

    studied_cards = sum(
        min(max(progress.get(name, 0), 0), len(cards))
        for name, cards in decks.items()
    )

    streak = current_streak(study_days, date.today())

    with ui.column().classes("w-full p-5 gap-4"):

        ui.label("Study Dashboard").classes(
            "text-2xl font-bold"
        )

        ui.label(
            "Keep track of your decks and study progress."
        ).classes(f"text-sm text-[{MUTED}]")

        with ui.grid(columns=2).classes("w-full gap-3"):

            # Total decks
            with ui.card().classes("w-full p-4 gap-2"):
                ui.icon("folder", size="md").classes(
                    f"text-[{BLUE}]"
                )
                ui.label("Total Decks").classes(
                    f"text-sm text-[{MUTED}]"
                )
                ui.label(str(total_decks)).classes(
                    "text-2xl font-bold"
                )

            # Total flashcards
            with ui.card().classes("w-full p-4 gap-2"):
                ui.icon("style", size="md").classes(
                    f"text-[{BLUE}]"
                )
                ui.label("Total Flashcards").classes(
                    f"text-sm text-[{MUTED}]"
                )
                ui.label(str(total_cards)).classes(
                    "text-2xl font-bold"
                )

            # Cards studied
            with ui.card().classes("w-full p-4 gap-2"):
                ui.icon("check_circle", size="md").classes(
                    f"text-[{BLUE}]"
                )
                ui.label("Cards Studied").classes(
                    f"text-sm text-[{MUTED}]"
                )
                ui.label(str(studied_cards)).classes(
                    "text-2xl font-bold"
                )

            # Daily study streak
            with ui.card().classes("w-full p-4 gap-2"):
                ui.icon(
                    "local_fire_department", size="md"
                ).classes(f"text-[{BLUE}]")
                ui.label("Current Streak").classes(
                    f"text-sm text-[{MUTED}]"
                )
                ui.label(f"{streak} days").classes(
                    "text-2xl font-bold"
                )

        # Overall study progress
        ui.label("Overall Progress").classes(
            "text-lg font-semibold mt-2"
        )

        percentage = (
            round((studied_cards / total_cards) * 100)
            if total_cards > 0 else 0
        )

        ui.linear_progress(
            value=percentage / 100,
            show_value=False,
        ).props("rounded").classes("w-full")

        ui.label(
            f"{studied_cards} of {total_cards} cards studied ({percentage}%)"
        ).classes(f"text-sm text-[{MUTED}]")


# Display all created decks
@ui.refreshable
def display_decks(search_text=""):
    with ui.column().classes(
        "w-full items-center p-8 gap-6"
    ):
        if not decks:
            ui.label("No decks yet").classes(
                "text-3xl font-extrabold"
            )
            ui.label(
                "Create a deck to start studying."
            ).classes(f"text-[{MUTED}]")

        else:
            query = (search_text or "").strip().lower()

            matching_card_decks = (
                {
                    card["deck"]
                    for card in search_cards(query)
                }
                if query else set()
            )

            filtered_decks = [
                name for name in decks
                if not query
                or query in name.lower()
                or name in matching_card_decks
            ]

            if not filtered_decks:
                ui.label(
                    "No matching decks or cards found"
                ).classes("text-3xl font-extrabold")
                ui.label(
                    "Try a different search term."
                ).classes(f"text-[{MUTED}]")

            for deck_name in filtered_decks:
                with ui.column().classes(
                    f"w-full p-4 gap-3 rounded-xl "
                    f"border border-[{BORDER}]"
                ):
                    ui.label(deck_name).classes(
                        "text-lg font-semibold gap-1"
                    )

                    ui.label(
                        f"{len(decks[deck_name])} flashcards"
                    ).classes(f"text-sm text-[{MUTED}]")

                    progress_indicator(
                        progress.get(deck_name, 0),
                        len(decks[deck_name]),
                    )

                    with ui.row().classes(
                        "w-full gap-2 no-wrap"
                    ):
                        ui.button(
                            "Study",
                            on_click=lambda name=deck_name:
                                ui.navigate.to(
                                    f"/study/{quote(name)}"
                                ),
                        ).props(
                            "rounded no-caps unelevated dense"
                        ).classes(
                            "flex-1 text-sm font-bold py-2 mt-1"
                        )

                        ui.button(
                            "View Details",
                            on_click=lambda name=deck_name:
                                ui.navigate.to(
                                    f"/deck_details/{quote(name)}"
                                ),
                        ).props(
                            "rounded no-caps unelevated dense"
                        ).classes(
                            "flex-1 text-sm font-bold py-2 mt-1"
                        )


# Left sidebar
def sidebar():
    with ui.column().classes(
        "w-52 sticky top-0 h-screen p-3 gap-1"
    ):
        ui.icon("style", size="lg").classes(
            f"text-[{BLUE}] m-3"
        )

        streak = current_streak(
            study_days, date.today()
        )

        if streak:
            ui.label(
                f"🔥 {streak} day streak"
            ).classes(
                f"text-sm font-semibold px-3 text-[{MUTED}]"
            )

        search = ui.input(
            placeholder="Search..."
        ).props(
            "outlined clearable"
        ).classes("w-full px-4 py-3")

        nav_button("Create deck", "create").on(
            "click",
            lambda: create_deck_dialog(refresh_dashboard),
        )

        nav_button("Import deck", "upload_file").on(
            "click",
            lambda: import_deck_dialog(refresh_dashboard),
        )

        nav_button("Delete deck", "delete").on(
            "click",
            lambda: delete_deck_dialog(refresh_dashboard),
        )

        nav_button("Profile", "person").on(
            "click",
            lambda: ui.navigate.to("/profile"),
        )

        @ui.refreshable
        def show_suggestions(search_text=""):
            if search_text:
                matching_decks = [
                    deck_name for deck_name in decks
                    if search_text.lower()
                    in deck_name.lower()
                ]

                matching_cards = search_cards(search_text)

                matching_decks.sort(
                    key=lambda name: (
                        not name.lower().startswith(
                            search_text.lower()
                        ),
                        name.lower(),
                    )
                )

                if matching_decks or matching_cards:
                    with ui.column().classes(
                        "w-full px-4 py-2 gap-1"
                    ):
                        for deck_name in matching_decks:
                            with ui.row().classes(
                                "w-full items-center gap-2 p-2 "
                                "cursor-pointer hover:bg-gray-100"
                            ).on(
                                "click",
                                lambda e, name=deck_name:
                                    search.set_value(name),
                            ):
                                ui.icon("search", size="sm")
                                ui.html(
                                    highlight_match(
                                        deck_name, search_text
                                    ),
                                    sanitize=False,
                                )

                        for card in matching_cards:
                            with ui.row().classes(
                                "w-full items-center gap-2 p-2 "
                                "cursor-pointer hover:bg-gray-100"
                            ).on(
                                "click",
                                lambda e, question=card["question"]:
                                    search.set_value(question),
                            ):
                                ui.icon(
                                    "description", size="sm"
                                )

                                with ui.column().classes("gap-0"):
                                    ui.html(
                                        highlight_match(
                                            card["question"],
                                            search_text,
                                        ),
                                        sanitize=False,
                                    )
                                    ui.label(
                                        f"Deck: {card['deck']}"
                                    ).classes(
                                        f"text-xs text-[{MUTED}]"
                                    )

        search.on_value_change(
            lambda e: (
                show_suggestions.refresh(e.value or ""),
                display_decks.refresh(e.value or ""),
            )
        )

        show_suggestions()


# Main column
def main_column():
    with ui.column().classes(
        f"w-full max-w-xl min-h-screen gap-0 "
        f"border-x border-[{BORDER}]"
    ):
        study_dashboard()

        ui.separator()

        ui.label("My Decks").classes(
            f"w-full text-xl font-bold p-4 "
            f"border-b border-[{BORDER}]"
        )

        display_decks()


# Home page
@ui.page("/")
def home():
    ui.colors(primary=BLUE, negative=NEGATIVE)

    ui.query("body").classes(
        f"bg-white text-[{TEXT}]"
    )

    ui.query(".nicegui-content").classes("p-0")

    with ui.row().classes(
        "w-full justify-center no-wrap gap-0"
    ):
        sidebar()
        main_column()
