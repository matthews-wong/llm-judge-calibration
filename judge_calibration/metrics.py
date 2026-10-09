"""Agreement metrics between judge verdicts and human labels."""

from collections import Counter
from collections.abc import Sequence


def _check_paired(human: Sequence[str], judge: Sequence[str]) -> None:
    if len(human) != len(judge):
        raise ValueError(
            f"label count mismatch: {len(human)} human vs {len(judge)} judge"
        )
    if not human:
        raise ValueError("cannot score an empty set of labels")


def accuracy(human: Sequence[str], judge: Sequence[str]) -> float:
    _check_paired(human, judge)
    return sum(h == j for h, j in zip(human, judge)) / len(human)


def cohen_kappa(human: Sequence[str], judge: Sequence[str]) -> float:
    """Agreement corrected for chance.

    Returns 1.0 when both sides use a single identical label: chance agreement
    is then 1 and the usual formula would divide by zero.
    """
    _check_paired(human, judge)
    total = len(human)
    observed = accuracy(human, judge)
    human_counts = Counter(human)
    judge_counts = Counter(judge)
    expected = sum(
        human_counts[label] * judge_counts[label] for label in human_counts
    ) / (total * total)
    if expected == 1.0:
        return 1.0
    return (observed - expected) / (1.0 - expected)


def confusion(
    human: Sequence[str], judge: Sequence[str]
) -> dict[tuple[str, str], int]:
    """Counts keyed by (human label, judge label)."""
    _check_paired(human, judge)
    return dict(Counter(zip(human, judge)))
