# A/B Evaluation

`run_ab_codex.py` runs each case twice using the actual Codex CLI:
1. baseline workspace with no Arab Writer skill;
2. candidate workspace containing `.agents/skills/arab-writer` and explicit `$arab-writer` invocation.

Prerequisites:
- authenticated `codex` CLI on PATH;
- network/model access available to that Codex installation.

## Skill isolation

The harness now protects the baseline from a user/global `arab-writer` installation.

Before any model call it:
1. looks for `arab-writer/SKILL.md` in known user roots such as `~/.agents/skills` and `~/.codex/skills` (plus `$CODEX_HOME/skills` when set);
2. disables those exact paths with a session-level Codex `skills.config` override;
3. renders `codex debug prompt-input` for a temporary baseline and candidate workspace;
4. fails closed if the baseline still sees `arab-writer` or the candidate cannot see its repository-local copy.

The rendered prompt is used only for the visibility check and is not written to the evaluation artifacts. Isolation evidence is recorded in `run_metadata.json`.

If Arab Writer is installed from a nonstandard user/plugin path and the baseline preflight reports that it is still visible, pass the exact skill directory or `SKILL.md` explicitly:

```bash
python evals/run_ab_codex.py \
  --global-skill-path "/absolute/path/to/arab-writer/SKILL.md" \
  --limit 5
```

`--global-skill-path` may be repeated. The emergency option `--skip-skill-isolation-preflight` exists for diagnostics only and should not be used for a controlled A/B result.

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

Start with a five-case smoke run on a computer where Codex is already authenticated:

```bash
python evals/run_ab_codex.py \
  --evals-glob 'evals/linguistic_core_pilot_*.jsonl' \
  --limit 5
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
