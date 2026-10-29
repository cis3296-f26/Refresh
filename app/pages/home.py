import re 
from html import escape

from nicegui import ui


from app.components import nav_button
from app.colors import BLUE, BORDER, MUTED, NEGATIVE, TEXT
from app.deck_actions import add_card_dialog, create_deck_dialog, delete_deck_dialog, import_deck_dialog
from app.store import decks

#highlight matching letters in search results
def highlight_match(text, search_text):
    if not search_text:
        return escape(text)

    pattern = re.compile(re.escape(search_text), re.IGNORECASE)

    return pattern.sub(
        lambda match: (
            '<mark style="background-color: #fff2a8; font-weight: bold;">'
            + escape(match.group())
            + '</mark>'
        ),
        escape(text),
    )


# Search flashcards
def search_cards(search_text):
    matching_cards = []

    if not search_text:
        return matching_cards

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


# Display all created decks (re-rendered via display_decks.refresh)
@ui.refreshable
def display_decks(search_text=""):
    with ui.column().classes("w-full items-center p-12 gap-1"):
        if not decks:
            ui.label("No decks yet").classes("text-3xl font-extrabold")
            ui.label("Create a deck to start studying.").classes(f"text-[{MUTED}]")
        else:
            matching_decks = [
                deck_name for deck_name in decks
                if search_text.lower() in deck_name.lower()
            ]

            matching_decks.sort(
                key=lambda name: (
                    not name.lower().startswith(search_text.lower()),
                    name.lower()
                )
            )

            matching_cards = search_cards(search_text)

            if not matching_decks and not matching_cards:
                ui.label("No matching decks or cards found.")

            if matching_decks:
                for deck_name in matching_decks:
                    with ui.column().classes("w-full gap-1"):
                        ui.html(
                            highlight_match(deck_name, search_text),
                            sanitize=False,
                        ).classes("text-lg font-semibold")

                        ui.label(f"{len(decks[deck_name])} cards").classes(
                            f"text-sm text-[{MUTED}]"
                        )

            if matching_cards:
                ui.label("Matching Cards").classes(
                    "text-xl font-bold mt-6 mb-2"
                )

                for card in matching_cards:
                    with ui.column().classes(
                        "w-full border rounded-lg p-4 gap-2"
                    ):
                        ui.label(f"Deck: {card['deck']}").classes(
                            f"text-sm text-[{MUTED}]"
                        )

                        ui.html(
                            "Question: " + highlight_match(
                                card["question"], search_text
                            ),
                            sanitize=False,
                        )

                        ui.html(
                            "Answer: " + highlight_match(
                                card["answer"], search_text
                            ),
                            sanitize=False,
                        )


# Left sidebar: logo and action buttons
def sidebar():
    with ui.column().classes("w-52 sticky top-0 h-screen p-3 gap-1"):
        ui.icon("style", size="lg").classes(f"text-[{BLUE}] m-3")

        nav_button("Add card", "note_add").on(
            "click", lambda: add_card_dialog(display_decks.refresh)
        )
        nav_button("Import deck", "upload_file").on(
            "click", lambda: import_deck_dialog(display_decks.refresh)
        )
        nav_button("Delete deck", "delete").on(
            "click", lambda: delete_deck_dialog(display_decks.refresh)
        )

        ui.button(
            "Create deck",
            on_click=lambda: create_deck_dialog(display_decks.refresh),
        ).props("rounded no-caps unelevated dense").classes(
            "w-full mt-3 text-sm font-bold py-2"
        )


# Main column: page heading and deck list
def main_column():
    with ui.column().classes(
        f"w-full max-w-xl min-h-screen gap-0 border-x border-[{BORDER}]"
    ):
        ui.label("Decks").classes(
            f"w-full text-xl font-bold p-4 border-b border-[{BORDER}]"
        )

        search = ui.input (
            placeholder = "Search..."
            ).props("outlined clearable").classes("w-full px-4 py-3")

        @ui.refreshable
        def show_suggestions(search_text=""):
            if search_text:
                matching_decks = [
                    deck_name for deck_name in decks
                    if search_text.lower() in deck_name.lower()
                ]

                matching_cards = search_cards(search_text)

                matching_decks.sort(
                    key=lambda name: (
                        not name.lower().startswith(search_text.lower()),
                        name.lower()
                    )
                )

                if matching_decks or matching_cards:
                    with ui.column().classes("w-full px-4 py-2 gap-1"):
                        for deck_name in matching_decks:
                            with ui.row().classes(
                                "w-full items-center gap-2 p-2 cursor-pointer hover:bg-gray-100"
                            ).on("click", lambda e, name=deck_name: search.set_value(name)):
                                ui.icon("search", size="sm")
                                ui.html(
                                    highlight_match(deck_name, search_text),
                                    sanitize=False,
                                )

                        for card in matching_cards:
                            with ui.row().classes(
                                "w-full items-center gap-2 p-2 cursor-pointer hover:bg-gray-100"
                            ).on(
                                "click",
                                lambda e, question=card["question"]: search.set_value(question)
                            ):
                                ui.icon("description", size="sm")

                                with ui.column().classes("gap-0"):
                                    ui.html(
                                        highlight_match(card["question"], search_text),
                                        sanitize=False,
                                    )
                                    ui.label(f"Deck: {card['deck']}").classes(
                                        f"text-xs text-[{MUTED}]"
                                    )

        search.on_value_change(
            lambda e: (
                show_suggestions.refresh(e.value or ""),
                display_decks.refresh(e.value or ""),
            )
        )

        show_suggestions()
        display_decks()




# Home page: sets the theme and lays out sidebar + main column
@ui.page("/")
def home():
    ui.colors(primary=BLUE, negative=NEGATIVE)
    ui.query("body").classes(f"bg-white text-[{TEXT}]")
    ui.query(".nicegui-content").classes("p-0")

    with ui.row().classes("w-full justify-center no-wrap gap-0"):
        sidebar()
        main_column()
