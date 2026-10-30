from datetime import date

from app.streak import record_study_day


def test_record_study_day_adds_date():
    study_days = set()
    record_study_day(study_days, date(2026, 10, 29))
    assert study_days == {date(2026, 10, 29)}


def test_record_study_day_twice_same_day():
    study_days = set()
    record_study_day(study_days, date(2026, 10, 29))
    record_study_day(study_days, date(2026, 10, 29))
    assert len(study_days) == 1
