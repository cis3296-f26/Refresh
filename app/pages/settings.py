from nicegui import ui

from app.auth import current_user_id, log_out, require_login
from app.colors import BLUE, BORDER, MUTED, NEGATIVE, TEXT
from app.components import nav_button
from app.db import engine
from app.fsrs_settings import DEFAULTS, clean_settings
from app.settings_storage import restore_user_settings, save_user_settings
from app.store import settings

def setting_label(text, description):
    with ui.row().classes("items-center gap-1 no-wrap cursor-help"):
        label = ui.label(text).classes("text-sm font-semibold")
        ui.icon("settings", size="xs").classes(f"text-[{MUTED}]")
        ui.tooltip(description).classes("text-sm").props("max-width=280px")
    return label

def fsrs_form():
    with ui.column().classes("w-full p-4 gap-5"):
        retention_label = setting_label(
            "Desired retention",
            "How likely you want to be to remember a card when it comes back. "
            "Higher means shorter gaps and more daily reviews. 90% is the standard choice.",
        )
        retention = ui.slider(min=0.7, max=0.97, step=0.01,
                              value=settings["desired_retention"]).props("label-always")
        retention_label.bind_text_from(retention, "value", lambda v: f"Desired retention: {v:.0%}")

        setting_label(
            "Learning steps",
            "How soon a new card comes back before it graduates to normal spaced review. "
            "'1m 10m' means 1 minute, then 10 minutes. Use m, h or d, shortest first. "
            "Leave empty to skip learning.",
        )
        learning = ui.input(value=settings["learning_steps"], placeholder="1m 10m") \
            .props("outlined dense").classes("w-full")

        setting_label(
            "Relearning steps",
            "Same idea for cards you knew and then forgot (pressed Again). "
            "'10m' means a lapsed card returns after 10 minutes.",
        )
        relearning = ui.input(value=settings["relearning_steps"], placeholder="10m") \
            .props("outlined dense").classes("w-full")

        setting_label(
            "Maximum interval (days)",
            "The longest gap allowed between reviews of a card. Lower it if you want "
            "well-known cards to keep resurfacing, e.g. 180 for a semester.",
        )
        max_int = ui.number(value=settings["maximum_interval"], min=1, max=36500, precision=0) \
            .props("outlined dense").classes("w-full")

        with ui.row().classes("items-center gap-1 no-wrap cursor-help"):
            fuzz = ui.switch("Randomize intervals slightly", value=settings["enable_fuzzing"])
            ui.icon("info", size="xs").classes(f"text-[{MUTED}]")
            ui.tooltip(
                "Adds a small random offset to review dates so cards learned together "
                "don't all come due on the same day. Recommended on."
            ).classes("text-sm").props("max-width=280px")

        ui.label("Changes apply to your next reviews; existing due dates stay as they are.") \
            .classes(f"text-xs text-[{MUTED}]")

        def current_values():
            return {
                "desired_retention": retention.value,
                "learning_steps": learning.value,
                "relearning_steps": relearning.value,
                "maximum_interval": max_int.value,
                "enable_fuzzing": fuzz.value,
            }

        def save():
            user_id = current_user_id()
            if user_id is None:
                ui.navigate.to("/login")
                return
            try:
                cleaned = clean_settings(current_values())
                with engine.begin() as conn:
                    save_user_settings(conn, user_id, cleaned)
            except ValueError as e:
                ui.notify(str(e), color="negative")
                return
            except Exception as e:
                print("Database settings error:", repr(e))
                ui.notify("Could not save settings", color="negative")
                return
            settings.update(cleaned)
            ui.notify("Settings saved", color="positive")

        def reset():
            retention.value = DEFAULTS["desired_retention"]
            learning.value = DEFAULTS["learning_steps"]
            relearning.value = DEFAULTS["relearning_steps"]
            max_int.value = DEFAULTS["maximum_interval"]
            fuzz.value = DEFAULTS["enable_fuzzing"]
            ui.notify("Defaults restored. Press Save to keep them.")

        with ui.row().classes("w-full gap-2 pt-2"):
            ui.button("Save", on_click=save).props("rounded no-caps unelevated")
            ui.button("Reset to defaults", on_click=reset).props("rounded no-caps flat")


@ui.page("/settings")
def settings_page():
    user_id = require_login()
    if user_id is None:
        return

    try:
        with engine.connect() as conn:
            restore_user_settings(conn, user_id, settings)
    except Exception as e:
        print("Database loading error:", repr(e))
        ui.notify("Could not load saved settings", color="negative")

    ui.colors(primary=BLUE, negative=NEGATIVE)
    ui.query("body").classes(f"bg-white text-[{TEXT}]")
    ui.query(".nicegui-content").classes("p-0")

    with ui.row().classes("w-full justify-center no-wrap gap-0"):
        with ui.column().classes("w-52 sticky top-0 h-screen p-3 gap-1"):
            ui.icon("style", size="lg").classes(f"text-[{BLUE}] m-3")
            nav_button("Decks", "home").on("click", lambda: ui.navigate.to("/"))
            nav_button("Profile", "person").on("click", lambda: ui.navigate.to("/profile"))
            nav_button("Log out", "logout").on("click", log_out)

        with ui.column().classes(f"w-full max-w-xl min-h-screen gap-0 border-x border-[{BORDER}] pb-8"):
            ui.label("Settings").classes(f"w-full text-xl font-bold p-4 border-b border-[{BORDER}]")
            ui.label("Spaced repetition").classes("w-full text-lg font-bold px-4 pt-4")
            fsrs_form()