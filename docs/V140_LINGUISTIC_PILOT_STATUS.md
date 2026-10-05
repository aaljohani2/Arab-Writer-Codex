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

The pilot mixes correction cases, correct-source/no-change controls, adversarial/context cases, and fidelity/protected-value cases.

### A/B harness hardening

`evals/run_ab_codex.py` now includes four controls added after the first five-case local smoke exposed measurement weaknesses:

1. **Sentinel-based skill isolation**
   - known global/user Arab Writer copies are disabled by exact path for each Codex session;
   - the temporary candidate copy receives a unique one-run sentinel in its description;
   - `codex debug prompt-input` must show no Arab Writer in baseline and must show the sentinel in candidate;
   - path visibility is diagnostic only because Codex prompt rendering may omit local paths;
   - the repository skill itself is not modified.

2. **Stratified smoke sampling**
   - `--stratified-smoke` selects one deterministic case from each of ORT, MOR, SYN, AGR, NUM, PUN, and AMB;
   - this replaces `--limit 5` as the recommended smoke method because the first five sorted cases were all MOR.

3. **Controlled-run gate**
   - `--controlled` requires pinned `--model` and `--reasoning`;
   - requires a clean Git worktree;
   - rejects a skipped skill-isolation preflight;
   - records commit SHA, worktree-clean state, sampling mode, case IDs, Codex CLI version, and configured runtime values.

4. **Strict versus substantive scoring**
   - exact/minimality metrics remain strict;
   - substantive linguistic metrics ignore optional Arabic harakat only;
   - optional diacritics still count as a strict change on `PRESERVE` cases;
   - protected literals remain a separate fidelity signal.

### Structural validation

Tests include:
- `tests/test_v140_linguistic_pilot.py`
- `tests/test_v140_eval_harness.py`

They cover schema, unique IDs, family allocation, case-type mix, protected literals, multi-file loading, scorer behavior, sentinel injection/visibility, Windows path escaping, controlled-run requirements, and stratified smoke selection.

### Linguistic scorer v2

`evals/score_linguistic_pilot.py` reports:
- exact gold rate;
- substantive gold rate;
- substantive correction accuracy;
- exact correction accuracy;
- strict source preservation;
- substantive source preservation;
- strict and substantive false-change rates;
- optional-diacritic-only changes;
- protected-literal retention;
- family breakdown;
- candidate-minus-baseline deltas;
- mismatch classification.

The score schema is `arab-writer-linguistic-pilot-score-v2`.

## First local smoke: evidence and limitation

A five-case run on 2026-10-05 successfully demonstrated that:
- baseline did not expose the globally installed Arab Writer;
- candidate exposed Arab Writer;
- all ten model calls returned code 0.

However, the run is **not** accepted as the formal baseline because:
- model and reasoning were unpinned;
- candidate local-path visibility was false, so name-only visibility did not prove provenance;
- all five sampled cases were MOR;
- exact scoring treated optional tanwin additions as correction failures;
- the user's working tree contained unrelated prior fixture deletions.

Those weaknesses are the reason for the hardening above. The five-case result remains diagnostic evidence only.

## Required next smoke

Run from a clean checkout/worktree at a fixed commit:

```bash
python evals/run_ab_codex.py \
  --evals-glob 'evals/linguistic_core_pilot_*.jsonl' \
  --stratified-smoke \
  --controlled \
  --model <model-slug> \
  --reasoning medium
```

Required preconditions/evidence:
- `Skill isolation: VERIFIED (baseline clean; candidate sentinel-tagged local skill visible)`
- `git_worktree_clean: true`
- configured model is pinned
- configured reasoning is pinned
- seven cases covering ORT/MOR/SYN/AGR/NUM/PUN/AMB
- all model calls return 0

Then score:

```bash
python evals/score_linguistic_pilot.py \
  evals/results/ab_results.jsonl \
  --out evals/results/linguistic_score.json
```

If the stratified smoke is clean, run the full 64-case controlled baseline with the same model, reasoning, Codex CLI environment, and skill commit.

## Evidence boundary

Passing CI and a structurally valid 64-case corpus do **not** establish that v1.4 improves Arabic writing or grammar performance.

No formal baseline-vs-skill linguistic result is accepted yet. The first five-case smoke is intentionally excluded from the formal baseline for the reasons above.

Only after a reproducible 64-case baseline is captured should new linguistic knowledge packs be injected into the skill. This preserves a valid before-v1.4-knowledge comparison.

## Decision gate after baseline

Proceed to the first v1.4 knowledge implementation only after:
1. the controlled 64-case baseline is captured;
2. family-level weaknesses are identified;
3. strict over-editing and substantive correctness are reviewed separately;
4. non-exact substantive mismatches are adjudicated where necessary.

The first knowledge pack should target the highest-error families rather than implementing the entire taxonomy blindly.
