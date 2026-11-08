"""Pure, deterministic progression logic. No network or filesystem I/O."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, timedelta
from math import sqrt

LEVELS = ((0, 'Hatchling'), (50, 'Juvenile'), (200, 'Subadult'), (500, 'Adult'), (1000, 'Apex Rex'))


@dataclass(frozen=True)
class RexState:
    login: str
    contributions: int
    commits: int | None
    stage: str
    level: int
    progress: float
    scale: float
    streak: int
    longest_streak: int
    yesterday: int
    behavior: str
    dominant_language: str
    language_color: str
    as_of: str

    def to_dict(self) -> dict:
        return asdict(self)


def validate_snapshot(data: dict) -> None:
    if not isinstance(data, dict) or not isinstance(data.get('login'), str) or not data['login'].strip():
        raise ValueError('Snapshot must have a nonempty login')
    if not isinstance(data.get('daily'), dict):
        raise ValueError('Snapshot must have a daily map')
    for day, amount in data['daily'].items():
        date.fromisoformat(day)
        if type(amount) is not int or amount < 0:
            raise ValueError(f'Invalid count for {day}: {amount!r}')
    if not isinstance(data.get('as_of'), str):
        raise ValueError('Snapshot missing as_of')
    date.fromisoformat(data['as_of'])


def streaks(daily: dict[str, int], as_of: str) -> tuple[int, int]:
    """Current streak ends on as_of, longest streak from all consecutive positive dates."""
    dates = sorted(date.fromisoformat(d) for d, c in daily.items() if c > 0 and d <= as_of)
    if not dates:
        return 0, 0
    seen = set(dates)
    last = date.fromisoformat(as_of)
    current = 0
    while last in seen:
        current += 1
        last -= timedelta(days=1)
    longest, run, previous = 0, 0, None
    for d in dates:
        run = run + 1 if previous and (d-previous).days == 1 else 1
        longest = max(longest, run)
        previous = d
    return current, longest


def derive(data: dict) -> RexState:
    validate_snapshot(data)
    as_of = data['as_of']
    daily = {d: v for d, v in data['daily'].items() if d <= as_of}
    count = sum(daily.values())
    level = max(i for i, (start, _) in enumerate(LEVELS) if count >= start)
    base, stage = LEVELS[level]
    next_threshold = LEVELS[level+1][0] if level + 1 < len(LEVELS) else None
    progress = min(1.0, (count - base) / (next_threshold - base)) if next_threshold else 1.0
    # Smooth growth: EVERY contribution changes size (up to the natural maximum).
    scale = min(1.0, 0.52 + 0.48 * sqrt(min(count, 1000) / 1000.0))
    current, longest = streaks(daily, as_of)
    recent = daily.get(as_of, 0)
    behavior = 'roar' if recent >= 5 else 'walk' if recent >= 1 else 'idle'
    langs = data.get('languages') or []
    language = langs[0] if langs else {'name': 'Unknown', 'color': '#c8a67a'}
    commits = data.get('commits')
    if commits is not None and (type(commits) is not int or commits < 0):
        raise ValueError('commits must be a nonnegative integer or null')
    return RexState(
        login=data['login'], contributions=count, commits=commits,
        stage=stage, level=level+1, progress=progress, scale=scale,
        streak=current, longest_streak=longest, yesterday=recent,
        behavior=behavior, dominant_language=str(language.get('name','Unknown')),
        language_color=str(language.get('color') or '#c8a67a'), as_of=as_of,
    )
