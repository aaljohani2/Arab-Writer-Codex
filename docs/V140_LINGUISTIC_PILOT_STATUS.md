# v1.4 Arabic Linguistic Core — Pilot Status

Status date: 2026-10-05  
Branch: `feature/v1.4-arabic-linguistic-core`

## Implemented

### Engineering specification
- `docs/ARABIC_ERROR_TAXONOMY_V1.md`
- Families: ORT, MOR, SYN, AGR, NUM, PUN, AMB, STY.
- Explicit separation among defects, contextual defects, editorial opportunities, and ambiguous cases.
- Confidence, severity, and default-action dimensions defined.

### Initial authored pilot
Current pilot: **64 cases** across four JSONL files.

| Family | Cases |
|---|---:|
| SYN | 20 |
| ORT | 10 |
| MOR | 10 |
| AGR | 8 |
| NUM | 8 |
| PUN | 4 |
| AMB | 4 |
| **Total** | **64** |

The pilot intentionally mixes:
- correction cases;
- correct-source/no-change controls;
- adversarial/context cases;
- fidelity/protected-value cases.

### Structural validation
Added:
- `tests/test_v140_linguistic_pilot.py`
- `tests/test_v140_eval_harness.py`

The tests validate schema, unique IDs, family allocation, case-type mix, no-change behavior, protected literals, guard cases, multi-file loading, scorer behavior, and path-scoped global-skill isolation helpers.

### A/B harness
`evals/run_ab_codex.py` supports:

```bash
--evals-glob 'evals/linguistic_core_pilot_*.jsonl'
```

This avoids maintaining a duplicated combined dataset.

It also implements controlled skill isolation so a globally installed `arab-writer` does not contaminate the baseline:
- auto-detect known user/global copies under `~/.agents/skills`, `~/.codex/skills`, and `$CODEX_HOME/skills` when present;
- disable exact global `SKILL.md` paths via a session-level Codex `skills.config` override;
- render `codex debug prompt-input` before any model call;
- fail closed if baseline still sees `arab-writer`;
- require the candidate workspace to see its repository-local copy;
- record isolation evidence in `run_metadata.json` without persisting the rendered prompt.

Nonstandard global/plugin paths can be supplied explicitly with repeatable `--global-skill-path` arguments.

### Linguistic scorer
Added `evals/score_linguistic_pilot.py` reporting separately for baseline and candidate:
- exact normalized gold rate;
- correction accuracy;
- correct-source preservation;
- false-change rate;
- protected-literal retention;
- family breakdown;
- candidate-minus-baseline deltas.

A non-exact output is treated as an evaluation mismatch, not automatic proof of grammatical error.

### GitHub Actions
The manual `codex-ab-benchmark` workflow supports:
- `internal` suite;
- `linguistic-pilot` suite.

The linguistic suite is scored automatically after the A/B run and uploaded with the artifacts.

The ordinary validation workflow remains push-triggered and does **not** invoke paid model benchmarking.

## CI state

Latest validation on this branch passed all structural steps, including:
- readiness preflight;
- skill/plugin validation;
- Python compilation;
- deterministic regression tests;
- v1.4 isolation-helper tests;
- benchmark-matrix validation;
- structural release gate;
- fidelity smoke test;
- package build/verification.

## Evidence boundary

The 64-case corpus and passing CI establish that the pilot dataset and evaluation harness are structurally valid. They do **not** establish that v1.4 improves Arabic writing or grammar performance.

No completed baseline-vs-skill linguistic A/B result is recorded yet for this branch.

A one-time GitHub benchmark attempt was intentionally prevented before model execution because the repository did not have an `OPENAI_API_KEY` secret. No model benchmark evidence was produced by that failed credential preflight.

## Recommended local baseline run

On a computer where Codex CLI is already authenticated, first run only five cases:

```bash
python evals/run_ab_codex.py \
  --evals-glob 'evals/linguistic_core_pilot_*.jsonl' \
  --limit 5
```

The harness must report:

```text
Skill isolation: VERIFIED (baseline clean; candidate skill visible)
```

Then score the smoke run:

```bash
python evals/score_linguistic_pilot.py \
  evals/results/ab_results.jsonl \
  --out evals/results/linguistic_score.json
```

If the five-case smoke run is clean, repeat without `--limit` for all 64 cases.

## Next empirical gate

Capture a controlled baseline-vs-skill result using either:
- the local authenticated Codex CLI with the isolation preflight; or
- the manual `codex-ab-benchmark` workflow after adding the repository `OPENAI_API_KEY` secret.

For formal comparison, pin model and reasoning effort when possible. After results are produced, inspect:
1. correction-accuracy delta;
2. correct-source-preservation delta;
3. false-change delta;
4. protected-literal failures;
5. family-level regressions;
6. non-exact cases requiring blind human adjudication.

Only after this baseline measurement should the new linguistic reference files be injected into the skill. This preserves a clean **before-v1.4-knowledge** baseline against which the linguistic layer can be measured.

## Decision gate after baseline

Proceed to the first v1.4 knowledge implementation only if the baseline results are captured and reviewable. The first knowledge pack should target the highest-error families rather than blindly implementing the entire taxonomy at once.
