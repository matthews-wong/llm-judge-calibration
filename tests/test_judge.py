import json
import unittest

from judge_calibration.judge import JudgeRequest, OverlapJudge


def _verdict(judge: OverlapJudge, reference: str, answer: str) -> str:
    reply = judge.complete(JudgeRequest("q", reference, answer))
    return json.loads(reply)["verdict"]


class OverlapJudgeTest(unittest.TestCase):
    def test_matching_answer_passes(self) -> None:
        self.assertEqual(_verdict(OverlapJudge(), "Paris is the capital", "The capital is Paris"), "pass")

    def test_unrelated_answer_fails(self) -> None:
        self.assertEqual(_verdict(OverlapJudge(), "Paris is the capital", "Bananas are yellow"), "fail")

    def test_empty_reference_fails_instead_of_dividing_by_zero(self) -> None:
        self.assertEqual(_verdict(OverlapJudge(), "", "anything"), "fail")

    def test_is_deterministic(self) -> None:
        request = JudgeRequest("q", "a b c", "a b")
        judge = OverlapJudge()
        self.assertEqual(judge.complete(request), judge.complete(request))


if __name__ == "__main__":
    unittest.main()
