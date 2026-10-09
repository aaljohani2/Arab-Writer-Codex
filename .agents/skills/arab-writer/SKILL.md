---
name: arab-writer
description: Context-aware high-fidelity Arabic writing and editing for Codex. Use for Arabic proofreading, rewriting, naturalization, voice preservation, academic/financial/legal/professional/technical writing, Saudi/Gulf register, dialect-sensitive editing, or long-document revision. Trigger when improving Arabic writing is the task; do not trigger for coding, research-only questions, or isolated word translation unless editing/writing is requested.
---

# Arab Writer v1.3

The user's explicit instructions are the highest-priority writing constraints.

## Operating loop

1. **Route** — choose the primary mode and only the relevant context packs.
2. **Risk** — set `standard`, `elevated`, or `high-fidelity`.
3. **Ledger** — protect facts, relations, modality, conditions, citations, tables, code, and requested voice/locale.
4. **Edit** — use the lightest edit that produces a real gain.
5. **Verify** — audit language, fidelity, voice/locale, missed opportunities, and regressions.
6. **Return** — provide exactly the requested artifact.

Meaning and evidence outrank elegance.

## Modes

Primary:
- `proofread` — discover and correct definite language/mechanical defects with the smallest valid edit; do not rewrite correct wording.
- `rewrite` — improve wording, clarity, and flow.
- `naturalize` — reduce stiffness, generic framing, repetition, and mechanical structure.
- `voice-lock` — improve defects while keeping recognizable style within an acceptable drift band.
- `shorten` — reduce length by information priority.
- `expand` — develop only from supplied facts or clearly labeled explanation.
- `translate-polish` — translate and produce natural target Arabic.
- `document` — multi-section/long-document editing with a persistent ledger.

Context packs, only when relevant:
`professional`, `executive`, `academic`, `financial`, `policy-legal`,
`marketing-social`, `technical-product`, `saudi-gulf`, `dialect-sensitive`,
`bilingual`.

## Fidelity levels

### Standard
Ordinary messages and general writing.

### Elevated
Professional/public/customer-facing content.

### High fidelity
Academic, financial, legal, regulatory, medical, technical, policy, contract,
or any text with critical values, dates, citations, standards, IDs, conditions,
or evidentiary claims.

At high fidelity, load `references/fidelity-graph.md` and run the applicable
deterministic QA helpers when files are available.

## Progressive references

Always:
- `references/arabic-core.md`
- `references/quality-gates.md`

Correctness-heavy, especially `proofread`:
- `references/arabic-linguistic-verification.md`
- `references/arabic-syntax.md`
- `references/arabic-punctuation.md`

For proofreading, perform a short grammatical discovery pass before deciding that the source needs no correction. Minimality means **small edits**, not missed deterministic errors. Use `arabic-syntax.md` to test governed relations and agreement before preserving a suspicious form.

In blind proofreading, do not return a suspicious sentence unchanged before checking visible case/agreement relations. Give special attention to:
- direct adjective/predicate agreement with non-human plurals;
- passive verbs that take two objects, where the promoted first object becomes نائب الفاعل;
- dual and sound-plural endings whose case is visible in the letters.

When changing agreement, prove the target's syntactic attachment first. Do not propagate agreement to a separate clause or phrase merely because it follows the same noun.

For punctuation in proofreading, classify the issue before editing: deterministic/mechanical (D1), structural/contextual (S2), or editorial/judgment (J3). Fix D1, repair S2 only when a real boundary is missing or misleading, and preserve J3 unless the user supplied a house style. Use `arabic-punctuation.md` for this decision.

By task:
- naturalize → `references/naturalness.md`
- voice-lock → `references/tone-and-voice.md`, `references/voice-profile.md`
- document → `references/document-mode.md`
- financial → `references/financial-business.md`
- academic → `references/academic-research.md`
- policy/legal → `references/policy-legal.md`
- professional/executive → `references/professional-executive.md`
- Saudi/Gulf → `references/saudi-gulf.md`, `references/saudi-pragmatics.md`
- dialect → `references/dialect-sensitive.md`
- bibliography/citations → `references/bibliography.md`
- numeric normalization → `references/numeral-policy.md`
- editorial rewrite/naturalize → `references/editorial-gain.md`

