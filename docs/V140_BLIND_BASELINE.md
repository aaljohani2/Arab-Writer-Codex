# v1.4 Blind Challenge Baseline

Status: **ACCEPTED FOR DEVELOPMENT TARGETING**  
Branch: `feature/v1.4-arabic-linguistic-core`  
Run commit: `96519ed8fe29f76916a589a76037bcb6455c0110`  
Prompt mode: `blind-proofread-v1`

## Controlled run

The blind challenge run used:

- 70 source-grounded challenge cases;
- 70 baseline calls + 70 Arab Writer v1.3 candidate calls;
- clean Git worktree;
- verified temporary-sentinel skill isolation;
- configured model `gpt-6.1-sol`;
- configured reasoning `medium`;
- Codex CLI `0.160.0`;
- no protected-literal failures;
- no non-zero model-call return codes.

Observed runtime model/reasoning remained unavailable from the CLI harness, so the run records the configured values rather than claiming separately observed runtime identity.

## Blind results

| Metric | Baseline | Arab Writer v1.3 | Candidate delta |
|---|---:|---:|---:|
| Exact gold | 84.29% | 81.43% | -2.86 pp |
| Substantive gold | 94.29% | 90.00% | -4.29 pp |
| Correction accuracy | 92.86% | 87.50% | -5.36 pp |
| Exact correction accuracy | 82.14% | 76.79% | -5.35 pp |
| Exact source preservation | 92.86% | 100.00% | +7.14 pp |
| Substantive source preservation | 100.00% | 100.00% | 0.00 pp |
| False-change rate | 7.14% | 0.00% | -7.14 pp |
| Protected-literal retention | 100.00% | 100.00% | 0.00 pp |

## Interpretation

The blind run exposes a real v1.3 trade-off:

- the skill is **better at restraint and preservation**;
- the skill is **worse at discovering some genuine corrections without a rule-specific hint**.

That is the development target for v1.4: improve rule discovery and adjudication **without giving back the preservation gain**.

The strongest current deficits are in syntax/agreement rather than morphology, number grammar, or orthography.

### Family signal

| Family | Baseline substantive | Candidate substantive | Development signal |
|---|---:|---:|---|
| AGR | 100% | 80% | priority |
| SYN | 95% | 85% | priority |
| MOR | 100% | 100% | hold |
| NUM | 100% | 100% | hold |
| ORT | 100% | 100% | hold |
| AMB | 100% | 100% | preserve behavior |
| PUN | 40% | 40% | adjudication-heavy; do not overfit |

## Candidate-specific substantive misses to target

The blind candidate underperformed the baseline on these rule families:

- agreement with a non-human plural predicate;
- the syntactic role after `إلا` in an emptied/negative construction;
- case/role of `غير` inside a governed predicate structure;
- relative reference to a non-human plural;
- passive ditransitive structures where the first object becomes deputy subject.

The runtime knowledge layer must learn the **rule families**, not memorize challenge sentences or IDs.

## Leakage rule

Challenge files are evaluation-only. Runtime references must not copy:

- challenge IDs;
- challenge source sentences;
- challenge gold answers;
- challenge-specific rationales.

Knowledge references may encode the underlying Arabic rule using independent examples and canonical grammatical sources.

## Punctuation

`PUN` remains a separate editorial-adjudication problem. Exact mismatch is not automatically a linguistic failure when an alternative punctuation scheme is coherent and preserves clause relations. Do not tune v1.4 syntax rules to force one punctuation house style.

## Next development step

Phase 1 of the v1.4 Arabic Linguistic Core should target **syntax + agreement discovery** first, because that is where blind v1.3 loses to the no-skill baseline. Morphology, number grammar, and orthography should remain unchanged until a benchmark demonstrates a real gap.
