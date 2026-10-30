import asyncio
import importlib
import sys

from nicegui import ui
from nicegui.elements.upload_files import SmallFileUpload
from nicegui.testing.user_interaction import UserInteraction
from nicegui.testing.user_simulation import user_simulation

from app.store import decks

def run(test_body, path="/"):
    async def runner():
        decks.clear()
        async with user_simulation() as user:
            for module in ("app.pages.home", "app.pages.deck_details"):
                sys.modules.pop(module, None)
                importlib.import_module(module)
            await user.open(path)
            await test_body(user)

    asyncio.run(runner())


# Click the button whose label is exactly `label`. NiceGUI's content search
# matches substrings, so "Create" would also hit the "Create deck" sidebar button.
def click(user, label):
    buttons = [b for b in user.find(kind=ui.button).elements if b.text == label]
    UserInteraction(user, set(buttons[:1]), None).click()


# Click the icon-only button showing `icon` (e.g. the "add" button on a deck page)
def click_icon(user, icon):
    buttons = [b for b in user.find(kind=ui.button).elements if b.props.get("icon") == icon]
    UserInteraction(user, set(buttons[:1]), None).click()


# Pick `value` in the (only) select box of the open dialog
def choose(user, value):
    user.find(ui.select).elements.pop().set_value(value)


# Create deck ---------------------------------------------------------------

# Creating a deck adds it to the list with zero cards
def test_create_deck():
    async def body(user):
        click(user, "Create deck")
        user.find("Deck Name").type("Biology")
        click(user, "Create")
        await user.should_see("Deck created successfully!")
        assert decks == {"Biology": []}

    run(body)


# An empty name is rejected
def test_create_deck_needs_name():
    async def body(user):
        click(user, "Create deck")
        click(user, "Create")
        await user.should_see("Please enter a deck name")
        assert decks == {}

    run(body)


# A name that already exists is rejected and the old deck is kept
def test_create_deck_duplicate():
    async def body(user):
        decks["Biology"] = [{"question": "Q", "answer": "A"}]
        click(user, "Create deck")
        user.find("Deck Name").type("Biology")
        click(user, "Create")
        await user.should_see("Deck already exists")
        assert len(decks["Biology"]) == 1

    run(body)


# Add card ------------------------------------------------------------------

# With no decks there is nowhere to add a card
def test_add_card_without_decks():
    async def body(user):
        click_icon(user, "add")
        await user.should_see("Create a deck first!")

    run(body, "/deck_details/Biology")


# A card with a question and answer is saved into the deck being viewed
def test_add_card():
    async def body(user):
        decks["Biology"] = []
        await user.open("/deck_details/Biology")
        click_icon(user, "add")
        user.find("Question").type("What is DNA?")
        user.find("Answer").type("Genetic material")
        click(user, "Save Card")
        await user.should_see("Flashcard added successfully!")
        assert decks["Biology"] == [
            {"question": "What is DNA?", "answer": "Genetic material"}
        ]

    run(body)


# Saving without filling in both fields is rejected
def test_add_card_needs_both_fields():
    async def body(user):
        decks["Biology"] = []
        await user.open("/deck_details/Biology")
        click_icon(user, "add")
        user.find("Question").type("Only a question")
        click(user, "Save Card")
        await user.should_see("Please fill in both fields")
        assert decks["Biology"] == []

    run(body)


# Delete deck ---------------------------------------------------------------

# With no decks there is nothing to delete
def test_delete_deck_without_decks():
    async def body(user):
        click(user, "Delete deck")
        await user.should_see("No decks to delete")

    run(body)


# Deleting removes only the selected deck
def test_delete_deck():
    async def body(user):
        decks["Biology"] = []
        decks["History"] = []
        click(user, "Delete deck")
        choose(user, "Biology")
        click(user, "Delete")
        await user.should_see("Deleted Biology")
        assert list(decks) == ["History"]

    run(body)


# Import deck ---------------------------------------------------------------

# Upload the bundled example file into the open import dialog
async def upload_example(user):
    with open("example/example_deck.txt", "rb") as f:
        data = f.read()
    upload = user.find(ui.upload).elements.pop()
    await upload.handle_uploads(
        [SmallFileUpload(name="example_deck.txt", content_type="text/plain", _data=data)]
    )
    await user.should_see("Ready to import 3 cards.")


# Importing the example file creates a deck named after the file with 3 cards
def test_import_deck():
    async def body(user):
        click(user, "Import deck")
        await upload_example(user)
        click(user, "Import Deck")
        await user.should_see("Imported 3 cards")
        assert len(decks["example_deck"]) == 3

    run(body)


# Importing with no file uploaded is rejected
def test_import_deck_needs_file():
    async def body(user):
        click(user, "Import deck")
        user.find("Deck Name").type("Empty")
        click(user, "Import Deck")
        await user.should_see("No valid cards to import")
        assert decks == {}

    run(body)


# Importing under an existing name is rejected and the old deck is kept
def test_import_deck_duplicate_name():
    async def body(user):
        decks["example_deck"] = []
        click(user, "Import deck")
        await upload_example(user)
        click(user, "Import Deck")
        await user.should_see("Deck already exists")
        assert decks["example_deck"] == []

    run(body)
