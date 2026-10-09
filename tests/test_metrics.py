import unittest

from judge_calibration.metrics import accuracy, cohen_kappa, confusion


class MetricsTest(unittest.TestCase):
    def test_accuracy(self) -> None:
        self.assertEqual(accuracy(["pass", "fail", "pass"], ["pass", "pass", "pass"]), 2 / 3)

    def test_kappa_perfect_agreement(self) -> None:
        labels = ["pass", "fail", "pass", "fail"]
        self.assertEqual(cohen_kappa(labels, labels), 1.0)

    def test_kappa_chance_level_is_zero(self) -> None:
        human = ["pass", "pass", "fail", "fail"]
        judge = ["pass", "fail", "pass", "fail"]
        self.assertAlmostEqual(cohen_kappa(human, judge), 0.0)

    def test_kappa_known_value(self) -> None:
        # 20 pass/fail items: po = 0.7, pe = 0.5 -> kappa = 0.4
        human = ["pass"] * 10 + ["fail"] * 10
        judge = ["pass"] * 7 + ["fail"] * 3 + ["pass"] * 3 + ["fail"] * 7
        self.assertAlmostEqual(cohen_kappa(human, judge), 0.4)

    def test_kappa_single_label_does_not_divide_by_zero(self) -> None:
        self.assertEqual(cohen_kappa(["pass"] * 3, ["pass"] * 3), 1.0)

    def test_confusion_counts(self) -> None:
        counts = confusion(["pass", "fail", "fail"], ["pass", "pass", "pass"])
        self.assertEqual(counts, {("pass", "pass"): 1, ("fail", "pass"): 2})

    def test_length_mismatch_names_both_sizes(self) -> None:
        with self.assertRaisesRegex(ValueError, "2 human vs 1 judge"):
            accuracy(["pass", "fail"], ["pass"])

    def test_empty_input_rejected(self) -> None:
        with self.assertRaises(ValueError):
            cohen_kappa([], [])


if __name__ == "__main__":
    unittest.main()
