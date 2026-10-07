# v1.4 Arabic Linguistic Core — Pilot Status

Status date: 2026-10-07  
Branch: `feature/v1.4-arabic-linguistic-core`

## Current phase

The project has moved from corpus construction and baseline capture into **measured linguistic knowledge development**.

The runtime skill is still labeled `v1.3.0`; the feature branch contains experimental v1.4 knowledge only. Do not merge or release it as v1.4 until the blind regression gates and the remaining family decisions are complete.

## Measurement assets

### Initial linguistic pilot

64 cases across ORT/MOR/SYN/AGR/NUM/PUN/AMB. This suite established the scorer, A/B harness, skill isolation, strict-vs-substantive metrics, and the first reproducible before-v1.4 baseline.

### Challenge Set v1

70 source-grounded hard cases:

| Family | Cases |
|---|---:|
| SYN | 20 |
| MOR | 15 |
| NUM | 10 |
| AMB | 10 |
| AGR | 5 |
| ORT | 5 |
| PUN | 5 |
| **Total** | **70** |

The set is balanced at 35 classical/heritage and 35 modern/contemporary cases. The second-pass linguistic review is documented in `docs/CHALLENGE_SET_V1_LINGUISTIC_REVIEW.md`.

## Controlled A/B safeguards

`evals/run_ab_codex.py` provides:

- exact-path disabling of global/user Arab Writer installations;
- temporary candidate sentinel injection;
- `codex debug prompt-input` skill-isolation preflight;
- `--controlled` clean-worktree and pinned-runtime gate;
- deterministic stratified smoke selection;
- `--blind-proofread`, which hides per-case task/rule/family/rationale/gold hints and sends one generic proofreading instruction plus the source text only;
- run metadata containing commit, prompt mode, configured model/reasoning, case IDs, Codex CLI version, and isolation evidence.

The scorer separates exact minimality from substantive matching that ignores optional Arabic harakat only.

## Blind Challenge baseline before v1.4 knowledge

Controlled pre-knowledge run:

- commit: `96519ed8fe29f76916a589a76037bcb6455c0110`
- skill version: `1.3.0`
- prompt mode: `blind-proofread-v1`
- configured model: `gpt-6.1-sol`
- reasoning: `medium`
- Codex CLI: `0.160.0`
- cases: 70
- model calls: 140
- worktree clean: yes
- skill isolation: verified
- protected failures: 0
- nonzero model return codes: 0

### Pre-knowledge result

| Metric | Baseline | Arab Writer v1.3 |
|---|---:|---:|
| Exact gold | 84.29% | 81.43% |
| Substantive gold | 94.29% | 90.00% |
| Correction accuracy | 92.86% | 87.50% |
| Exact source preservation | 92.86% | 100.00% |
| Substantive source preservation | 100.00% | 100.00% |
| Strict false-change rate | 7.14% | 0.00% |
| Protected retention | 100.00% | 100.00% |

Interpretation: v1.3 was **more conservative and better at preservation**, but that conservatism reduced blind discovery/correction of deterministic syntax/agreement defects.

Family signal before Phase 1:

- MOR: 100% substantive candidate
- NUM: 100%
- ORT: 100%
- AMB: 100%
- AGR: 80%
- SYN: 85%
- PUN: 40% exact/substantive under the deterministic gold scorer; punctuation remains human-adjudication sensitive.

Therefore Phase 1 targeted **syntax + agreement discovery**, not morphology, numbers, or orthography.

## Phase 1 implementation — syntax/agreement core

Added runtime reference:

- `.agents/skills/arab-writer/references/arabic-syntax.md`

It is wired through `SKILL.md` and `arabic-linguistic-verification.md` for correctness-heavy/proofread tasks.

The knowledge is rule-based and uses fresh examples. Evaluation case IDs, target sentences, gold answers, and case-specific rationales are forbidden from runtime references.

Primary rule anchors include:

- سيبويه — `الكتاب`
- ابن هشام — `مغني اللبيب`
- ابن عقيل — `شرح ابن عقيل`
- مصطفى الغلاييني — `جامع الدروس العربية`
- عباس حسن — `النحو الوافي`

## Phase 1 targeted smoke and Phase 1b refinement

The first ten-case blind smoke at commit `c5e7190da4645b05a141127605f2c1033362df79` was a partial failure: the candidate preserved all controls but missed or misdiagnosed two priority patterns.

Phase 1b therefore added two role-based decision procedures with fresh examples:

1. **Non-human plural local attachment**
   - direct adjective/predicate agreement → feminine singular in standard Arabic;
   - do not spread agreement into a separate clause/predicative relation;
   - use syntactic attachment, not nearest-noun attraction.

