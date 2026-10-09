import unittest
from pathlib import Path

from judge_calibration.calibrate import Case, calibrate, load_cases
from judge_calibration.judge import JudgeRequest, OverlapJudge

GOLDEN = Path(__file__).parent.parent / "data" / "golden.jsonl"


class StubJudge:
    def __init__(self, replies: list[str]) -> None:
        self._replies = iter(replies)

    def complete(self, request: JudgeRequest) -> str:
        return next(self._replies)


def _case(case_id: str, human: str) -> Case:
    return Case(case_id, "q", "ref", "ans", human)


class CalibrateTest(unittest.TestCase):
    def test_golden_set_loads_with_valid_labels(self) -> None:
        cases = load_cases(GOLDEN)
        self.assertGreaterEqual(len(cases), 20)
        self.assertEqual({c.human for c in cases}, {"pass", "fail"})
        self.assertEqual(len({c.id for c in cases}), len(cases))

    def test_perfect_judge(self) -> None:
        judge = StubJudge(['{"verdict": "pass"}', '{"verdict": "fail"}'])
        report = calibrate(judge, [_case("a", "pass"), _case("b", "fail")])
        self.assertEqual((report.accuracy, report.kappa, report.disagreements), (1.0, 1.0, ()))

    def test_unparseable_reply_is_excluded_and_reported(self) -> None:
        judge = StubJudge(["I think it passes", '{"verdict": "pass"}'])
        report = calibrate(judge, [_case("a", "pass"), _case("b", "pass")])
        self.assertEqual(report.unparseable, ("a",))
        self.assertEqual(report.total, 2)
        self.assertEqual(report.accuracy, 1.0)

    def test_disagreements_name_the_case(self) -> None:
        judge = StubJudge(['{"verdict": "pass"}', '{"verdict": "pass"}'])
        report = calibrate(judge, [_case("a", "pass"), _case("b", "fail")])
        self.assertEqual(report.disagreements, ("b",))

    def test_malformed_case_line_reports_file_and_line(self) -> None:
        bad = Path(__file__).parent / "_bad.jsonl"
        bad.write_text('{"id": "x"}\n')
        self.addCleanup(bad.unlink)
        with self.assertRaisesRegex(ValueError, r"_bad\.jsonl:1"):
            load_cases(bad)

    def test_overlap_judge_on_golden_set_is_imperfect_but_better_than_chance(self) -> None:
        report = calibrate(OverlapJudge(), load_cases(GOLDEN))
        self.assertTrue(0.0 < report.kappa < 1.0)


if __name__ == "__main__":
    unittest.main()
