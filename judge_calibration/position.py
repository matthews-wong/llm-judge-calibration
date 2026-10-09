"""Position-bias check for pairwise judges.

Each pair is judged twice, once per ordering. A judge that follows content
picks the same answer both times; one that favours a slot flips.
"""

import json
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

from .verdict import VerdictError

SLOTS = ("A", "B")


@dataclass(frozen=True)
class PairRequest:
    question: str
    answer_a: str
    answer_b: str


class PairJudge(Protocol):
    def complete(self, request: PairRequest) -> str:
        """Return raw text expected to be JSON like {"winner": "A"}."""


@dataclass(frozen=True)
class PositionReport:
    pairs: int
    consistent: int
    first_slot_wins: int
    inconsistent_ids: tuple[str, ...]

    @property
    def consistency(self) -> float:
        return self.consistent / self.pairs


def parse_winner(raw: str) -> str:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise VerdictError(f"pair reply is not JSON ({exc.msg}): {raw[:80]!r}") from exc
    winner = data.get("winner") if isinstance(data, dict) else None
    if winner not in SLOTS:
        raise VerdictError(f"winner must be one of {SLOTS}, got {winner!r}")
    return winner


def check_position_bias(
    judge: PairJudge, pairs: Iterable[tuple[str, str, str, str]]
) -> PositionReport:
    """`pairs` yields (id, question, answer_1, answer_2)."""
    total = consistent = first_slot = 0
    inconsistent: list[str] = []
    for pair_id, question, one, two in pairs:
        forward = parse_winner(judge.complete(PairRequest(question, one, two)))
        backward = parse_winner(judge.complete(PairRequest(question, two, one)))
        total += 1
        first_slot += (forward == "A") + (backward == "A")
        # Same answer must win in both orderings: A then B (or B then A).
        if forward != backward:
            consistent += 1
        else:
            inconsistent.append(pair_id)
    if total == 0:
        raise ValueError("no pairs to check")
    return PositionReport(total, consistent, first_slot, tuple(inconsistent))
