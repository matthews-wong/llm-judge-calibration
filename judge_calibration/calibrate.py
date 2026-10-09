"""Run a judge over human-labelled cases and score the agreement."""

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from .judge import Judge, JudgeRequest
from .metrics import accuracy, cohen_kappa, confusion
from .verdict import VerdictError, parse_verdict


@dataclass(frozen=True)
class Case:
    id: str
    question: str
    reference: str
    answer: str
    human: str


@dataclass(frozen=True)
class Report:
    total: int
    unparseable: tuple[str, ...]
    accuracy: float
    kappa: float
    confusion: dict[tuple[str, str], int]
    disagreements: tuple[str, ...]


def load_cases(path: Path) -> list[Case]:
    cases = []
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            cases.append(Case(**json.loads(line)))
        except (json.JSONDecodeError, TypeError) as exc:
            raise ValueError(f"{path}:{number}: bad case ({exc})") from exc
    return cases


def calibrate(judge: Judge, cases: Iterable[Case]) -> Report:
    """Cases whose judge reply cannot be parsed are excluded from the
    agreement metrics and listed in `unparseable`, so a flaky judge shows up
    as a count instead of silently counting as a fail."""
    human: list[str] = []
    verdicts: list[str] = []
    unparseable: list[str] = []
    disagreements: list[str] = []
    for case in cases:
        reply = judge.complete(JudgeRequest(case.question, case.reference, case.answer))
        try:
            verdict = parse_verdict(reply)
        except VerdictError:
            unparseable.append(case.id)
            continue
        human.append(case.human)
        verdicts.append(verdict)
        if verdict != case.human:
            disagreements.append(case.id)
    return Report(
        total=len(human) + len(unparseable),
        unparseable=tuple(unparseable),
        accuracy=accuracy(human, verdicts),
        kappa=cohen_kappa(human, verdicts),
        confusion=confusion(human, verdicts),
        disagreements=tuple(disagreements),
    )
