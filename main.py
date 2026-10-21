import os

from nicegui import ui


@ui.page("/")
def home():
    with ui.header():
        ui.label("Refresh").classes("text-2xl font-bold")
    ui.label("Study smarter with flashcards.").classes("p-4")


ui.run(
    title="Refresh",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8080)),
    reload=False,
)
