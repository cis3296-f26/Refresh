
from asyncio import events
import os
from nicegui import ui

BLUE = "#1d9bf0"
TEXT = "#0f1419"
MUTED = "#536471"
BORDER = "#eff3f4"

decks = {}


def nav_button(label, icon):
    return ui.button(label, icon=icon).props("flat no-caps align=left dense").classes(
        f"w-full text-sm font-semibold rounded-full px-3 py-1 text-[{TEXT}] "
        "hover:bg-[#e7e7e8] [&>.q-btn__content]:justify-start"
    )

async def parse_deck(uploaded_file):
    text_content = await uploaded_file.text()

    for line in text_content.splitlines():
        cleaned = line.strip()

        if not cleaned or cleaned.startswith('#'):
            continue
        
        yield cleaned


@ui.page("/")
def home():
    ui.colors(primary=BLUE, negative="#f4212e")
    ui.query("body").classes(f"bg-white text-[{TEXT}]")
    ui.query(".nicegui-content").classes("p-0")

    # Display all created decks
    @ui.refreshable
    def display_decks():
        with ui.column().classes("w-full items-center p-12 gap-1"):
            if not decks:
                ui.label("No decks yet").classes("text-3xl font-extrabold")
                ui.label("Create a deck to start studying.").classes(
                    f"text-[{MUTED}]"
                )
            else:
                for deck_name in decks:
                    with ui.column().classes("w-full gap-1"):
                        ui.label(deck_name).classes(
                            "text-lg font-semibold"
                        )
                        ui.label(
                            f"{len(decks[deck_name])} cards"
                        ).classes(f"text-sm text-[{MUTED}]")
    #save deck
    def save_deck(name, dialog):
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
        display_decks.refresh()

    # Create a new deck
    def create_deck(name=None):
        with ui.dialog() as dialog, ui.card():
            ui.label("Create a New Deck").classes("text-lg font-bold")
            
            if name:
                name.set_text(name)

            name = ui.input("Deck Name").classes("w-full")
            ui.button("Create", on_click=save_deck(name, dialog)).classes("w-full")

        dialog.open()

    # Add a flashcard to an existing deck
    def add_card():
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

            def save_card():
                if not deck_select.value:
                    ui.notify("Please select a deck", color="negative")
                    return

                question_text = (question.value or "").strip()
                answer_text = (answer.value or "").strip()

                if not question_text or not answer_text:
                    ui.notify(
                        "Please fill in both fields",
                        color="negative"
                    )
                    return

                decks[deck_select.value].append({
                    "question": question_text,
                    "answer": answer_text
                })

                ui.notify(
                    "Flashcard added successfully!",
                    color="positive"
                )
                dialog.close()
                display_decks.refresh()

            ui.button("Save Card", on_click=save_card)

        dialog.open()

    def import_deck():
        with ui.dialog() as dialog, ui.card():
            ui.label("Upload Deck Here: ")
            
        output_container = None
        async def handle_upload(e: events.UploadEventArguments):
            output_container.clear()

            with output_container:
                create_deck()
            name.set_text(e.name)
            dialog.close()
            
        ui.upload(on_upload = handle_upload, max_files= 1).props('accept=.md,.txt')

        name = ui.input("Deck Name").classes("w-full")
        save_deck(name,dialog)
        ui.button("Create", on_click=save_deck)

        save_deck()

        pass
    with ui.row().classes("w-full justify-center no-wrap gap-0"):

        # Left sidebar
        with ui.column().classes("w-52 sticky top-0 h-screen p-3 gap-1"):
            ui.icon("style", size="lg").classes(f"text-[{BLUE}] m-3")

            nav_button("Add card", "note_add").on(
                "click", add_card
            )

            nav_button("Import deck", "upload_file").on_click(import_deck)
            nav_button("Delete deck", "delete")

            ui.button(
                "Create deck",
                on_click=create_deck
            ).props("rounded no-caps unelevated dense").classes(
                "w-full mt-3 text-sm font-bold py-2"
            )

        # Main column
        with ui.column().classes(
            f"w-full max-w-xl min-h-screen gap-0 border-x border-[{BORDER}]"
        ):
            ui.label("Decks").classes(
                f"w-full text-xl font-bold p-4 border-b border-[{BORDER}]"
            )

            display_decks()

    
ui.run(
    title="Refresh",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8080)),
    reload=False,
)
