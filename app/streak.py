# Pure streak helpers; `study_days` is the set of dates the user studied


# Record that the user studied on `today`
def record_study_day(study_days, today):
    study_days.add(today)
