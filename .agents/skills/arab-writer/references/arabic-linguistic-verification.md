# Arabic Linguistic Verification

Use this for proofreading and any task where Arabic correctness is a primary requirement. It complements, rather than replaces, `arabic-core.md`.

For syntax/agreement discovery and adjudication, also load `arabic-syntax.md`. For punctuation discovery and adjudication, also load `arabic-punctuation.md`.

## Two-pass rule

Do not assume the first correction pass is correct. After producing a candidate, audit it independently against the source.

### Pass A — discovery + correction

Before deciding that the text is already correct, run a short discovery scan for grammatical triggers and governed relations. In particular, inspect:

- `إن` and sisters;
- `كان` and sisters;
- `لا` النافية للجنس;
- negation/restriction with `إلا`;
- passive verbs and deputy subjects;
- human vs non-human plural agreement;
- relative-pronoun agreement;
- dual/sound-plural case forms and idafa nun deletion;
- followers such as adjective/apposition where case agreement is visible;
- jussive/subjunctive environments whose effects are visible in the written form.

Before returning **no change** in blind proofreading, perform two mandatory role checks when applicable:

1. **Non-human plural attachment check** — if a predicate/adjective directly describes a non-human plural, verify feminine-singular agreement; do not replace it with masculine singular or human-plural agreement. At the same time, do not spread that agreement to a later word that belongs to a separate clause or predicative relation.
2. **Passive ditransitive check** — if a passive verb normally takes two objects, identify whether the first post-verbal nominal is the promoted first object/نائب الفاعل. If so, require nominative form, especially when dual or sound-plural endings make the case visible.

Correct only defects that are sufficiently supported by context. Preserve correct source forms.

**Minimality must not become passivity:** once a deterministic grammatical defect is established, correct the smallest span that repairs it even if the sentence is still understandable.

### Pass B — independent audit

Review each changed span and then scan the full candidate for:
- orthography: hamza, alif maqsura/yaa, taa marbuta/haa, duplicated/missing letters;
- morphology: inflection, dual/plural forms, attached pronouns, derived forms;
- syntax: subject/predicate completeness, coordination, case-sensitive forms that are actually written, governed verb forms;
- agreement: gender, number, person, adjective/noun, verb/subject;
- number constructions and units where relevant;
- negation and particles that alter grammatical government;
- pronoun antecedents and ambiguity;
- punctuation and sentence boundaries.

For punctuation, classify a proposed edit before applying it:
- **D1 mechanical** — unmatched paired marks, wrong terminal mark on a direct question, accidental duplicated punctuation, or explicit house-style shape/spacing defects;
- **S2 structural** — a missing or misleading boundary before an announced enumeration, explanation, definition, or staged division;
- **J3 editorial** — a defensible choice of pause strength such as comma versus semicolon or colon versus dash.

Fix D1. Fix S2 only when the structure is genuinely obscured or mis-signalled. Preserve J3 in proofreading unless an explicit house style resolves the choice.

For every changed agreement span, ask: **what exactly does this word attach to?** Revert any agreement change that was driven only by proximity to a nearby noun rather than a proven syntactic relation.

## Visible morphology rule

Do not invent an error that depends only on an unshown optional case vowel. Give higher confidence to defects that are visible in the written form, such as:

- dual `ان/ين`;
- sound masculine plural `ون/ين`;
- five-noun letter forms;
- deletion/retention of nun in idafa;
- deletion of a weak letter under jussive/prohibitive government;
- an explicitly written wrong short vowel or tanwin in a vocalized span.

If the case relationship is invisible and multiple readings remain possible, preserve rather than guess.

## Minimality

A proofreading request is not a rewriting request. If a sentence is correct and clear, leave it alone. If a localized defect is proven, fix that defect without broad stylistic cleanup.

## Uncertainty

If two readings are plausible and context does not resolve them, do not guess. Preserve the source or flag the ambiguity when the user asked for diagnostic feedback.

Do not collapse recognized classical/heritage variation into a modern house style merely because the modern pattern is more frequent.

## Benchmark discipline

Internal fluency is not evidence of grammatical mastery. Regression evaluation should include natural, expert-annotated Arabic grammar/error-correction data such as Nahw-Passage and linguistic-competence suites such as AraLingBench.

Evaluation challenge cases are measurement artifacts, not runtime knowledge. Do not copy benchmark sentences, gold answers, IDs, or case-specific rationales into runtime references.
