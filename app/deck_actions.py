from nicegui import ui

from app.store import decks


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


# Add a flashcard to an existing deck
def add_card_dialog(on_change):
    if not decks:
        ui.notify("Create a deck first!", color="negative")
        return

    with ui.dialog() as dialog, ui.card():
        ui.label("Add Flashcard").classes("text-lg font-bold")

        deck_select = ui.select(
            list(decks.keys()),
            label="Select Deck"
        ).classes("w-full")

        question = ui.input("Question").classes("w-full")
        answer = ui.textarea("Answer").classes("w-full")

        # Validate the inputs, then append the card to the chosen deck
        def save_card():
            if not deck_select.value:
                ui.notify("Please select a deck", color="negative")
                return

            question_text = (question.value or "").strip()
            answer_text = (answer.value or "").strip()

            if not question_text or not answer_text:
                ui.notify("Please fill in both fields", color="negative")
                return

            decks[deck_select.value].append({
                "question": question_text,
                "answer": answer_text
            })

            ui.notify("Flashcard added successfully!", color="positive")
            dialog.close()
            on_change()

        ui.button("Save Card", on_click=save_card)

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

            ui.notify(f"Deleted {deck_name}", color="positive")
            dialog.close()
            on_change()

        with ui.row():
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Delete", on_click=confirm_delete, color="negative")

    dialog.open()
