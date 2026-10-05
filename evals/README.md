# A/B Evaluation

`run_ab_codex.py` runs each case twice using the actual Codex CLI:
1. baseline workspace with no Arab Writer skill;
2. candidate workspace containing `.agents/skills/arab-writer` and explicit `$arab-writer` invocation.

Prerequisites:
- authenticated `codex` CLI on PATH;
- network/model access available to that Codex installation.

## Existing internal suite

```bash
python evals/run_ab_codex.py --limit 10
```

For a controlled model comparison:

```bash
python evals/run_ab_codex.py --model gpt-5.6-sol --reasoning medium
```

## v1.4 Arabic linguistic-core pilot

The pilot cases are split by family under:

```text
evals/linguistic_core_pilot_*.jsonl
```

Run all current pilot files without creating a duplicated combined dataset:

```bash
python evals/run_ab_codex.py \
  --evals-glob 'evals/linguistic_core_pilot_*.jsonl'
```

Then score baseline and candidate separately:

```bash
python evals/score_linguistic_pilot.py \
  evals/results/ab_results.jsonl \
  --out evals/results/linguistic_score.json
```

The linguistic scorer reports:
- exact normalized gold match;
- correction accuracy on `CORRECT` cases;
- correct-source preservation on no-change / preserve cases;
- false-change rate;
- protected-literal retention;
- breakdown by linguistic family;
- candidate-minus-baseline deltas.

An exact mismatch is **not automatically evidence of a grammatical error**. It is an evaluation mismatch that may require blind human review, especially for ambiguous or stylistic cases.

## GitHub Actions

The manual `codex-ab-benchmark` workflow supports two suites:
- `internal`;
- `linguistic-pilot`.

The workflow requires the repository `OPENAI_API_KEY` secret and therefore is intentionally manual rather than a push-triggered model benchmark.

## Outputs

The harness writes:
- `evals/results/ab_results.jsonl`;
- `evals/results/human_review.csv`;
- `evals/results/run_metadata.json`.

For the linguistic pilot, the workflow also writes:
- `evals/results/linguistic_score.json`.

Keep human reviewers blind to which column is baseline/candidate when doing formal evaluation.
