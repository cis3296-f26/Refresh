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


# Longest run of consecutive days ever studied
def longest_streak(study_days):
    longest = 0
    for day in study_days:
        if day - timedelta(days=1) not in study_days:  # first day of a run
            length = 1
            while day + timedelta(days=length) in study_days:
                length += 1
            longest = max(longest, length)
    return longest
