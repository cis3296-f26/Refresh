from pathlib import Path
import random

from nicegui import ui,events
from app.store import decks, progress
from app.parsing import parse_deck

# Each dialog takes an on_change callback that refreshes the deck list after a change

# Create a new deck
def create_deck_dialog(on_change):
    with ui.dialog() as dialog, ui.card():
        ui.label("Create a New Deck").classes("text-lg font-bold")

        name = ui.input("Deck Name").classes("w-full")

        # Validate the name, then save the new deck
        def save_deck():
            deck_name = (name.value or "").strip()

            if not deck_name:
                ui.notify("Please enter a deck name", color="negative")
                return

            if deck_name in decks:
                ui.notify("Deck already exists", color="negative")
                return

            decks[deck_name] = []
            ui.notify("Deck created successfully!", color="positive")
            dialog.close()
            on_change()

        ui.button("Create", on_click=save_deck)

    dialog.open()


# Delete an existing deck
def delete_deck_dialog(on_change):
    if not decks:
        ui.notify("No decks to delete", color="negative")
        return

    with ui.dialog() as dialog, ui.card():
        ui.label("Delete Deck").classes("text-lg font-bold")

        deck_select = ui.select(
            list(decks.keys()),
            label="Select Deck"
        ).classes("w-full")

        # Remove the selected deck
        def confirm_delete():
            if not deck_select.value:
                ui.notify("Please select a deck", color="negative")
                return

            deck_name = deck_select.value
            del decks[deck_name]
            progress.pop(deck_name, None)

            ui.notify(f"Deleted {deck_name}", color="positive")
            dialog.close()
            on_change()

        with ui.row():
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Delete", on_click=confirm_delete, color="negative")

    dialog.open()

#import deck (format must be .txt or .md with each line as a flashcard)
def import_deck_dialog(on_change):
    parsed_cards: list[dict] = []

    with ui.dialog() as dialog, ui.card().classes("w-96 gap-3"):
        ui.label("Upload Deck Here: ").classes("text-lg font-bold")
        ui.label("Upload a .md or .txt file with each line as a flashcard.").classes("text-sm text-gray-500")

        name = ui.input("Deck Name").classes("w-full")
        status_label = ui.label("No file uploaded yet").classes("text-sm text-gray-500")
    
        async def handle_upload(e: events.UploadEventArguments):
            nonlocal parsed_cards

            if not (name.value or "").strip():
                name.value = Path(e.file.name).stem

            parsed_cards = await parse_deck(e.file)

            if parsed_cards:
                status_label.set_text(f"Ready to import {len(parsed_cards)} cards.")
                status_label.classes(replace="text-sm text-green-600 font-medium")
            else:
                status_label.set_text("No valid cards found in the uploaded file.")
                status_label.classes(replace="text-sm text-red-600 font-medium")
            
        ui.upload(on_upload = handle_upload, 
                    auto_upload=True,
                    max_files= 1
                    ).props('accept=.md,.txt').classes("w-full")
        
        def finalize_import():
            deck_name = (name.value or "").strip()
            if not deck_name:
                ui.notify("Please enter a deck name", color="negative")
                return

            if deck_name in decks:
                ui.notify("Deck already exists", color="negative")
                return

            if not parsed_cards:
                ui.notify("No valid cards to import", color="negative")
                return

            if name.value in decks:
                ui.notify("Deck already exists", color="negative")
                return

            decks[name.value] = parsed_cards.copy()

            ui.notify(f"Imported {len(parsed_cards)} cards into '{name.value}'!", color="positive")
            dialog.close()
            on_change()

        with ui.row().classes("w-full gap-2"):
            ui.button("Import Deck", on_click=finalize_import).props("w-full")
            ui.button("Cancel", on_click=dialog.close).props("w-full")
    dialog.open()

    pass
