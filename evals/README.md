# A/B Evaluation

`run_ab_codex.py` runs each case twice using the actual Codex CLI:
1. baseline workspace with no Arab Writer skill;
2. candidate workspace containing `.agents/skills/arab-writer` and explicit `$arab-writer` invocation.

Prerequisites:
- authenticated `codex` CLI on PATH;
- network/model access available to that Codex installation.

## Skill isolation

The harness protects the baseline from a user/global `arab-writer` installation.

Before any model call it:
1. looks for `arab-writer/SKILL.md` in known user roots such as `~/.agents/skills` and `~/.codex/skills` (plus `$CODEX_HOME/skills` when set);
2. disables those exact paths with a session-level Codex `skills.config` override;
3. copies the repository skill into a temporary candidate workspace and injects a one-run sentinel into that temporary copy's description;
4. renders `codex debug prompt-input` for a temporary baseline and candidate workspace;
5. fails closed unless the baseline sees neither Arab Writer nor the sentinel and the candidate sees the sentinel-tagged temporary local copy.

The repository skill itself is never modified by the sentinel. The rendered prompt is used only for verification and is not written to evaluation artifacts. Isolation evidence is recorded in `run_metadata.json`.

If Arab Writer is installed from a nonstandard user/plugin path and baseline preflight still sees it, pass the exact skill directory or `SKILL.md` explicitly:

```bash
python evals/run_ab_codex.py \
  --global-skill-path "/absolute/path/to/arab-writer/SKILL.md" \
  --limit 5
```

`--global-skill-path` may be repeated. `--skip-skill-isolation-preflight` is diagnostic only and is rejected by `--controlled`.

## Reproducible controlled runs

Use `--controlled` for formal before/after comparisons. It fails closed unless:
- `--model` is supplied;
- `--reasoning` is supplied;
- the Git worktree is clean;
- skill-isolation preflight is enabled.

Example:

```bash
python evals/run_ab_codex.py \
  --evals-glob 'evals/linguistic_core_pilot_*.jsonl' \
  --controlled \
  --model <model-slug> \
  --reasoning medium
```

`run_metadata.json` records the commit SHA, whether the worktree was clean, configured model/reasoning, case IDs, sampling mode, Codex CLI version, and isolation evidence.

The harness still labels the *observed* runtime model/reasoning as unknown unless separate runtime evidence is captured. A configured model slug is not treated as observed runtime proof.

## Existing internal suite

```bash
python evals/run_ab_codex.py --limit 10
```

## v1.4 Arabic linguistic-core pilot

The pilot cases are split by family under:

```text
evals/linguistic_core_pilot_*.jsonl
```

### Stratified smoke test

Do not use `--limit 5` as the main smoke test because sorted files can make that sample come from one family only.

Use:

```bash
python evals/run_ab_codex.py \
  --evals-glob 'evals/linguistic_core_pilot_*.jsonl' \
  --stratified-smoke \
  --controlled \
  --model <model-slug> \
  --reasoning medium
```

This deterministically selects one case from each current pilot family:

```text
ORT, MOR, SYN, AGR, NUM, PUN, AMB
```

After the smoke run succeeds, repeat without `--stratified-smoke` to run all 64 cases.

### Scoring

```bash
python evals/score_linguistic_pilot.py \
  evals/results/ab_results.jsonl \
  --out evals/results/linguistic_score.json
```

The v2 linguistic scorer deliberately separates strict minimality from substantive linguistic correctness.

Strict metrics:
- exact normalized gold rate;
- exact correction accuracy;
- exact source preservation;
- false-change rate.

Substantive metrics:
- substantive gold rate;
- correction accuracy after ignoring optional Arabic harakat only;
- substantive source preservation;
- substantive false-change rate.

It also reports:
- optional-diacritic-only changes;
- protected-literal retention;
- family breakdown;
- candidate-minus-baseline deltas;
- mismatch classification.

Optional harakat are not ignored for strict preservation. Therefore changing `يوميا` to `يوميًا` on a `PRESERVE` case still counts as an over-edit, while the substantive metric records that no lexical/syntactic content changed.

A substantive mismatch is **not automatically evidence of a grammatical error**. It may still require blind human adjudication where more than one correct formulation exists.

## GitHub Actions

The manual `codex-ab-benchmark` workflow supports:
- `internal`;
- `linguistic-pilot`.

The workflow requires the repository `OPENAI_API_KEY` secret and is intentionally manual rather than a push-triggered paid model benchmark.

## Outputs

The harness writes:
- `evals/results/ab_results.jsonl`;
- `evals/results/human_review.csv`;
- `evals/results/run_metadata.json`.

For the linguistic pilot, scoring writes:
- `evals/results/linguistic_score.json`.

Keep human reviewers blind to which column is baseline/candidate when doing formal evaluation.
