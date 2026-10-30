import os

from nicegui import ui

# Importing the page module registers the "/" and "/profile" routes
import app.pages.home  # noqa: F401
import app.pages.profile  # noqa: F401

ui.run(
    title="Refresh",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8080)),
    reload=False,
)
