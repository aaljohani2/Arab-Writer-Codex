# v1.4 Punctuation Adjudication Protocol v1

Status: design approved for the next measurement phase.  
Branch: `feature/v1.4-arabic-linguistic-core`

## Why this protocol exists

The full blind Challenge Set v1 produced only 40% exact/substantive score for PUN in both baseline and candidate, while the other linguistic families were substantially stronger.

That number must **not** be treated as proof that 60% of the punctuation outputs were linguistically wrong. Several current PUN cases encode a preferred editorial punctuation pattern as one exact gold string even though alternative comma/semicolon/colon choices can remain defensible.

The purpose of this protocol is to prevent the project from overfitting Arab Writer to one punctuation house style.

## Governing principle

Punctuation is evaluated by **function before glyph choice**.

Ask first:

1. Does the punctuation preserve or clarify the intended syntactic relation?
2. Does it prevent a materially misleading parse?
3. Is the mark mechanically required by the writing convention in question?
4. Are there multiple established editorial choices that preserve the same relation?

Only the first three can support a high-confidence deterministic failure. If the fourth applies, use human adjudication rather than exact-gold punishment.

## Adjudication classes

### `PUN-D1-DETERMINISTIC`

A mechanical or strongly conventional error whose correction is expected regardless of house style.

Typical targets:

- mismatched quotation marks or parentheses;
- a direct question closed with an incompatible terminal mark when the interrogative force is unambiguous;
- punctuation separated from the preceding Arabic word by an erroneous space under the selected house style;
- duplicated punctuation produced accidentally;
- missing or malformed paired punctuation that changes readability materially;
- use of an incompatible punctuation direction/form where the document explicitly requires Arabic punctuation conventions.

These cases may be scored automatically when the expected transformation is genuinely unique.

### `PUN-S2-STRUCTURAL`

A punctuation choice with a strong structural recommendation but some editorial latitude.

Examples:

- colon before an announced enumeration or explanation;
- semicolon between longer coordinated clauses when the writer wants an intermediate stop;
- commas separating list members;
- punctuation separating a lead-in phrase from a following explanatory sequence.

These cases should allow more than one acceptable answer when the alternatives preserve the intended structure.

### `PUN-J3-EDITORIAL`

A house-style or rhetorical choice rather than a correctness defect.

Examples:

- comma versus semicolon between two independently complete but closely related clauses;
- optional comma around a short explanatory `هي` clause;
- colon versus dash in an editorially introduced explanation;
- punctuation density in classical/heritage prose when modernization was not requested.

These cases must not be used as deterministic correctness failures.

## Heritage-sensitive rule

Classical Arabic prose predates the modern punctuation system used in contemporary publishing. When editing heritage text:

- do not infer that the original author "made a punctuation mistake" merely because a modern edition could punctuate the passage differently;
- distinguish original/source punctuation from editor-supplied modern punctuation;
- if the task is proofreading rather than modernization, preserve a defensible punctuation scheme unless it creates a real parsing problem;
- if modernization is requested, apply one declared modern house style consistently.

## Reference anchors

The punctuation layer should be grounded in both historical and modern Arabic writing references, including:

- أحمد زكي باشا — `الترقيم وعلاماته في اللغة العربية` (1912), an early systematic Arabic treatment of modern punctuation;
- university-level Arabic writing guidance such as King Saud University's `أساسيات الكتابة العربية`, which summarizes punctuation functions and cites multiple Arabic orthography/writing references;
- modern Arabic writing-system work from the King Salman Global Academy for Arabic Language discussing punctuation and variation in Arabic writing conventions;
- additional contemporary editing/style manuals should be cited at case level when a house-style rule is being tested.

Reference anchors are for rule grounding. Benchmark sentences and gold answers must not be copied into runtime knowledge.

## Fresh holdout design

Create a new punctuation holdout separate from Challenge Set v1:

`evals/punctuation_holdout_v1_*.jsonl`

Target size: **18 cases**.

| Class | Cases | Purpose |
|---|---:|---|
| PUN-D1-DETERMINISTIC | 6 | unique/mechanical corrections |
| PUN-S2-STRUCTURAL | 6 | structurally preferred but adjudicable |
| PUN-J3-EDITORIAL | 6 | preservation / acceptable-variant controls |

Balance:

- 9 heritage/classical-source contexts;
- 9 modern/contemporary contexts;
- at least 6 `PRESERVE` cases;
- at least 4 paired-punctuation/mechanical cases;
- at least 4 list/enumeration cases;
- at least 4 cases where two outputs are deliberately registered as acceptable variants.

## Case schema additions

For punctuation holdout cases add:

- `pun_class`: `PUN-D1-DETERMINISTIC | PUN-S2-STRUCTURAL | PUN-J3-EDITORIAL`
- `acceptable_outputs`: list of normalized acceptable strings; empty only when a unique deterministic gold is justified
- `house_style`: `neutral | modern-arabic | source-preserving | named-style`
- `adjudication_required`: boolean
- `source_period`: `heritage | modern`
- `rule_source`: bibliographic/rule anchor

The existing `expected` field remains for compatibility, but it is no longer the sole truth for S2/J3 cases.

## Scoring policy

### Automatic score

For `PUN-D1-DETERMINISTIC`:

- exact gold may be used when unique;
- otherwise pass if normalized output is in `acceptable_outputs`.

### Adjudicated score

For `PUN-S2-STRUCTURAL` and `PUN-J3-EDITORIAL`:

- first test against `acceptable_outputs`;
- unmatched outputs go to blind human adjudication;
- adjudicator labels:
  - `PASS_EQUIVALENT`
  - `PASS_STYLE_VARIANT`
  - `FAIL_STRUCTURE`
  - `FAIL_MEANING`
  - `FAIL_MECHANICAL`

Do not convert `PASS_STYLE_VARIANT` into a grammar/correctness failure.

## Runtime knowledge gate

Do **not** wire `references/arabic-punctuation.md` merely to improve the existing five PUN Challenge Set exact strings.

A punctuation runtime reference may be added only after:

1. this adjudication schema is represented in tests/data;
2. the fresh 18-case holdout is authored from independent source contexts;
3. v1.3 blind behavior is measured on that holdout before punctuation knowledge is added;
4. candidate gains are assessed by deterministic + adjudicated outcomes, not exact-gold alone.

## Current decision

Phase 1 syntax/agreement is frozen as a provisional positive gain. Punctuation is the next **measurement** workstream, but not yet the next runtime knowledge injection.

MOR, NUM, ORT, and AMB remain untouched while they continue to score 100% substantive on Challenge Set v1.
