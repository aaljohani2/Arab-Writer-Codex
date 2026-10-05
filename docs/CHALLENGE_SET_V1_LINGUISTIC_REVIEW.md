# Challenge Set v1 — Second-pass linguistic review

Status: **REVIEWED — 70/70 cases**  
Branch: `feature/v1.4-arabic-linguistic-core`  
Review date: 2026-10-05

## Scope

This review covers all 70 source-grounded challenge cases across:

- `SYN` — 20
- `MOR` — 15
- `NUM` — 10
- `AMB` — 10
- `AGR` — 5
- `ORT` — 5
- `PUN` — 5

The corpus remains balanced at 35 classical/heritage cases and 35 modern/contemporary cases. The review is linguistic only; no domain claim in fiqh, hadith commentary, creed, medicine, economics, science, engineering, AI, education, or public policy is scored for subject-matter truth.

## Review method

Each case was checked for:

1. grammatical or orthographic correctness of the gold answer;
2. whether the alleged defect is actually deterministic or admits a recognized Arabic variant;
3. whether a `PRESERVE` case is genuinely licensed rather than merely awkward;
4. whether the task can be decided from the supplied context rather than hidden author intent;
5. whether `protected` literals, numbers, and quoted material remain intact;
6. whether classical constructions are being modernized merely because they are unfamiliar;
7. whether modern accepted usage is being mislabeled as a grammar error;
8. whether sacred text is ever deliberately corrupted for a correction item.

## Outcome

- **68 cases:** approved without a gold-answer change.
- **2 cases:** revised because the original formulation admitted a competing grammatical reading or recognized Arabic variety.
- **0 cases:** removed.
- **0 sacred-text violations:** no deliberate error is inserted inside a Qur'anic verse or a Prophetic hadith presented as a direct quotation.

## Revisions made

### `CH-AGR-002`

Original design used a post-verbal plural form of the type `قالوا العلماء` and treated it as a deterministic error.

That is unsuitable for a source-grounded classical challenge because Arabic grammarians record the recognized, though non-majority, pattern traditionally called **لغة أكلوني البراغيث**, in which a plural/dual marker may accompany a following overt plural/dual subject. Treating every such form as categorically ungrammatical would create a false gold answer in a benchmark that deliberately includes heritage Arabic.

The case was therefore replaced with an unambiguous agreement error in which a human plural subject precedes its verb:

- source pattern: `العلماءُ ... يقول ...`
- gold pattern: `العلماءُ ... يقولون ...`

This keeps the case in `AGR`, keeps its classical provenance, and removes the dialectal/heritage ambiguity.

### `CH-MOR-012`

Original design used `لا تتوانى الجهات...` and assumed that `لا` was prohibitive. Without a sufficiently explicit directive context, the surface sentence can also be read with **لا النافية**, in which the indicative `تتوانى` is not the targeted error.

The case was rewritten with an explicit directive frame:

`وجاء في التوجيه إلى مسؤول البيانات: لا تتوانى ...`

The gold is now `لا تتوانَ ...`, so the intended prohibitive reading is contextually forced and the weak-verb jussive judgment is fair.

## High-risk judgments reviewed and retained

The following cases were reviewed specifically because a simplistic proofreader may overcorrect them:

- `CH-AMB-004` — agreement with `من` by meaning is licensed; plural agreement may be preserved when the intended referent is plural.
- `CH-AMB-006` — semantic agreement with a collective such as `طائفة` is attested in classical Arabic and may legitimately take plural reference by meaning.
- `CH-AMB-005` — `مائة` is a valid orthographic form; a proofreader should not force `مئة` when no house style requires it.
- `CH-AMB-007` — `تم + المصدر` is treated here as established contemporary institutional usage; replacing it with a passive verb is an editorial preference, not a mandatory grammar correction.
- `CH-AMB-008` — `سوى` is a valid exception/addition noun and must not be normalized automatically to `غير`.
- `CH-AMB-009` — `رقمنة` is established modern technical terminology and is protected from synonym substitution.
- `CH-AMB-010` — in a negative, emptied exception construction, the noun after `إلا` takes its syntactic role; `وجهٌ` remains nominative as the subject of `ثبت`.
- `CH-SYN-013` — so-called extra `من` after negation is a licensed classical construction and should not be deleted merely for simplification.
- `CH-SYN-017` — `رُبَّ` is a valid classical particle and must not be modernized simply because it is less frequent today.
- `CH-SYN-019` — the delayed nominative after fronted material with `كان` is valid; the surface nominative must be preserved.
- `CH-MOR-015` — the benchmark retains `دنيوي/دنيوية` as the gold nisba and rejects `دنيائي` for this rule-targeted item.

## Punctuation adjudication rule

The five `PUN` cases follow the punctuation conventions cited in their `rule_source` metadata. Punctuation, however, admits more editorial variation than morphology or core syntax.

Therefore:

- exact-match failure on a `PUN` case is **not by itself proof of a linguistic failure**;
- if Codex produces a different but coherent punctuation scheme while preserving all words and clause relations, the case must receive blind human adjudication before being counted as a substantive error;
- punctuation edits that change clause relations, introduce an inappropriate mark, leave an unmatched pair, or violate the explicitly requested punctuation operation remain true failures.

This rule prevents the benchmark from turning one editorial convention into a universal grammatical law.

## Reference stance

The review uses the challenge's declared classical and modern linguistic references as adjudication anchors, including works such as:

- `كتاب سيبويه`
- `مغني اللبيب`
- `شرح ابن عقيل`
- `جامع الدروس العربية`
- `النحو الوافي`
- `شذا العرف في فن الصرف`
- Arabic orthography and punctuation references listed in the case metadata
- modern usage references where a case explicitly tests contemporary accepted usage

The text/register provenance remains separate from the rule source: literary, Islamic, historical, scientific, medical, economic, technical, and institutional sources provide authentic linguistic pressure, while the `rule_source` supports the linguistic judgment.

## Benchmark readiness

After the two revisions above, the 70-case corpus is considered **linguistically reviewed for baseline measurement**, subject to the repository's deterministic tests and CI passing on the final review commit.

The challenge files remain evaluation-only artifacts under `evals/challenge/`; they must not be copied into the Arab Writer runtime reference layer or exposed as answer material to the candidate.
