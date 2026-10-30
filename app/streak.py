from datetime import timedelta

# Pure streak helpers; `study_days` is the set of dates the user studied


# Record that the user studied on `today`
def record_study_day(study_days, today):
    study_days.add(today)


# Consecutive days studied, ending today (or yesterday if today has no study yet)
def current_streak(study_days, today):
    day = today if today in study_days else today - timedelta(days=1)
    streak = 0
    while day in study_days:
        streak += 1
        day -= timedelta(days=1)
    return streak
