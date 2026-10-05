# Arabic Error Taxonomy v1.0

Status: **draft engineering specification for Arab Writer v1.4**  
Target: `feature/v1.4-arabic-linguistic-core`  
Scope: Modern Standard Arabic editing, with Saudi/professional locale packs layered separately.

## 1. Purpose

This taxonomy defines what Arab Writer should recognize as an Arabic language defect, what should remain an editorial opportunity rather than an error, how confidence should be handled, and how each category should be evaluated.

The goal is not to turn Arab Writer into a deterministic parser. The goal is to give the model a structured Arabic linguistic knowledge layer that improves proofreading and rewriting while preserving the v1.3 contract:

> Meaning and evidence outrank elegance.

The taxonomy therefore separates:

1. **definite defects** that should normally be corrected;
2. **context-dependent defects** that require sentence-level or document-level interpretation;
3. **editorial opportunities** where more than one form may be correct;
4. **ambiguous cases** where preservation or human review is safer than guessing.

## 2. Design principles

### 2.1 Context before rule matching
A surface pattern is not sufficient evidence of an error when Arabic syntax, ellipsis, dialect, quotation, proper names, or context can change the analysis.

### 2.2 Correct text is protected
A correct source is a first-class test case. Over-correction is a regression.

### 2.3 Minimality depends on mode
- `proofread`: correct the defect with the smallest justified change.
- `rewrite`: permit structural changes only when they create clear editorial gain.
- `naturalize`: address stiffness and formulaic prose without inventing facts or flattening voice.

### 2.4 Linguistic correction remains subordinate to fidelity
A grammatically smoother candidate must be rejected if it alters negation, modality, conditions, quantities, attribution, chronology, citations, or protected terminology.

### 2.5 Deterministic checks are narrow
Use deterministic rules only for high-confidence mechanical phenomena. Morphology, syntax, attachment, ellipsis, and ambiguity usually require model judgment.

## 3. Classification dimensions

Every taxonomy item should carry the following dimensions.

### 3.1 Family
- `ORT` — orthography
- `MOR` — morphology
- `SYN` — syntax/government
- `AGR` — agreement and reference
- `NUM` — numeral grammar
- `PUN` — punctuation and segmentation
- `AMB` — ambiguity and judgment
- `STY` — sentence craft/editorial quality

### 3.2 Status
- `DEFECT` — linguistically incorrect in the resolved context.
- `CONTEXTUAL_DEFECT` — incorrect only after contextual analysis.
- `EDITORIAL_OPPORTUNITY` — source may be correct but improvable.
- `AMBIGUOUS` — insufficient evidence for a safe correction.

### 3.3 Confidence
- `D1_DETERMINISTIC` — mechanically checkable with very low false-positive risk.
- `C2_HIGH_CONTEXT` — correction is strongly supported after context is resolved.
- `C3_MODEL_JUDGMENT` — requires linguistic interpretation; no blind rule.
- `H4_HUMAN_REVIEW` — competing analyses remain plausible or stakes are high.

### 3.4 Severity
- `S1_MECHANICAL` — visible spelling/typing/punctuation defect with low semantic risk.
- `S2_GRAMMATICAL` — morphology/syntax/agreement defect affecting correctness.
- `S3_CLARITY` — defect or structure that materially obscures interpretation.
- `S4_MEANING_RISK` — correction may alter scope, reference, modality, conditions, or factual relations.

### 3.5 Default action
- `CORRECT`
- `CORRECT_AFTER_CONTEXT`
- `PRESERVE`
- `FLAG`
- `EDITORIAL_REWRITE_ONLY`

---

# 4. ORT — Orthography

## ORT-01 Hamzat al-qat‘ vs hamzat al-wasl
Examples of target phenomena include standard spelling in forms such as `إن`, `إلى`, `أحمد`, and initial alif in words governed by hamzat al-wasl conventions.

