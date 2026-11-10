from collections.abc import MutableMapping, MutableSet


# Each logged-in user gets their own copy of this data
def _current_key():
    from app.auth import session
    storage = session()
    return storage.get("user_id") if storage is not None else None


class PerUserDict(MutableMapping):
    def __init__(self, default=dict):
        self._default = default
        self._by_user = {}

    def _data(self):
        key = _current_key()
        if key not in self._by_user:
            self._by_user[key] = self._default()
        return self._by_user[key]

    def __getitem__(self, name):
        return self._data()[name]

    def __setitem__(self, name, value):
        self._data()[name] = value

    def __delitem__(self, name):
        del self._data()[name]

    def __iter__(self):
        return iter(self._data())

    def __len__(self):
        return len(self._data())

    def __repr__(self):
        return repr(self._data())


class PerUserSet(MutableSet):
    def __init__(self):
        self._by_user = {}

    def _data(self):
        return self._by_user.setdefault(_current_key(), set())

    def __contains__(self, item):
        return item in self._data()

    def __iter__(self):
        return iter(self._data())

    def __len__(self):
        return len(self._data())

    def add(self, item):
        self._data().add(item)

    def discard(self, item):
        self._data().discard(item)

    def update(self, items):
        self._data().update(items)

    def __repr__(self):
        return repr(self._data())


# Deck storage: {deck_name: [{"question": str, "answer": str}, ...]}
decks = PerUserDict()

# Furthest progress per deck: {deck_name: number of cards reached}
progress = PerUserDict()

# Dates the user studied at least one card: {datetime.date, ...}
study_days = PerUserSet()

# Current user's profile: display name and the date it was created
profile = PerUserDict(default=lambda: {"name": "", "joined": None})
