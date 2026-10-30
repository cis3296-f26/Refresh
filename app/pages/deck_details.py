from nicegui import ui
from urllib.parse import unquote

from app.components import nav_button, progress_indicator
from app.deck_actions import add_card_dialog, delete_card_dialog, edit_card_dialog
from app.colors import BLUE, BORDER, MUTED, NEGATIVE, TEXT
from app.store import decks

@ui.page("/deck_details/{deck_name}")
def card_details(deck_name: str):
    deck_name = unquote(deck_name)
    
    ui.colors(primary=BLUE, negative=NEGATIVE)
    ui.query("body").classes(f"bg-white text-[{TEXT}]")
    ui.query(".nicegui-content").classes("p-0")
    
    with ui.row().classes("w-full justify-center no-wrap gap-0"):
        sidebar()
        with ui.column().classes(f"w-full max-w-4xl min-h-screen gap-0 border-x border-[{BORDER}]"): 
            search = ui.input("Search cards...", placeholder="Type to search...").classes("w-full px-8 pt-6")
            search.on_value_change(lambda e: display_cards.refresh(deck_name, e.value or ""))
            display_cards(deck_name)
# Left sidebar: logo and action buttons
def sidebar():
    with ui.column().classes("w-52 sticky top-0 h-screen p-3 gap-1"):
        ui.icon("style", size="lg").classes(f"text-[{BLUE}] m-3")
        nav_button("Home", "home").on(
            "click", lambda: ui.navigate.to("/")
        )

@ui.refreshable
def display_cards(deck_name: str, search_text: str = ""):
    ui.label(f"Cards in {deck_name}").classes(
            f"w-full text-xl font-bold p-4 border-b border-[{BORDER}]"
        )    
    cards  = decks.get(deck_name, [])
    query = (search_text or "").strip().lower() 

    filtered_cards = [
        card for card in cards
        if not query or query in card["question"].lower() or query in card["answer"].lower()
    ]

    with ui.column().classes("w-full p-8 gap-6"):
        if not cards:
            with ui.column().classes("w-full items-center p-8 gap-6"):
                ui.label("No cards yet").classes("text-3xl font-extrabold")
                ui.label("Create a card to start studying.").classes(f"text-[{MUTED}]")
            
        else:
         with ui.grid(columns = 3).classes("w-full items-start justify-center p-8 gap-4") as grid:

            if not query:
                grid.make_sortable(on_end=lambda e: reorder_cards(deck_name, e))

            for card in filtered_cards:
                with ui.card().classes(f"w-full p-4 gap-2 rounded-xl border border-[{BORDER}]"):
                    with ui.column().classes("w-full items-start justify-between no-wrap gap-4"):
                        with ui.column().classes("gap-1 flex-1"):
                            ui.label(card["question"]).classes("text-md font-large")
                            ui.label(card["answer"]).classes("text-sm text-gray-500")
                        with ui.row().classes("gap-1 shrink-0 justify-end"):
                            ui.button(icon = "edit", on_click=lambda c=card: edit_card_dialog(deck_name, cards.index(c), display_cards.refresh)).props("flat round dense size=sm").classes("text-gray-500 hover:text-blue-500")
                            ui.button(icon = "delete", on_click=lambda c=card: delete_card_dialog(deck_name, cards.index(c), display_cards.refresh)).props("flat round dense size=sm").classes("text-gray-500 hover:text-red-500")
        ui.button(icon = "add", on_click=lambda: add_card_dialog(cards, display_cards.refresh)).props("rounded no-caps unelevated dense").classes("w-full mt-3 text-sm font-bold py-2")         

def reorder_cards(deck_name: str, event):
    cards = decks.get(deck_name, [])
    if 0 <= event.old_index < len(cards) and 0 <= event.new_index < len(cards):
        card = cards.pop(event.old_index)
        cards.insert(event.new_index, card)
        ui.notify("Cards reordered successfully!", color="positive")
    display_cards.refresh()  
    