- Status: `DEFECT` when the lexical form is certain.
- Confidence: `C2_HIGH_CONTEXT`; selected lexical cases may be `D1_DETERMINISTIC`.
- Guard: do not alter proper names, brands, quoted forms, or identifiers by intuition.

## ORT-02 Medial hamza
Check the written seat of medial hamza where standard spelling is determined by surrounding vowels and lexical convention.

- Status: `DEFECT`.
- Confidence: `C2_HIGH_CONTEXT`.
- Eval requirement: include correct forms that must remain unchanged.

## ORT-03 Final hamza
Check final hamza spelling based on the preceding letter/vowel where applicable.

- Status: `DEFECT`.
- Confidence: `C2_HIGH_CONTEXT`.

## ORT-04 Alif maqsurah vs yaa
Examples: distinction between final `ى` and `ي` where the lexical form requires it.

- Status: `DEFECT`.
- Confidence: `C2_HIGH_CONTEXT`.
- Guard: preserve names and official spellings unless verified.

## ORT-05 Taa marbuta vs haa vs taa maftuha
Detect confusion between `ة`, `ه`, and `ت` when morphology and lexical identity resolve the form.

- Status: `DEFECT`.
- Confidence: `C2_HIGH_CONTEXT`.

## ORT-06 Alif fariqa after waw al-jama‘a
Target forms such as the orthographic distinction in verb forms ending with plural `وا`.

- Status: `DEFECT`.
- Confidence: generally `C2_HIGH_CONTEXT` because the token must first be identified morphologically.

## ORT-07 Added/deleted letters in conventional spelling
Covers missing or duplicated letters caused by typing and selected standardized forms.

- Status: `DEFECT`.
- Confidence: `D1_DETERMINISTIC` for obvious duplication; otherwise `C2_HIGH_CONTEXT`.

## ORT-08 Word joining and separation
Covers conventional joining/separation where a stable orthographic rule applies.

- Status: `DEFECT`.
- Confidence: `C2_HIGH_CONTEXT`.

## ORT-09 Tatweel and invisible-direction artifacts
Covers accidental `ـ`, zero-width characters, bidi artifacts, and visually defective hidden characters.

- Status: `DEFECT`.
- Confidence: `D1_DETERMINISTIC`.

## ORT-10 Diacritics
Do not treat absent full vocalization as an error. Correct only necessary or explicitly requested diacritics, or preserve critical diacritics already present in names, quotations, religious text, or terminology.

- Status: normally `PRESERVE`.
- Confidence: `C3_MODEL_JUDGMENT`.

---

# 5. MOR — Morphology

## MOR-01 Verb inflection
Check person, number, gender, tense/form, and suffix morphology when the governing context is resolved.

Example defect class: a verb form incompatible with its required inflection.

- Status: `DEFECT` or `CONTEXTUAL_DEFECT`.
- Confidence: `C2_HIGH_CONTEXT`.

## MOR-02 Weak verbs
Cover common inflectional behavior of:
- المثال;
- الأجوف;
- الناقص;
- اللفيف.

The aim is editing correctness, not exhaustive historical morphology.

- Confidence: `C3_MODEL_JUDGMENT` unless the form is unambiguous.

## MOR-03 The five verbs — الأفعال الخمسة
Cover رفع بثبوت النون and نصب/جزم بحذفها when the verb is genuinely one of the five forms.

Example test pair:
- incorrect in resolved context: `لن يكتبون التقارير.`
- candidate: `لن يكتبوا التقارير.`

No-change control:
- `هم يكتبون التقارير يوميًا.`

- Status: `DEFECT`.
- Confidence: `C2_HIGH_CONTEXT`.

## MOR-04 Dual morphology
Check nominative vs accusative/genitive dual endings when explicitly represented in undiacritized spelling.

- Status: `DEFECT`.
- Confidence: `C2_HIGH_CONTEXT`.

