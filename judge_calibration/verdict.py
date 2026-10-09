"""Strict parsing of judge output.

Judge text is untrusted: it is parsed as JSON and checked against a fixed
shape, never evaluated and never searched for free-text "pass" substrings.
"""

import json
import re

PASS = "pass"
FAIL = "fail"
VALID_VERDICTS = (PASS, FAIL)

# Models often wrap JSON in a markdown fence even when told not to.
_FENCE = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", re.DOTALL)


class VerdictError(ValueError):
    """The judge output could not be turned into a verdict."""


def parse_verdict(raw: str) -> str:
    text = raw.strip()
    if not text:
        raise VerdictError("empty judge output")
    fenced = _FENCE.match(text)
    if fenced:
        text = fenced.group(1)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise VerdictError(f"judge output is not JSON ({exc.msg}): {raw[:80]!r}") from exc
    if not isinstance(data, dict):
        raise VerdictError(f"expected a JSON object, got {type(data).__name__}")
    verdict = data.get("verdict")
    if verdict not in VALID_VERDICTS:
        raise VerdictError(
            f"verdict must be one of {VALID_VERDICTS}, got {verdict!r}"
        )
    return verdict
