from datetime import date

from app.streak import current_streak, record_study_day


def test_record_study_day_adds_date():
    study_days = set()
    record_study_day(study_days, date(2026, 10, 29))
    assert study_days == {date(2026, 10, 29)}


def test_record_study_day_twice_same_day():
    study_days = set()
    record_study_day(study_days, date(2026, 10, 29))
    record_study_day(study_days, date(2026, 10, 29))
    assert len(study_days) == 1


def test_current_streak_empty():
    assert current_streak(set(), date(2026, 10, 29)) == 0


def test_current_streak_consecutive_days():
    days = {date(2026, 10, 27), date(2026, 10, 28), date(2026, 10, 29)}
    assert current_streak(days, date(2026, 10, 29)) == 3


def test_current_streak_gap_resets():
    days = {date(2026, 10, 25), date(2026, 10, 26), date(2026, 10, 27), date(2026, 10, 29)}
    assert current_streak(days, date(2026, 10, 29)) == 1


def test_current_streak_today_not_studied_yet():
    days = {date(2026, 10, 26), date(2026, 10, 27)}
    assert current_streak(days, date(2026, 10, 28)) == 2


def test_current_streak_missed_a_full_day():
    assert current_streak({date(2026, 10, 26)}, date(2026, 10, 29)) == 0
