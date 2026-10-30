from pathlib import Path

from nicegui import ui,events
from app.store import decks, progress


# Each dialog takes an on_change callback that refreshes the deck list after a change

async def parse_deck(uploaded_file) -> list[dict]:
    content = await uploaded_file.text()

    cards = []
    for line in content.splitlines():
        cleaned = line.strip()

        if not cleaned or cleaned.startswith('#'):
            continue

        for delimiter in ('|', '\t', ',', ';', '::', ':'):
            if delimiter in cleaned:
                question, answer = cleaned.split(delimiter, 1)
                q_clean, a_clean = question.strip(), answer.strip()
                if q_clean and a_clean:
                    cards.append({"question": q_clean, "answer": a_clean})
                break

    return cards

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

# Add a flashcard to an existing deck
def add_card_dialog(cards ,on_change):
    if not decks:
        ui.notify("Create a deck first!", color="negative")
        return

    with ui.dialog() as dialog, ui.card().classes("w-96 gap-4"):
        ui.label("Add Flashcard").classes("text-lg font-bold")

        question = ui.input("Question").classes("w-full")
        answer = ui.textarea("Answer").classes("w-full")

        # Validate the inputs, then append the card to the chosen deck
        def save_card():

            question_text = (question.value or "").strip()
            answer_text = (answer.value or "").strip()

            if not question_text or not answer_text:
                ui.notify("Please fill in both fields", color="negative")
                return

            cards.append({
                "question": question_text,
                "answer": answer_text
            })

            ui.notify("Flashcard added successfully!", color="positive")
            dialog.close()
            on_change()

        ui.button("Save Card", on_click=save_card)

        ui.label("Or import a deck from a file").classes("text-sm text-gray-500")
        ui.button("Import Deck", on_click=lambda: import_deck_dialog(on_change)).props("flat").classes("text-blue-600 hover:text-blue-800")

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

def edit_card_dialog(deck_name: str, card_index: int, on_change):

    cards = decks.get(deck_name, [])
    if not (0 <= card_index < len(cards)):
        return  # Invalid index, do nothing
    
    card = cards[card_index]

    with ui.dialog() as dialog, ui.card().classes("w-96 gap-4"):
        ui.label("Edit Flashcard").classes("text-lg font-bold")

        question = ui.input("Question", value=card["question"]).classes("w-full")
        answer = ui.textarea("Answer", value=card["answer"]).classes("w-full")

        def save_edits():
            question_text = (question.value or "").strip()
            answer_text = (answer.value or "").strip()

            if not question_text or not answer_text:
                ui.notify("Please fill in both fields", color="negative")
                return

            cards[card_index] = {
                "question": question_text,
                "answer": answer_text
            }

            ui.notify("Flashcard updated successfully!", color="positive")
            dialog.close()
            on_change()
        ui.button("Cancel", on_click=dialog.close).props("flat no-caps")
        ui.button("Save Changes", on_click=save_edits).props("unelevated no-caps").classes("bg-blue-600 text-white hover:bg-blue-700")

    dialog.open()

def delete_card_dialog(deck_name: str, card_index: int, on_change):
    cards = decks.get(deck_name, [])
    if not (0 <= card_index < len(cards)):
        return  # Invalid index, do nothing

    with ui.dialog() as dialog, ui.card().classes("w-96 gap-4"):
        ui.label("Delete Flashcard").classes("text-lg font-bold")
        ui.label(f"Are you sure you want to delete this flashcard?").classes("text-sm text-gray-600")

        def confirm_delete():
            cards.pop(card_index)
            if deck_name in progress:
                progress[deck_name] = min(progress[deck_name], len(cards))
            ui.notify("Flashcard deleted successfully!", color="positive")
            dialog.close()
            on_change()

        with ui.row().classes("w-full gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("w-full")
            ui.button("Delete", on_click=confirm_delete, color="negative").props("w-full")

    dialog.open()
