import re 
from datetime import timedelta
from functools import lru_cache
from fsrs import Scheduler

DEFAULTS = {
    "desired_retention": 0.9,
    "learning_steps": "1m 10m",
    "relearning_steps": "10m",
    "maximum_interval": 36500,
    "enable_fuzzing": True,
}
_UNITS = {"m": 60, "h": 3600, "d": 86400}

def parse_steps(text):
    steps = []
    for part in (text or "").split():
        match = re.fullmatch(r"(\d+)([mhd])", part.lower())
        if not match:
            raise ValueError(f"Bad step '{part}' (use e.g. 1m, 10m, 1h)")
        seconds = int(match[1]) * _UNITS[match[2]]
        if not 60 <= seconds < 86400:
            raise ValueError("Each step must be at least 1m and under 1 day")
        steps.append(timedelta(seconds=seconds))
    if steps != sorted(steps):
        raise ValueError("Steps must go from shortest to longest")
    return steps

def clean_settings(raw):
    out = {**DEFAULTS, **{k: raw[k] for k in DEFAULTS if k in raw}}
    out["desired_retention"] = float(out["desired_retention"])
    if not 0.7 <= out["desired_retention"] <= 0.97:
        raise ValueError("Retention must be between 70% and 97%")
    out["maximum_interval"] = int(out["maximum_interval"])
    if not 1 <= out["maximum_interval"] <= 36500:
        raise ValueError("Max interval must be 1 to 36500 days")
    parse_steps(out["learning_steps"]); parse_steps(out["relearning_steps"])
    out["enable_fuzzing"] = bool(out["enable_fuzzing"])
    return out

@lru_cache(maxsize=256)
def _build(retention, learning, relearning, max_interval, fuzz):
    return Scheduler(desired_retention=retention,
                     learning_steps=parse_steps(learning),
                     relearning_steps=parse_steps(relearning),
                     maximum_interval=max_interval, enable_fuzzing=fuzz)

def make_scheduler(settings=None):
    s = {**DEFAULTS, **(settings or {})}
    return _build(s["desired_retention"], s["learning_steps"], s["relearning_steps"], s["maximum_interval"], s["enable_fuzzing"])