Do not load naturalization guidance for proofreading-only tasks.

## High-fidelity ledger

Capture, as applicable:
- named entities and titles;
- dates/deadlines/periods;
- amounts, percentages, quantities, units, currencies;
- identifiers, standards, versions;
- citations, DOI, URLs, email addresses;
- quotations, code, formulas and table relationships;
- conditions and exceptions;
- claim strength: possibility, association, causation, obligation, prohibition,
  estimate, forecast, guarantee, fact;
- numeric **semantic value separately from presentation**;
- relation graph: entity/measure → value → time/status/unit.

For long documents, persist the ledger across sections.

## Context-aware semantics

Do not classify Arabic operators from isolated words when context changes their
function. Examples:
- `قد أعلنت` is commonly past/aspectual, not uncertainty;
- `قد تعلن` can express uncertainty;
- `تضمن التقرير ثلاثة بنود` is containment, not a guarantee.

Use contextual semantic sentinels as review signals, not semantic proof.

## Editorial Gain Gate

A safe edit is not automatically a useful edit.

For `rewrite`/`naturalize`, before accepting a material change ask:
- What correctness/clarity/naturalness/organization gain does it create?
- What fidelity/voice/terminology/change cost does it introduce?
- Is the candidate clearly better than retaining the source?

If gain does not justify cost, retain the source.

Never use an edit quota.

## Verification passes

### Pass A — Edit
Produce the candidate.

### Pass B — Language + fidelity audit
Re-read source and candidate independently. Check Arabic correctness and
protected relations.

### Pass C — Missed-opportunity review
Find remaining awkwardness, semantic repetition, dense chronology, weak
transitions, redundant meta-sentences, and citation/bibliography inconsistency.

### Pass D — Adversarial regression review
Ask what became worse because of the edit. Revert changes whose gain is not
clear or whose cost is too high.

## Voice and locale

Do not maximize style-similarity blindly. Small measured drift can be acceptable
when it buys real clarity/correctness and remains within tolerance.

Do not infer dialect by substring matching. Preserve pragmatic function,
hierarchy, request strength, register, and regional scope. Never manufacture
Saudi slang to sound local.

## Numeric policy

Protect semantic numeric value absolutely unless the user requests a factual
change. Presentation may be normalized only under an explicit/document policy
and only when equivalence is proven.

Policies:
- `preserve-exact`
- `normalize-arabic`
- `normalize-western`
- `document-consistent`

## Runtime provenance

For benchmark/evaluation work, record model/reasoning only when runtime metadata
or explicit execution configuration verifies them. Requested settings inside a
prompt are not proof. Unknown stays `unknown`.

## Tools when files are available

Use as applicable:
- `scripts/qa_pair.py`
- `scripts/fidelity_graph.py`
- `scripts/semantic_sentinels.py`
- `scripts/numeral_policy.py`
- `scripts/editorial_gain.py`
- `scripts/semantic_repetition.py`
- `scripts/voice_profile.py`
- `scripts/locale_guard.py`
- `scripts/bibliography_schema.py`
- `scripts/document_ledger.py`
- `scripts/edit_trail.py`
- `scripts/run_provenance.py`
- `scripts/gec_adjudicator.py`

Heuristic findings require judgment; do not call them proof.

## Evidence policy

CI proves software checks passed, not that writing improved.

Product-quality claims require:
- baseline-vs-skill evaluation;
- multiple domains/tasks/locales;
- deterministic checks;
- Arabic-specific/external benchmark evidence where licensed;
- blind human review for material writing-quality claims.

## Non-goals

Do not:
- fabricate facts, citations, sources, quotes, or missing bibliography metadata;
- weaken uncertainty or strengthen causality without source support;
- bypass plagiarism/authorship-detection systems;
- disguise copied text as original work;
- rewrite already-good text merely to create visible changes;
- invoke this skill for unrelated coding/research-only tasks.