## MOR-05 Sound masculine plural
Check `ون/ين` where syntactic position is recoverable with high confidence.

- Status: `DEFECT`.
- Confidence: `C2_HIGH_CONTEXT`.
- Guard: do not force case analysis when ellipsis or syntactic attachment is unresolved.

## MOR-06 Sound feminine plural
Check plural formation and written inflection where relevant.

- Status: `DEFECT`.
- Confidence: `C2_HIGH_CONTEXT`.

## MOR-07 Broken plurals
Treat lexical plural selection conservatively. A less common plural is not automatically wrong.

- Status: often `AMBIGUOUS` or `CONTEXTUAL_DEFECT`.
- Confidence: `C3_MODEL_JUDGMENT` / `H4_HUMAN_REVIEW`.

## MOR-08 The five nouns — الأسماء الخمسة
Cover the conditions under which `أب، أخ، حم، فو، ذو` take the letter-based inflectional forms, including relevant constraints such as addition and the meaning of `ذو`.

- Status: `DEFECT` when conditions are satisfied and the form conflicts with syntactic government.
- Confidence: `C3_MODEL_JUDGMENT`.

## MOR-09 Maqsur, manqus, mamdud nouns
Cover editing-relevant behavior of الاسم المقصور والمنقوص والممدود, including visible yaa deletion/retention in appropriate indefinite environments.

- Confidence: `C3_MODEL_JUDGMENT`.

## MOR-10 Derived forms
Cover common misuse of اسم الفاعل، اسم المفعول، المصدر، صيغ المبالغة, and related derived forms only when lexical/morphological evidence is strong.

- Status: `CONTEXTUAL_DEFECT`.
- Confidence: `C3_MODEL_JUDGMENT`.

## MOR-11 Attached pronouns
Check attachment and morphophonological form when the antecedent/function is clear.

- Status: `DEFECT` or `CONTEXTUAL_DEFECT`.
- Confidence: `C2_HIGH_CONTEXT`.

---

# 6. SYN — Syntax and government

## SYN-01 Nominal sentence completeness
Detect missing or structurally broken subject/predicate relations while allowing legitimate ellipsis and marked structures.

- Status: `CONTEXTUAL_DEFECT`.
- Confidence: `C3_MODEL_JUDGMENT`.

## SYN-02 Verbal sentence structure
Check verb/subject structure and required complements without assuming every verb requires an object.

- Critical guard: do not encode the false rule `verbal sentence = verb + subject + object`.
- Confidence: `C3_MODEL_JUDGMENT`.

## SYN-03 Kana and sisters
Check the syntactic relation of `كان وأخواتها` and visible forms affected by their government.

- Status: `DEFECT` in resolved contexts.
- Confidence: `C2_HIGH_CONTEXT` / `C3_MODEL_JUDGMENT`.

## SYN-04 Inna and sisters
Check the syntactic relation of `إن وأخواتها`, including visible nominal forms and agreement downstream.

Example defect class: `إن المعلمون حاضرون` when the intended standard construction is clear.

- Status: `DEFECT`.
- Confidence: `C2_HIGH_CONTEXT`.

## SYN-05 Prepositional government
Check forms governed by prepositions only where the written morphology exposes the case distinction.

- Status: `DEFECT`.
- Confidence: `C2_HIGH_CONTEXT`.

## SYN-06 Idafa
Check the relation between مضاف and مضاف إليه, including deletion of nun in dual/sound masculine plural when required by addition.

- Status: `DEFECT`.
- Confidence: `C2_HIGH_CONTEXT`.

## SYN-07 Adjective — النعت
Check noun-adjective dependency and applicable agreement dimensions.

- Status: `DEFECT` or `CONTEXTUAL_DEFECT`.
- Confidence: `C2_HIGH_CONTEXT`.

## SYN-08 Coordination — العطف
Check broken coordination, mismatched syntactic levels, and conjunction choice only when the intended relation is clear.

