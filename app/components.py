from nicegui import ui

from app.colors import MUTED, TEXT
from app.progress import progress_fraction, progress_label


# Flat, left-aligned sidebar button with a hover highlight
def nav_button(label, icon):
    return ui.button(label, icon=icon).props("flat no-caps align=left dense").classes(
        f"w-full text-sm font-semibold rounded-full px-3 py-1 text-[{TEXT}] "
        "hover:bg-[#e7e7e8] [&>.q-btn__content]:justify-start"
    )


# "X of N cards" label with a bar showing how far into the deck the user is
def progress_indicator(reached, total):
    ui.label(progress_label(reached, total)).classes(f"text-sm text-[{MUTED}]")
    ui.linear_progress(value=progress_fraction(reached, total), show_value=False).props("rounded")
