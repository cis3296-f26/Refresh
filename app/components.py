from nicegui import ui

from app.colors import MUTED, TEXT
from app.progress import progress_fraction, progress_label, today_progress


# Flat, left-aligned sidebar button with a hover highlight
def nav_button(label, icon):
    return ui.button(label, icon=icon).props("flat no-caps align=left dense").classes(
        f"w-full text-sm font-semibold rounded-full px-3 py-1 text-[{TEXT}] "
        "hover:bg-[#e7e7e8] [&>.q-btn__content]:justify-start"
    )


# "X of N cards studied" label with a bar showing how far into the deck the user is
def progress_indicator(done, total):
    with ui.row().classes("w-full items-center gap-1"):
        ui.label(progress_label(done, total)).classes(f"text-sm text-[{MUTED}]")
        ui.linear_progress(value=progress_fraction(done, total), show_value=False).props("rounded").classes("w-full")

def today_indicator(cards):
    p = today_progress(cards)
    progress_indicator(p["done"], p["total"])