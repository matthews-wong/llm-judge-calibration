"""Print a calibration table: python3 -m judge_calibration [cases.jsonl]"""

import sys
from pathlib import Path

from .calibrate import calibrate, load_cases
from .judge import OverlapJudge

DEFAULT_CASES = Path(__file__).parent.parent / "data" / "golden.jsonl"


def main(argv: list[str]) -> int:
    path = Path(argv[0]) if argv else DEFAULT_CASES
    cases = load_cases(path)
    report = calibrate(OverlapJudge(), cases)
    print(f"cases: {report.total} ({path.name})  judge: OverlapJudge")
    print(f"unparseable: {len(report.unparseable)}")
    print(f"accuracy: {report.accuracy:.3f}")
    print(f"kappa:    {report.kappa:.3f}")
    print("confusion (human -> judge):")
    for (human, judge), count in sorted(report.confusion.items()):
        print(f"  {human:>4} -> {judge:<4} {count}")
    print("disagreements: " + (", ".join(report.disagreements) or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
