from app.progress import record_viewed


def test_record_viewed_first_card():
    progress = {}
    assert record_viewed(progress, "Bio", 0, 3) == 1
    assert progress == {"Bio": 1}


def test_record_viewed_never_goes_backward():
    progress = {"Bio": 3}
    assert record_viewed(progress, "Bio", 1, 3) == 3


def test_record_viewed_capped_at_deck_size():
    progress = {}
    assert record_viewed(progress, "Bio", 5, 3) == 3


def test_record_viewed_empty_deck():
    progress = {}
    assert record_viewed(progress, "Bio", 0, 0) == 0
