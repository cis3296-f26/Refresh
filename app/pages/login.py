from nicegui import ui

from app.auth import (
    MAX_USERNAME_LENGTH, MIN_PASSWORD_LENGTH, create_user, log_in, session, verify_user,
)
from app.colors import BLUE, BORDER, MUTED, NEGATIVE, TEXT


# Shared look for the login and sign up
def auth_layout(title, subtitle):
    ui.colors(primary=BLUE, negative=NEGATIVE)
    ui.query("body").classes(f"bg-white text-[{TEXT}]")

    with ui.column().classes("w-full min-h-screen items-center justify-center"):
        card = ui.column().classes(f"w-full max-w-sm gap-4 p-8 border border-[{BORDER}] rounded-2xl")
        with card:
            ui.icon("style", size="xl").classes(f"text-[{BLUE}] self-center")
            ui.label(title).classes("text-2xl font-extrabold self-center")
            ui.label(subtitle).classes(f"text-sm text-[{MUTED}] self-center -mt-3")
    return card


@ui.page("/login")
def login_page():
    # Already logged in, skip straight to the decks
    storage = session()
    if storage is not None and storage.get("user_id") is not None:
        ui.navigate.to("/")
        return

    with auth_layout("Log in to Refresh", "Welcome back"):
        username = ui.input("Username").props("outlined").classes("w-full")
        password = ui.input("Password", password=True, password_toggle_button=True).props(
            "outlined"
        ).classes("w-full")

        def try_login():
            user_id = verify_user(username.value, password.value)
            if user_id is None:
                ui.notify("Wrong username or password", color="negative")
                return
            log_in(user_id)
            ui.navigate.to("/")

        password.on("keydown.enter", try_login)
        ui.button("Log in", on_click=try_login).props("rounded no-caps unelevated").classes("w-full")

        with ui.row().classes("w-full justify-center gap-1"):
            ui.label("New here?").classes(f"text-sm text-[{MUTED}]")
            ui.link("Create an account", "/signup").classes(f"text-sm text-[{BLUE}]")


@ui.page("/signup")
def signup_page():
    storage = session()
    if storage is not None and storage.get("user_id") is not None:
        ui.navigate.to("/")
        return

    with auth_layout("Create your account", "Start studying with Refresh"):
        username = ui.input("Username").props(f"outlined maxlength={MAX_USERNAME_LENGTH}").classes("w-full")
        password = ui.input("Password", password=True, password_toggle_button=True).props(
            "outlined"
        ).classes("w-full")
        confirm = ui.input("Confirm password", password=True).props("outlined").classes("w-full")
        ui.label(f"At least {MIN_PASSWORD_LENGTH} characters").classes(f"text-xs text-[{MUTED}] -mt-3")

        def try_signup():
            if password.value != confirm.value:
                ui.notify("Passwords don't match", color="negative")
                return
            user_id, error = create_user(username.value, password.value)
            if error:
                ui.notify(error, color="negative")
                return
            log_in(user_id)
            ui.navigate.to("/")

        confirm.on("keydown.enter", try_signup)
        ui.button("Sign up", on_click=try_signup).props("rounded no-caps unelevated").classes("w-full")

        with ui.row().classes("w-full justify-center gap-1"):
            ui.label("Already have an account?").classes(f"text-sm text-[{MUTED}]")
            ui.link("Log in", "/login").classes(f"text-sm text-[{BLUE}]")
