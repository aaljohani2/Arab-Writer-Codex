# v1.4 Arabic Linguistic Core — Pilot Status

Status date: 2026-10-06  
Branch: `feature/v1.4-arabic-linguistic-core`

## Current phase

The project has moved past corpus construction and baseline capture into **Phase 1 linguistic knowledge refinement**.

The current runtime skill is still labeled `v1.3.0`; the feature branch contains experimental v1.4 knowledge only. Do not merge or release it as v1.4 until the blind regression gates pass.

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

`evals/run_ab_codex.py` now provides:

- exact-path disabling of global/user Arab Writer installations;
- temporary candidate sentinel injection;
- `codex debug prompt-input` skill-isolation preflight;
- `--controlled` clean-worktree and pinned-runtime gate;
- deterministic stratified smoke selection;
- `--blind-proofread`, which hides per-case task/rule/family/rationale/gold hints and sends one generic proofreading instruction plus the source text only;
- run metadata containing commit, prompt mode, configured model/reasoning, case IDs, Codex CLI version, and isolation evidence.

The scorer separates exact minimality from substantive matching that ignores optional Arabic harakat only.

## Blind Challenge baseline before v1.4 knowledge

Controlled run:

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

### Blind result

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

Therefore Phase 1 targets **syntax + agreement discovery**, not morphology, numbers, or orthography.

## Phase 1 implementation

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

## Phase 1 targeted blind smoke

Controlled ten-case smoke at commit:

`c5e7190da4645b05a141127605f2c1033362df79`

The sample contained five target correction cases and five preservation/heritage controls.

### Result

| Metric | Baseline | Candidate |
|---|---:|---:|
| Substantive gold | 90% | 80% |
| Correction accuracy | 80% | 60% |
| Exact source preservation | 80% | 100% |
| Substantive source preservation | 100% | 100% |
| Strict false-change rate | 20% | 0% |

The smoke shows a **partial success, not a pass**.

Three previously weak syntax targets were corrected by the candidate in this smoke:

- `CH-SYN-003`
- `CH-SYN-011`
- `CH-SYN-012`

All five preservation controls remained substantively correct, and the candidate made no preservation edits.

Two target failures remain:

- `CH-AGR-001` — the candidate changed the defective human-plural form to masculine singular instead of the required feminine-singular agreement for the directly predicated non-human plural; the later impersonal/predicative material must not attract agreement from the earlier noun.
- `CH-SYN-018` — the candidate still failed to promote the first object of a passive ditransitive verb to nominative نائب الفاعل.

No protected failures or nonzero model return codes occurred.

## Phase 1b refinement

The syntax core now adds two explicit role-based decision procedures, using fresh examples rather than benchmark text:

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

The verification layer and SKILL routing repeat these checks so that minimality cannot become passive under-correction.

## Next gate

Do **not** run the full 70-case blind suite yet.

First rerun the same 10-case targeted blind smoke from a clean worktree at the current Phase 1b commit, with the same configured model/reasoning and Codex CLI environment.

Pass criteria:

1. candidate corrects all five target correction cases substantively;
2. candidate preserves all five control cases substantively;
3. no protected failure;
4. no nonzero model return code;
5. skill isolation verified;
6. no benchmark sentence/ID is present in runtime knowledge.

If Phase 1b passes, run the full 70-case blind A/B. Only then decide whether syntax/agreement is ready and whether a second knowledge family should be added.

## Evidence boundary

CI proves structure and deterministic tests, not model-quality improvement. The blind model run remains the quality gate.

A configured model slug is recorded as configured runtime only; observed runtime remains unknown unless independent runtime evidence is captured.
