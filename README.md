# llm-judge-calibration

An LLM used as a grader is only useful if it agrees with people. This repo
measures that: run a judge over a set of human-labelled answers, then report
accuracy, Cohen's kappa and a confusion matrix. Pairwise judges also get a
position-bias check (does the verdict flip when the two answers swap places?).

Everything runs offline. The judge sits behind a one-method interface, and a
deterministic fake judge ships with the repo, so no API key is needed.

Python 3.12, standard library only.

## Layout

- `judge_calibration/verdict.py` - strict parsing of judge output
- `judge_calibration/metrics.py` - accuracy, kappa, confusion matrix
- `tests/` - `python3 -m unittest`

## Run the tests

```sh
python3 -m unittest
```