- Grammatical mismatch: `DEFECT`.
- Conjunction preference: often `EDITORIAL_OPPORTUNITY`.

## SYN-09 Emphasis — التوكيد
Recognize lexical and semantic emphasis structures; do not “simplify” legitimate repetition merely because it repeats words.

- Status: usually `PRESERVE` unless structurally defective.

## SYN-10 Apposition/substitution — البدل
Recognize common بدل structures to avoid false agreement/case corrections.

- Confidence: `C3_MODEL_JUDGMENT`.

## SYN-11 Circumstantial accusative — الحال
Distinguish:
- الحال المفرد: منصوب;
- الجملة وشبه الجملة: في محل نصب when functioning as الحال.

Do not encode the simplistic rule that every surface form used as a حال must carry a visible accusative ending.

## SYN-12 Tamyiz
Check clear tamyiz constructions, especially where they interact with numbers and quantities.

- Confidence: `C3_MODEL_JUDGMENT`.

## SYN-13 Exception — الاستثناء
Cover common structures with `إلا`, and editing-relevant behavior of `غير/سوى/عدا/خلا/حاشا` conservatively.

Required knowledge includes:
- التام المثبت;
- التام المنفي;
- الناقص المنفي;
- distinction between nominal and verbal/prepositional analyses where relevant.

- Confidence: `C3_MODEL_JUDGMENT`.

## SYN-14 Vocative — النداء
Cover the five common pedagogical types and visible inflectional consequences.

- Confidence: `C3_MODEL_JUDGMENT`.

## SYN-15 Conditional structures
Distinguish jussive and non-jussive particles. In particular, do not treat `لو` as a jussive conditional particle.

- Status: `DEFECT` where government is visibly violated.
- Confidence: `C2_HIGH_CONTEXT`.

## SYN-16 Subjunctive/jussive particles
Check forms after particles such as `لن` and jussive contexts such as `لم`, while respecting irregular/weak-verb morphology.

- Confidence: `C2_HIGH_CONTEXT`.

## SYN-17 La النافية للجنس
Check clear uses of `لا` النافية للجنس without confusing them with ordinary negation.

- Confidence: `C3_MODEL_JUDGMENT`.

## SYN-18 Relative-clause structure
Check relative pronoun compatibility and presence/clarity of the required linking relation where applicable.

- Confidence: `C3_MODEL_JUDGMENT`.

## SYN-19 Passive structures
Recognize passive syntax and نائب الفاعل so that the editor does not manufacture an unnecessary explicit agent.

- Status: mostly recognition/guard category.

## SYN-20 Diptotes — الممنوع من الصرف
Handle only when the syntactic environment and lexical class are sufficiently certain. This category has elevated false-positive risk.

- Confidence: `H4_HUMAN_REVIEW` by default in ambiguous prose.

---

# 7. AGR — Agreement and reference

## AGR-01 Verb–subject agreement
Check person/gender/number under standard Arabic agreement rules, including the difference between pre-verbal and post-verbal subject configurations.

- Status: `DEFECT` when analysis is resolved.
- Confidence: `C2_HIGH_CONTEXT` / `C3_MODEL_JUDGMENT`.

## AGR-02 Noun–adjective agreement
Check gender, number, definiteness, and syntactic dependency where overtly recoverable.

- Confidence: `C2_HIGH_CONTEXT`.

## AGR-03 Non-human plural agreement
Treat non-human plural agreement according to standard Arabic behavior and avoid mechanically forcing human-plural patterns.

- Confidence: `C3_MODEL_JUDGMENT`.

## AGR-04 Demonstrative agreement
Check demonstrative selection against the intended noun/reference.

- Confidence: `C2_HIGH_CONTEXT`.

## AGR-05 Relative pronoun agreement
Check gender/number compatibility of relative pronouns where the antecedent is clear.

- Confidence: `C2_HIGH_CONTEXT`.

