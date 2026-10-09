import contextlib
import io
import unittest

from judge_calibration.__main__ import main


class CliTest(unittest.TestCase):
    def test_prints_the_agreement_table_for_the_golden_set(self) -> None:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main([])
        self.assertEqual(code, 0)
        text = out.getvalue()
        self.assertIn("cases: 24", text)
        self.assertIn("kappa:", text)


if __name__ == "__main__":
    unittest.main()
