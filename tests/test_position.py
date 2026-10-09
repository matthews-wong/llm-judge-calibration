import json
import unittest

from judge_calibration.position import PairRequest, check_position_bias, parse_winner
from judge_calibration.verdict import VerdictError

PAIRS = [("p1", "q", "short", "a longer answer"), ("p2", "q", "tiny", "a much longer reply")]


class ContentJudge:
    """Always picks the longer answer, whatever the slot."""

    def complete(self, request: PairRequest) -> str:
        longer = "A" if len(request.answer_a) >= len(request.answer_b) else "B"
        return json.dumps({"winner": longer})


class SlotAJudge:
    def complete(self, request: PairRequest) -> str:
        return '{"winner": "A"}'


class PositionTest(unittest.TestCase):
    def test_content_judge_is_consistent(self) -> None:
        report = check_position_bias(ContentJudge(), PAIRS)
        self.assertEqual((report.consistency, report.inconsistent_ids), (1.0, ()))

    def test_slot_biased_judge_flips_every_pair(self) -> None:
        report = check_position_bias(SlotAJudge(), PAIRS)
        self.assertEqual(report.consistency, 0.0)
        self.assertEqual(report.inconsistent_ids, ("p1", "p2"))
        self.assertEqual(report.first_slot_wins, 4)

    def test_bad_reply_is_rejected_with_value(self) -> None:
        with self.assertRaisesRegex(VerdictError, "'C'"):
            parse_winner('{"winner": "C"}')

    def test_non_json_rejected(self) -> None:
        with self.assertRaises(VerdictError):
            parse_winner("A")

    def test_empty_pairs_rejected(self) -> None:
        with self.assertRaises(ValueError):
            check_position_bias(ContentJudge(), [])


if __name__ == "__main__":
    unittest.main()
