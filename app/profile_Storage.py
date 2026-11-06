from sqlalchemy import select, update

from app.db import users


# Load the saved name and join date back into the app
def restore_user_profile(conn, user_id, profile):
    saved = conn.execute(
        select(users.c.display_name, users.c.joined).where(users.c.id == user_id)
    ).one_or_none()

    if saved is None:
        return

    profile["name"] = saved.display_name
    profile["joined"] = saved.joined


# Save new display name for the user
def save_display_name(conn, user_id, name):
    conn.execute(
        update(users).where(users.c.id == user_id).values(display_name=name)
    )
