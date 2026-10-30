from datetime import date

from nicegui import ui

from app.colors import BLUE, BORDER, MUTED, NEGATIVE, TEXT
from app.components import nav_button, progress_indicator
from app.profile import MAX_NAME_LENGTH, clean_display_name, initials, profile_stats
from app.store import decks, profile, progress


#Stat box(# on top, small label under)
def stat_tile(value, label):
    with ui.column().classes(f"flex-1 items-center gap-0 p-3 border border-[{BORDER}] rounded-xl"):
        ui.label(str(value)).classes("text-2xl font-extrabold")
        ui.label(label).classes(f"text-xs text-[{MUTED}]")


# Avatar, name and join date
@ui.refreshable
def profile_header():
    with ui.row().classes("w-full items-center gap-4 p-4"):
        with ui.element("div").classes(
            f"w-16 h-16 rounded-full bg-[{BLUE}] text-white flex items-center justify-center"
        ):
            ui.label(initials(profile["name"])).classes("text-2xl font-bold")

        with ui.column().classes("gap-0"):
            ui.label(profile["name"] or "No name yet").classes("text-xl font-bold")
            if profile["joined"]:
                ui.label(f"Joined {profile['joined']:%B %d, %Y}").classes(f"text-sm text-[{MUTED}]")
            else:
                ui.label("Set a display name to create your profile").classes(f"text-sm text-[{MUTED}]")


# Edit the display name
def edit_name_section():
    with ui.row().classes("w-full items-center gap-2 px-4 no-wrap"):
        name = ui.input("Display name", value=profile["name"]).props(
            f"outlined dense maxlength={MAX_NAME_LENGTH}"
        ).classes("flex-1")

        def save_name():
            cleaned = clean_display_name(name.value)
            if cleaned is None:
                ui.notify(f"Name must be 1 to {MAX_NAME_LENGTH} characters", color="negative")
                return

            profile["name"] = cleaned
            if profile["joined"] is None:
                profile["joined"] = date.today()

            ui.notify("Profile saved!", color="positive")
            profile_header.refresh()

        ui.button("Save", on_click=save_name).props("rounded no-caps unelevated")


# Study totals plus progress for each deck
def stats_section():
    stats = profile_stats(decks, progress)

    ui.label("Study stats").classes(f"w-full text-lg font-bold px-4 pt-6 pb-2 border-t border-[{BORDER}] mt-4")
    with ui.row().classes("w-full gap-2 px-4 no-wrap"):
        stat_tile(stats["decks"], "Decks")
        stat_tile(stats["cards"], "Cards")
        stat_tile(stats["cards_reached"], "Cards reached")
        stat_tile(stats["decks_finished"], "Decks finished")

    ui.label("Deck progress").classes("w-full text-lg font-bold px-4 pt-6 pb-2")
    with ui.column().classes("w-full px-4 gap-3"):
        if not decks:
            ui.label("No decks yet. Create one to start tracking progress.").classes(f"text-[{MUTED}]")
        for deck_name, cards in decks.items():
            with ui.column().classes("w-full gap-1"):
                ui.label(deck_name).classes("font-semibold")
                progress_indicator(progress.get(deck_name, 0), len(cards))


# Profile page. Same layout as home(sudebar and main col)
@ui.page("/profile")
def profile_page():
    ui.colors(primary=BLUE, negative=NEGATIVE)
    ui.query("body").classes(f"bg-white text-[{TEXT}]")
    ui.query(".nicegui-content").classes("p-0")

    with ui.row().classes("w-full justify-center no-wrap gap-0"):
        with ui.column().classes("w-52 sticky top-0 h-screen p-3 gap-1"):
            ui.icon("style", size="lg").classes(f"text-[{BLUE}] m-3")
            nav_button("Decks", "home").on("click", lambda: ui.navigate.to("/"))

        with ui.column().classes(f"w-full max-w-xl min-h-screen gap-0 border-x border-[{BORDER}] pb-8"):
            ui.label("Profile").classes(f"w-full text-xl font-bold p-4 border-b border-[{BORDER}]")
            profile_header()
            edit_name_section()
            stats_section()