## AGR-06 Pronoun antecedent
Detect clearly broken antecedent relations and ambiguous reference.

- Clear mismatch: `CONTEXTUAL_DEFECT`.
- Multiple plausible antecedents: `AMBIGUOUS` and usually `FLAG`/`PRESERVE`.

## AGR-07 Person consistency
Detect accidental switches such as moving between first/second/third person without rhetorical or quoted justification.

- Status: `CONTEXTUAL_DEFECT` or `EDITORIAL_OPPORTUNITY`.

---

# 8. NUM — Arabic numeral grammar

This family is separate from v1.3 numeric semantic-value and presentation policies. `NUM` governs the Arabic words and syntactic construction around a number; it must never change the protected numeric value.

## NUM-01 One and two
Check agreement and placement behavior of `واحد/واحدة` and `اثنان/اثنتان` in standard constructions.

## NUM-02 Three through ten
Check polarity with the counted noun and plural/genitive counted-noun behavior.

Example class:
- `ثلاث طالبات` vs the correct form required by the intended noun gender.

## NUM-03 Eleven and twelve
Check agreement patterns and the special inflectional behavior of twelve.

## NUM-04 Thirteen through nineteen
Check mixed agreement behavior across the two components.

## NUM-05 Decades
Check `عشرون` through `تسعون` and the singular accusative tamyiz pattern where applicable.

## NUM-06 Coordinated numbers 21–99
Check unit/decade interaction and tamyiz.

## NUM-07 Hundreds, thousands, millions, billions
Check counted-noun relation and idafa/tamyiz patterns conservatively.

## NUM-08 Ordinals
Check gender/agreement and compound ordinal forms in dates, rankings, and formal prose.

## NUM-09 Units and measures
Protect semantic value and unit attachment first; correct the surrounding Arabic grammar second.

### NUM safety rule
If the proposed linguistic correction changes the numeric value, measure, unit, time period, or entity relation, reject it regardless of grammatical elegance.

---

# 9. PUN — Punctuation and segmentation

## PUN-01 Arabic punctuation symbols
Prefer `،` `؛` `؟` in Arabic prose where appropriate, without altering punctuation inside code, URLs, identifiers, formulas, citations, or official foreign names.

## PUN-02 Punctuation spacing
No unnecessary space before punctuation; normal prose spacing after punctuation where the sentence continues.

- Confidence: `D1_DETERMINISTIC` in ordinary prose.

## PUN-03 Subject–predicate comma
Flag/remove an unjustified comma that mechanically separates a simple subject from its predicate.

- Confidence: `C2_HIGH_CONTEXT`.

## PUN-04 Sentence boundaries
Detect run-ons and fragments based on logical boundaries, not arbitrary word counts.

- Status: often `EDITORIAL_OPPORTUNITY` or `CONTEXTUAL_DEFECT`.
- Confidence: `C3_MODEL_JUDGMENT`.

## PUN-05 Colon/semicolon/list structure
Use punctuation to reflect hierarchy and relation, especially in professional documents and enumerations.

- Status: mostly `EDITORIAL_OPPORTUNITY`.

## PUN-06 Quotation boundaries
Preserve quoted wording. Punctuation corrections must not silently alter the content of a quotation.

---

# 10. AMB — Ambiguity and judgment

This family is a guardrail against confident but unsupported correction.

## AMB-01 Ambiguous pronoun reference
When more than one antecedent is plausible, do not guess unless the requested mode permits rewriting for clarity and the intended meaning is recoverable.

- Default action: `FLAG` or `PRESERVE`.

## AMB-02 Attachment ambiguity
Prepositional phrases, relative clauses, and modifiers may attach to more than one constituent.

- Default action: `PRESERVE` unless context resolves the attachment.

## AMB-03 Undiacritized case ambiguity
Do not manufacture case endings or grammatical errors merely because undiacritized text admits multiple parses.

- Default action: `PRESERVE`.