2. **Passive ditransitive promotion**
   - reconstruct active valency;
   - identify the promoted first object;
   - require nominative نائب الفاعل;
   - preserve the second object's/complement's own role;
   - prioritize visible dual/sound-plural endings as high-confidence evidence.

The repeated ten-case Phase 1b smoke at commit `7e5dcac8b1c08d4071d7e91dcf008a01f2d7c492` met the target gate:

- 5/5 substantive correction;
- 5/5 substantive preservation;
- 100% substantive gold;
- 0 substantive false changes;
- 0 protected failures;
- 0 nonzero return codes;
- skill isolation verified.

This justified running the full 70-case blind gate.

## Full 70-case Phase 1b blind gate

Controlled run at commit:

`7e5dcac8b1c08d4071d7e91dcf008a01f2d7c492`

Environment:

- skill version label: `1.3.0` (feature branch still pre-release)
- prompt mode: `blind-proofread-v1`
- configured model: `gpt-6.1-sol`
- configured reasoning: `medium`
- Codex CLI: `0.160.0`
- cases: 70
- model calls: 140
- worktree clean: yes
- skill isolation: verified
- protected failures: 0
- nonzero model return codes: 0

### Full Phase 1b result

| Metric | Baseline | Candidate |
|---|---:|---:|
| Exact gold | 84.29% | **85.71%** |
| Substantive gold | 92.86% | **94.29%** |
| Correction accuracy | 91.07% | **92.86%** |
| Exact correction accuracy | 82.14% | 82.14% |
| Exact source preservation | 92.86% | **100.00%** |
| Substantive source preservation | 100.00% | 100.00% |
| Strict false-change rate | 7.14% | **0.00%** |
| Substantive false-change rate | 0.00% | 0.00% |
| Protected retention | 100.00% | 100.00% |

### Family result

| Family | Baseline substantive | Candidate substantive |
|---|---:|---:|
| AGR | 80% | **100%** |
| AMB | 100% | 100% |
| MOR | 100% | 100% |
| NUM | 100% | 100% |
| ORT | 100% | 100% |
| PUN | 40% | 40% |
| SYN | 95% | 95% |

The candidate introduced **no substantive preservation regression** and retained all protected literals.

Relative to the pre-knowledge Arab Writer v1.3 blind snapshot, the Phase 1b candidate moved from:

- exact gold: 81.43% → 85.71%;
- substantive gold: 90.00% → 94.29%;
- correction accuracy: 87.50% → 92.86%;
- source preservation: stayed at 100% exact/substantive;
- protected retention: stayed at 100%.

These are single-run snapshots, not confidence intervals. Model stochasticity remains visible and must be considered before making product-quality claims.

## Important robustness observation

`CH-SYN-018` (passive ditransitive / نائب الفاعل) passed in the targeted Phase 1b smoke but failed in the full 70-case run. This means the rule is present and can be applied, but the behavior is not yet fully stable across independent model calls.

Do **not** copy or paraphrase that benchmark sentence into runtime knowledge. Track the pattern with fresh holdout examples if robustness work continues.

The syntax/agreement phase is therefore accepted as a **provisional positive gain**, not as perfect deterministic coverage.

## Punctuation decision boundary

PUN remains 40% for both baseline and candidate. Three scored mismatches are dominated by comma/semicolon/colon choices where more than one defensible editorial punctuation pattern may exist.

Therefore do **not** tune runtime knowledge to the existing five PUN gold strings. Before adding a punctuation knowledge pack:

1. separate deterministic punctuation errors from house-style/editorial variants;
2. create human-adjudication labels for acceptable alternatives;
3. build fresh holdout cases with clear semantic/syntactic consequences where possible;
4. use historical and modern Arabic punctuation references;
5. keep the existing Challenge Set unchanged as historical measurement evidence.

The punctuation plan is documented separately in `docs/V140_PUNCTUATION_ADJUDICATION_V1.md`.

## Next gate

Phase 1 syntax/agreement is frozen for now. Do not continue benchmark-specific syntax tuning from the existing 70 cases.

Next workstream:

1. build the punctuation adjudication protocol;
2. author a fresh punctuation holdout with deterministic vs stylistic labels;
3. only then decide whether `references/arabic-punctuation.md` should be wired into runtime;
4. keep MOR/NUM/ORT/AMB untouched while they remain at 100% substantive on the challenge set.

## Evidence boundary

CI proves structure and deterministic tests, not model-quality improvement. Blind model runs remain the quality gate.

Configured model/reasoning values are recorded as configured runtime only; observed runtime remains `unknown` unless independent runtime evidence is captured.
