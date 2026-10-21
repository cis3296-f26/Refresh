import os

from nicegui import ui

BLUE = "#1d9bf0"
TEXT = "#0f1419"
MUTED = "#536471"
BORDER = "#eff3f4"


def nav_button(label, icon):
    return ui.button(label, icon=icon).props("flat no-caps align=left dense").classes(
        f"w-full text-sm font-semibold rounded-full px-3 py-1 text-[{TEXT}] "
        "hover:bg-[#e7e7e8] [&>.q-btn__content]:justify-start"
    )


@ui.page("/")
def home():
    ui.colors(primary=BLUE, negative="#f4212e")
    ui.query("body").classes(f"bg-white text-[{TEXT}]")
    ui.query(".nicegui-content").classes("p-0")

    with ui.row().classes("w-full justify-center no-wrap gap-0"):
        # Left sidebar
        with ui.column().classes("w-52 sticky top-0 h-screen p-3 gap-1"):
            ui.icon("style", size="lg").classes(f"text-[{BLUE}] m-3")
            nav_button("Add card", "note_add")
            nav_button("Import deck", "upload_file")
            nav_button("Delete deck", "delete")
            ui.button("Create deck").props("rounded no-caps unelevated dense").classes(
                "w-full mt-3 text-sm font-bold py-2"
            )

        # Main column
        with ui.column().classes(f"w-full max-w-xl min-h-screen gap-0 border-x border-[{BORDER}]"):
            ui.label("Decks").classes(f"w-full text-xl font-bold p-4 border-b border-[{BORDER}]")
            with ui.column().classes("w-full items-center p-12 gap-1"):
                ui.label("No decks yet").classes("text-3xl font-extrabold")
                ui.label("Create a deck to start studying.").classes(f"text-[{MUTED}]")


ui.run(
    title="Refresh",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8080)),
    reload=False,
)
