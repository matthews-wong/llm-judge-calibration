# llm-judge-calibration

An LLM used as a grader is only useful if it agrees with people. This repo
measures that: run a judge over a set of human-labelled answers, then report
accuracy, Cohen's kappa and a confusion matrix. Pairwise judges also get a
position-bias check (does the verdict flip when the two answers swap places?).

Everything runs offline. The judge sits behind a one-method interface, and a
deterministic fake judge ships with the repo, so no API key is needed.

Python 3.12, standard library only.

## Layout

- `judge_calibration/judge.py` - the `Judge` interface and a deterministic `OverlapJudge`
- `judge_calibration/verdict.py` - strict parsing of judge output
- `judge_calibration/metrics.py` - accuracy, kappa, confusion matrix
- `judge_calibration/calibrate.py` - run a judge over labelled cases
- `judge_calibration/position.py` - swap-order check for pairwise judges
- `data/golden.jsonl` - 24 human-labelled answers (`pass` / `fail`)
- `tests/` - `python3 -m unittest`

## Run the tests

```sh
python3 -m unittest
```

## Run a calibration

```sh
python3 -m judge_calibration [cases.jsonl]
```

Result of the bundled `OverlapJudge` on the 24-case `data/golden.jsonl`
fixture (a fixture result, not a benchmark):

```
accuracy: 0.542
kappa:    0.057
```

A word-overlap judge is close to chance here: it passes confident wrong
answers that reuse the reference's words and fails correct paraphrases.
Plug a real model in by implementing `Judge.complete` and pass it to
`calibrate`; kappa near 0 means the judge tells you nothing the label
distribution did not, whatever the raw accuracy looks like.

## Design notes

- Judge replies are untrusted. `parse_verdict` accepts only a JSON object with
  `verdict` of `pass` or `fail`; prose and injected instructions are never
  interpreted.
- Replies that fail to parse are left out of the metrics and reported as
  `unparseable`, so a flaky judge is visible instead of counted as a fail.
- Kappa is reported next to accuracy because accuracy alone rewards a judge
  that always says the majority label.
