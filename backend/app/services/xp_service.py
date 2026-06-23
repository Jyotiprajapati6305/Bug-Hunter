"""XP and leveling business logic.

Level formula
-------------
Levels 1-5 use fixed thresholds from the product spec:
    L1=0, L2=100, L3=300, L4=600, L5=1000

From level 5 onward we continue the same "progressively more per level"
pattern. The deltas between L1..L5 are 100, 200, 300, 400 (i.e. delta(n) =
100 * n for the step from level n to n+1). We continue that arithmetic
progression indefinitely:

    delta(n) = 100 * n          (XP required to go from level n to level n+1)
    threshold(1) = 0
    threshold(n+1) = threshold(n) + delta(n)

This yields: L1=0, L2=100, L3=300, L4=600, L5=1000, L6=1500, L7=2100,
L8=2800, L9=3600, L10=4500, ... matching the spec exactly for L1-L5 and
extending smoothly (triangular-number growth) beyond it.
"""

MAX_COMPUTED_LEVEL = 100


def _level_thresholds(max_level: int = MAX_COMPUTED_LEVEL) -> list[int]:
    """Return a list where index i (0-based) holds the XP threshold for level i+1."""
    thresholds = [0]  # level 1
    for n in range(1, max_level):
        delta = 100 * n
        thresholds.append(thresholds[-1] + delta)
    return thresholds


_THRESHOLDS = _level_thresholds()


def get_level_table() -> list[tuple[int, int]]:
    """Return [(level, xp_required), ...] for all computed levels."""
    return [(idx + 1, xp) for idx, xp in enumerate(_THRESHOLDS)]


def xp_required_for_level(level: int) -> int:
    if level < 1:
        return 0
    if level - 1 < len(_THRESHOLDS):
        return _THRESHOLDS[level - 1]
    # Extend on the fly for absurdly high levels rather than hard-failing.
    xp = _THRESHOLDS[-1]
    for n in range(len(_THRESHOLDS), level):
        xp += 100 * n
    return xp


def level_for_xp(xp_total: int) -> int:
    """Given a total XP amount, return the level it corresponds to."""
    level = 1
    for lvl, threshold in get_level_table():
        if xp_total >= threshold:
            level = lvl
        else:
            break
    # Handle XP beyond the precomputed table.
    if xp_total >= _THRESHOLDS[-1]:
        level = len(_THRESHOLDS)
        next_xp = _THRESHOLDS[-1]
        n = len(_THRESHOLDS)
        while True:
            next_xp += 100 * n
            if xp_total >= next_xp:
                level += 1
                n += 1
            else:
                break
    return level


SEVERITY_XP_MAP: dict[str, int] = {
    "critical": 100,
    "high": 70,
    "medium": 50,
    "low": 25,
}


def xp_for_bug(severity: str, is_duplicate: bool, status: str) -> int:
    """Compute XP award for a bug submission per the severity formula.

    Duplicate or rejected bugs always award 0 XP. Otherwise, XP is determined
    by severity: critical=100, high=70, medium=50, low=25.
    """
    if is_duplicate or status == "duplicate" or status == "rejected":
        return 0
    return SEVERITY_XP_MAP.get(severity, 0)
