from nicegui import ui

from urllib.parse import quote

from app.components import nav_button, progress_indicator
from app.colors import BLUE, BORDER, MUTED, NEGATIVE, TEXT
from app.deck_actions import add_card_dialog, create_deck_dialog, delete_deck_dialog, import_deck_dialog
from app.store import decks, progress


# Display all created decks (re-rendered via display_decks.refresh)
@ui.refreshable
def display_decks():
    with ui.column().classes("w-full items-center p-8 gap-6"):
        if not decks:
            ui.label("No decks yet").classes("text-3xl font-extrabold")
            ui.label("Create a deck to start studying.").classes(f"text-[{MUTED}]")
        else:
            for deck_name in decks:
                with ui.column().classes("w-full p-4 gap-3 rounded-xl border border-[{BORDER}]"):
                    ui.label(deck_name).classes("text-lg font-semibold gap-1")
                    progress_indicator(progress.get(deck_name, 0), len(decks[deck_name]))
                    ui.button("View Details", on_click=lambda name = deck_name: ui.navigate.to(f"/deck_details/{quote(name)}")).props("rounded no-caps unelevated dense").classes(
                        "w-full text-sm font-bold py-2 mt-1"
                    )

# Left sidebar: logo and action buttons
def sidebar():
    with ui.column().classes("w-52 sticky top-0 h-screen p-3 gap-1"):
        ui.icon("style", size="lg").classes(f"text-[{BLUE}] m-3")

        nav_button("Create deck", "create").on(
            "click", lambda: create_deck_dialog(display_decks.refresh)
        )
        nav_button("Import deck", "upload_file").on(
            "click", lambda: import_deck_dialog(display_decks.refresh)
        )
        nav_button("Delete deck", "delete").on(
            "click", lambda: delete_deck_dialog(display_decks.refresh)
        )



# Main column: page heading and deck list
def main_column():
    with ui.column().classes(
        f"w-full max-w-xl min-h-screen gap-0 border-x border-[{BORDER}]"
    ):
        ui.label("Decks").classes(
            f"w-full text-xl font-bold p-4 border-b border-[{BORDER}]"
        )
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
