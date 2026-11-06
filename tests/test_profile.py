import asyncio
import importlib
import sys

from nicegui import ui
from nicegui.testing.user_interaction import UserInteraction
from nicegui.testing.user_simulation import user_simulation

from app.db import engine
from app.dev_user import get_test_user_id
from app.profile import clean_display_name, initials, profile_stats
from app.profile_storage import restore_user_profile, save_display_name
from app.store import decks, profile, progress


# helpers

def test_clean_name_trims_spaces():
    assert clean_display_name("  Dagem  ") == "Dagem"

def test_clean_name_rejects_empty():
    assert clean_display_name("   ") is None
    assert clean_display_name(None) is None

def test_clean_name_rejects_too_long():
    assert clean_display_name("a" * 31) is None
    assert clean_display_name("a" * 30) == "a" * 30

def test_initials():
    assert initials("dagem") == "D"
    assert initials("") == "?"

def test_stats_empty():
    assert profile_stats({}, {}) == {"decks": 0, "cards": 0, "cards_reached": 0, "decks_finished": 0}

def test_stats_counts_cards_and_progress():
    card = {"question": "q", "answer": "a"}
    stats = profile_stats({"Bio": [card] * 3, "Chem": [card] * 2, "Empty": []}, {"Bio": 3, "Chem": 1})
    assert stats == {"decks": 3, "cards": 5, "cards_reached": 4, "decks_finished": 1}

def test_stats_caps_progress_at_deck_size():
    card = {"question": "q", "answer": "a"}
    # progress past the end shouldn't overcount
    assert profile_stats({"Bio": [card] * 2}, {"Bio": 9})["cards_reached"] == 2


# Profile page

def run(test_body):
    async def runner():
        decks.clear()
        progress.clear()
        profile.update({"name": "", "joined": None})
        async with user_simulation() as user:
            sys.modules.pop("app.pages.profile", None)
            importlib.import_module("app.pages.profile")
            await user.open("/profile")
            await test_body(user)

    asyncio.run(runner())


def click(user, label):
    buttons = [b for b in user.find(kind=ui.button).elements if b.text == label]
    UserInteraction(user, set(buttons[:1]), None).click()


def test_profile_page_shows_saved_profile():
    async def body(user):
        await user.should_see("Test User")
        await user.should_see("No decks yet")

    run(body)


def test_save_display_name():
    async def body(user):
        user.find("Display name").clear().type("Dagem")
        click(user, "Save")
        await user.should_see("Profile saved!")
        assert profile["name"] == "Dagem"
        assert profile["joined"] is not None

    run(body)


def test_saved_name_survives_a_restart():
    async def body(user):
        user.find("Display name").clear().type("Dagem")
        click(user, "Save")
        await user.should_see("Profile saved!")

    run(body)

    # run() wipes the in-memory profile, same as restarting the app
    async def after_restart(user):
        await user.should_see("Dagem")
        assert profile["name"] == "Dagem"

    run(after_restart)


def test_blank_name_is_rejected():
    async def body(user):
        user.find("Display name").clear()
        click(user, "Save")
        await user.should_see("Name must be 1 to 30 characters")
        assert profile["name"] == "Test User"

    run(body)


# Saving to the database

def test_save_and_restore_profile():
    user_id = get_test_user_id()
    with engine.begin() as conn:
        save_display_name(conn, user_id, "Dagem")

    loaded = {"name": "", "joined": None}
    with engine.connect() as conn:
        restore_user_profile(conn, user_id, loaded)

    assert loaded["name"] == "Dagem"
    assert loaded["joined"] is not None


def test_restore_leaves_profile_alone_for_unknown_user():
    loaded = {"name": "", "joined": None}
    with engine.connect() as conn:
        restore_user_profile(conn, 999, loaded)

    assert loaded == {"name": "", "joined": None}
