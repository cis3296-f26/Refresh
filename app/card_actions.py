from nicegui import ui
from app.store import decks, progress
from app.db import engine
from app.deck_storage import update_saved_deck
from app.dev_user import get_test_user_id


def add_card_dialog(deck_name, cards, on_change):
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

            new_card = {
                "question": question_text,
                "answer": answer_text,
            }

            try:
                user_id = get_test_user_id()

                with engine.begin() as conn:
                    update_saved_deck(
                        conn,
                        user_id,
                        deck_name,
                        cards + [new_card]
                    )

            except Exception as e:
                print("Database card saving error:", repr(e))
                ui.notify("Could not save flashcard", color="negative")
                return

            cards.append(new_card)

            ui.notify("Flashcard added successfully!", color="positive")
            dialog.close()
            on_change()

        ui.button("Save Card", on_click=save_card)

    dialog.open()


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

            updated_cards = cards.copy()
            updated_cards[card_index] = {
                "question": question_text,
                "answer": answer_text
            }

            try:
                user_id = get_test_user_id()

                with engine.begin() as conn:
                    update_saved_deck(
                        conn, user_id, deck_name, updated_cards
                    )

            except Exception as e:
                print("Database card update error:", repr(e))
                ui.notify("Could not update flashcard", color="negative")
                return

            cards[:] = updated_cards

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
            updated_cards = cards.copy()
            updated_cards.pop(card_index)

            try:
                user_id = get_test_user_id()

                with engine.begin() as conn:
                    update_saved_deck(
                        conn, user_id, deck_name, updated_cards
                    )

            except Exception as e:
                print("Database card deletion error:", repr(e))
                ui.notify("Could not delete flashcard", color="negative")
                return

            cards[:] = updated_cards

            if deck_name in progress:
                progress[deck_name] = min(
                    progress[deck_name], len(cards)
                )

            ui.notify("Flashcard deleted successfully!", color="positive")
            dialog.close()
            on_change()

        with ui.row().classes("w-full gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("w-full")
            ui.button(
                "Delete",
                on_click=confirm_delete,
                color="negative"
            ).props("w-full")
            
    dialog.open()
