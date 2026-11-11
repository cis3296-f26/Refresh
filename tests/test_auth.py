import asyncio
import importlib
import sys

from nicegui import ui
from nicegui.testing.user_interaction import UserInteraction
from nicegui.testing.user_simulation import user_simulation
from sqlalchemy import select

from app.auth import clean_username, create_user, verify_user
from app.db import engine, users


# helpers

def test_clean_username():
    assert clean_username("  Dagem ") == "dagem"
    assert clean_username("ab") is None
    assert clean_username("a" * 31) is None
    assert clean_username("has space") is None
    assert clean_username("dagem_44.x") == "dagem_44.x"


def test_sign_up_then_log_in():
    user_id, error = create_user("Dagem", "secret123")
    assert error is None
    assert verify_user("dagem", "secret123") == user_id
    assert verify_user("DAGEM", "secret123") == user_id


def test_wrong_password_and_unknown_user():
    create_user("dagem", "secret123")
    assert verify_user("dagem", "wrong-pass") is None
    assert verify_user("nobody", "secret123") is None


def test_password_is_hashed_not_saved_as_text():
    create_user("dagem", "secret123")
    with engine.connect() as conn:
        saved = conn.execute(select(users.c.password_hash).where(users.c.username == "dagem")).scalar_one()
    assert saved != "secret123"
    assert saved.startswith("$2")


def test_duplicate_username_is_rejected():
    create_user("dagem", "secret123")
    user_id, error = create_user("Dagem", "another1")
    assert user_id is None
    assert error == "That username is taken"


def test_short_password_is_rejected():
    user_id, error = create_user("dagem", "123")
    assert user_id is None
    assert "at least 6" in error


def test_new_user_gets_display_name_and_join_date():
    create_user("dagem", "secret123")
    with engine.connect() as conn:
        row = conn.execute(select(users.c.display_name, users.c.joined)).one()
    assert row.display_name == "dagem"
    assert row.joined is not None


# Pages

def run(test_body, path):
    async def runner():
        async with user_simulation() as user:
            for module in ("app.pages.login", "app.pages.home"):
                sys.modules.pop(module, None)
                importlib.import_module(module)
            await user.open(path)
            await test_body(user)

    asyncio.run(runner())


def click(user, label):
    buttons = [b for b in user.find(kind=ui.button).elements if b.text == label]
    UserInteraction(user, set(buttons[:1]), None).click()


def test_signup_page_creates_account():
    async def body(user):
        user.find("Username").type("newuser")
        inputs = user.find(kind=ui.input).elements
        password, confirm = [i for i in inputs if i.props.get("label") in ("Password", "Confirm password")]
        password.set_value("secret123")
        confirm.set_value("secret123")
        click(user, "Sign up")
        await asyncio.sleep(0.1)
        assert verify_user("newuser", "secret123") is not None

    run(body, "/signup")


def test_signup_page_rejects_mismatched_passwords():
    async def body(user):
        user.find("Username").type("newuser")
        inputs = user.find(kind=ui.input).elements
        password, confirm = [i for i in inputs if i.props.get("label") in ("Password", "Confirm password")]
        password.set_value("secret123")
        confirm.set_value("different")
        click(user, "Sign up")
        await user.should_see("Passwords don't match")
        assert verify_user("newuser", "secret123") is None

    run(body, "/signup")


def test_login_page_rejects_wrong_password():
    create_user("dagem", "secret123")

    async def body(user):
        user.find("Username").type("dagem")
        inputs = user.find(kind=ui.input).elements
        [password] = [i for i in inputs if i.props.get("label") == "Password"]
        password.set_value("nope-nope")
        click(user, "Log in")
        await user.should_see("Wrong username or password")

    run(body, "/login")
