"""Judge seam: every grading call goes through `Judge.complete`."""

import json
import re
from dataclasses import dataclass
from typing import Protocol

DEFAULT_OVERLAP_THRESHOLD = 0.6
_TOKEN = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class JudgeRequest:
    question: str
    reference: str
    answer: str


class Judge(Protocol):
    def complete(self, request: JudgeRequest) -> str:
        """Return the judge's raw text reply (expected to be a JSON verdict)."""


def _tokens(text: str) -> set[str]:
    return set(_TOKEN.findall(text.lower()))


class OverlapJudge:
    """Deterministic stand-in for a model: passes when the answer covers
    enough of the reference's tokens. It is deliberately naive, so the
    calibration report has real disagreements to show."""

    def __init__(self, threshold: float = DEFAULT_OVERLAP_THRESHOLD) -> None:
        self.threshold = threshold

    def complete(self, request: JudgeRequest) -> str:
        reference = _tokens(request.reference)
        covered = len(reference & _tokens(request.answer)) / len(reference) if reference else 0.0
        verdict = "pass" if covered >= self.threshold else "fail"
        return json.dumps({"verdict": verdict, "reason": f"covers {covered:.2f} of reference"})