## AMB-04 Lexical ambiguity
A rare but valid word/derivation is not automatically an error. Prefer verification over normalization by familiarity.

## AMB-05 Proper names and official forms
Never “correct” names, regulations, product names, standards, brands, model identifiers, organization names, or titles by intuition.

- Default action: `PRESERVE` unless verified from a source or user instruction.

## AMB-06 Quotation/religious/legal text
Do not modernize, normalize, or paraphrase protected quoted text during proofreading. Verify against the supplied source when exactness matters.

## AMB-07 Dialect vs MSA
Do not classify a dialect form as an error when the task explicitly preserves dialect or voice. Route through `dialect-sensitive` and locale guidance.

## AMB-08 Disputed/variant usage
If reputable analyses permit more than one form, do not present one as the only “correct” form without a task-specific standard.

- Default action: `PRESERVE` or explain when diagnostic feedback was requested.

---

# 11. STY — Sentence craft and editorial quality

`STY` items are not automatically grammatical errors. They mainly apply to `rewrite`, `naturalize`, `document`, and selected high-depth professional editing.

## STY-01 Nominalization overload
Example pattern:
`العمل على القيام بتطوير وتحسين مستوى...`

Prefer a direct verbal structure when it improves clarity without changing agency or modality.

- Status: `EDITORIAL_OPPORTUNITY`.

## STY-02 Coordination chains
Excessive `و` can flatten logical hierarchy. Restructure only when the relations among propositions are recoverable.

## STY-03 Factual/chronological overload
Split a sentence when it contains several independent factual moves that obscure sequence, attribution, or conditions.

## STY-04 Literal translation syntax
Correct calques and foreign-language ordering when the Arabic is unnatural or ambiguous, while preserving technical terms and source meaning.

## STY-05 Semantic repetition
Remove or merge repeated propositions only after confirming that the second occurrence does not add scope, evidence, qualification, or emphasis.

## STY-06 Generic framing/meta-sentences
Reduce empty framing such as generic introductions/conclusions that do not add content, but do not delete required academic or legal framing.

## STY-07 Weak transitions
Add or revise transitions only when the logical relation is supported by the surrounding text. Never invent causality through a transition.

## STY-08 Parallelism
Improve malformed list/series parallelism where items occupy the same logical level.

## STY-09 Passive overuse
Prefer active voice only when agency is known and changing voice does not alter responsibility, legal meaning, or deliberate impersonal style.

## STY-10 Register mismatch
Align diction and sentence shape with the requested register. Do not equate “formal” with inflated or archaic prose.

## STY-11 Redundant modifiers
Remove intensifiers/adjectives that add no meaning only when voice and rhetorical emphasis are not intentionally dependent on them.

## STY-12 Long idafa chains
Recast dense chains of successive genitives when they cause attachment ambiguity or processing difficulty.

---

# 12. Correction decision protocol

For each suspected issue:

1. **Detect** the candidate span.
2. **Classify** it using a taxonomy ID.
3. **Resolve context**: sentence, paragraph, protected facts, locale, quotation status, and task mode.
4. **Assign confidence** (`D1/C2/C3/H4`).
5. **Choose action** (`CORRECT`, `PRESERVE`, `FLAG`, or editorial rewrite).
6. **Generate the lightest sufficient candidate**.
7. **Re-parse the full sentence**, not only the changed token.
8. **Run fidelity checks** for meaning, negation, modality, conditions, values, entities, dates, citations, and terminology.
9. **Run regression review**: what became worse?
10. In `proofread`, revert changes that are not supported as actual defects.

# 13. Evaluation schema

Every major rule should have at least four case types:

1. **Correction case** — contains the target defect.
2. **No-change control** — similar surface form but correct.
3. **Adversarial/context case** — same marker with a different grammatical function or legitimate reading.
4. **Fidelity case** — correction must not alter protected meaning.

Recommended JSONL fields:

```json
{
  "id": "MOR-03-001",
  "family": "MOR",
  "rule": "MOR-03",
  "status": "DEFECT",
  "confidence": "C2_HIGH_CONTEXT",
  "severity": "S2_GRAMMATICAL",
  "mode": "proofread",
  "locale": "msa",
  "source": "لن يكتبون التقارير.",
  "expected": "لن يكتبوا التقارير.",
  "action": "CORRECT",
  "protected": [],
  "rationale": "Five-verbs form is subjunctive after لن; nun is deleted.",
  "tags": ["verbs", "subjunctive", "minimal-edit"]
}
```

For no-change cases, `expected` must equal `source`.

# 14. Initial benchmark allocation

Target for the first v1.4 linguistic-core dataset: approximately **650 authored/verified cases**.

| Family | Initial target |
|---|---:|
| ORT | 80 |
| MOR | 70 |
| SYN | 150 |
| AGR | 80 |
| NUM | 60 |
| PUN | 40 |
| AMB / no-change / adversarial | 80 |
| STY | 90 |
| **Total** | **650** |

The allocation may change after the first 300-case pilot if false-positive concentration shows that specific families need more coverage.

# 15. Source and authorship policy for linguistic cases

- Rules may be documented from reputable Arabic grammar, morphology, orthography, and writing references.
- Evaluation sentences should preferably be newly authored fixtures rather than copied textbook passages.
- External benchmark samples must retain their original attribution/license requirements.
- A reference supports the linguistic rule; it does not automatically license copying examples.
- Disputed issues must be labeled as such rather than flattened into a single absolute rule.

# 16. v1.4 implementation mapping

This taxonomy is intended to feed the following progressive references:

- `references/arabic-orthography.md` ← ORT + relevant PUN
- `references/arabic-morphology.md` ← MOR
- `references/arabic-syntax.md` ← SYN + AGR
- `references/arabic-numerals-grammar.md` ← NUM
- `references/arabic-ambiguity-and-judgment.md` ← AMB
- `references/arabic-sentence-craft.md` ← STY + advanced PUN

Existing v1.3 references remain authoritative for:
- fidelity;
- naturalness;
- voice;
- Saudi/Gulf pragmatics;
- domain-specific academic/financial/legal/professional behavior;
- long-document ledgers;
- bibliography and numeric semantic-value preservation.

# 17. v1.4 release evidence required

The taxonomy itself is not evidence that Arabic quality improved.

Before a general v1.4 quality claim, require:

- critical fidelity regressions = 0;
- correct-source preservation >= 98% on the internal linguistic suite;
- introduced grammatical-error rate <= 1% on reviewed cases;
- false-correction rate <= 5% in `proofread`;
- correction coverage improves over the pinned baseline;
- no material regression on licensed/external Arabic GEC and linguistic benchmarks used in the comparison;
- blind human review on proofreading and rewrite outputs;
- no meaningful regression in `rewrite`/`naturalize` from excessive linguistic conservatism.

# 18. Explicit non-goals for v1.4

v1.4 does not attempt to provide:

- a complete theoretical Arabic grammar;
- exhaustive classical Arabic parsing;
- automatic full i‘rab of every sentence;
- a deterministic rule engine for all Arabic syntax;
- universal dialect normalization;
- broad rhetoric/بلاغة optimization.

Advanced rhetoric, figurative language, and higher-order البلاغة should be considered separately after the linguistic core is empirically stable.

# 19. Next implementation gate

Before changing `SKILL.md`, create a pilot suite of **approximately 300 cases** covering the highest-value rules:

1. orthography;
2. five verbs / dual / sound plurals;
3. إن/كان and common government;
4. adjective and verb–subject agreement;
5. number grammar;
6. pronoun ambiguity;
7. correct-source no-change controls;
8. sentence-craft cases that distinguish true correction from optional rewriting.

Only after the pilot is reviewed should the new references be wired into routing.