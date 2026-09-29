# Arab Writer for Codex

> **High-fidelity Arabic writing and editing for Codex.** Improve clarity, structure, and naturalness without silently changing the facts, numbers, conditions, citations, claim strength, or intended voice behind the text.

**محرر عربي عالي الدقة لـ Codex** — يساعد على تحسين الصياغة العربية مع إعطاء الأولوية للحفاظ على المعنى والأدلة والأرقام والنبرة، بدل تحسين الأسلوب على حساب ما يقوله النص فعليًا.

[![Validate](https://github.com/aaljohani2/Arab-Writer-Codex/actions/workflows/validate.yml/badge.svg)](https://github.com/aaljohani2/Arab-Writer-Codex/actions/workflows/validate.yml)
![Version](https://img.shields.io/badge/version-1.3.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Why this exists

General-purpose AI editors can make Arabic sound better while accidentally changing what the source actually says — a percentage, a date, a condition, the strength of a claim, a citation relationship, or even the writer's voice.

**Arab Writer** is designed around a stricter rule:

> **Meaning and evidence outrank elegance.**

It is a Codex-native skill for Arabic proofreading, rewriting, naturalization, voice preservation, translation polishing, and long-document editing, with additional safeguards for professional, academic, financial, legal, technical, Saudi/Gulf, and dialect-sensitive writing.

## What it helps with

| Need | What Arab Writer does |
|---|---|
| Proofreading | Corrects definite language and mechanical issues with minimal rewriting |
| Rewriting | Improves clarity, wording, flow, and organization |
| Naturalization | Reduces stiffness, generic AI phrasing, repetition, and mechanical structure |
| Voice preservation | Improves defects while keeping the writer's recognizable style |
| High-fidelity editing | Protects critical facts, values, dates, conditions, citations, and claim strength |
| Long documents | Carries terminology, acronyms, and protected relationships across sections |
| Saudi/Gulf Arabic | Applies locale-sensitive guidance when relevant instead of forcing one generic register |
| Bibliographies | Audits consistency without inventing missing years, URLs, DOIs, or metadata |

## Quick start

### 1. Install

In Codex:

```text
$skill-installer
```

Install from:

```text
https://github.com/aaljohani2/Arab-Writer-Codex/tree/main/.agents/skills/arab-writer
```

Or copy:

```text
.agents/skills/arab-writer
```

to:

```text
$HOME/.agents/skills/arab-writer
```

### 2. Use

General rewrite:

```text
$arab-writer
راجع هذا النص وأعد صياغته بصورة طبيعية وواضحة مع الحفاظ على المعنى والنبرة.
```

Proofreading only:

```text
$arab-writer
دقق هذا النص لغويًا فقط. لا تعِد صياغة الجمل الصحيحة.
```

High-fidelity financial or legal editing:

```text
$arab-writer
حرر النص مع الحفاظ على الأرقام وعلاقاتها بالفترات والبنود، وقوة الادعاء والشروط والاستثناءات.
```

Voice-preserving edit:

```text
$arab-writer
حسّن النص مع الحفاظ على أسلوبي ونبرتي. غيّر فقط ما يحقق تحسنًا واضحًا.
```

Long-document editing:

```text
$arab-writer
راجع هذا المستند كوثيقة واحدة، وحافظ على اتساق المصطلحات والأرقام والاختصارات والعلاقات بين الفصول.
```

## Editing modes

Primary modes:

- `proofread` — minimal correction, no unnecessary rewriting.
- `rewrite` — improve clarity, wording, and flow.
- `naturalize` — reduce stiffness and generic or repetitive phrasing.
- `voice-lock` — improve the text while preserving recognizable author voice.
- `shorten` — reduce length by information priority.
- `expand` — develop only from supplied facts or clearly labeled explanation.
- `translate-polish` — translate and produce natural target Arabic.
- `document` — edit multi-section or long documents with persistent consistency checks.

Relevant context packs are loaded only when needed, including `academic`, `financial`, `policy-legal`, `professional`, `technical-product`, `saudi-gulf`, `dialect-sensitive`, and `bilingual`.

## High-fidelity behavior

When the text contains sensitive facts or evidence, Arab Writer can protect relationships such as:

```text
entity / measure → value → time / status / unit
```

Typical protected elements include:

- names, entities, and titles;
- dates, periods, and deadlines;
- amounts, percentages, quantities, currencies, and units;
- identifiers, standards, and versions;
- citations, DOI, URLs, quotations, formulas, and table relationships;
- conditions and exceptions;
- claim strength such as possibility, association, causation, obligation, estimate, forecast, or guarantee;
- numeric semantic value separately from how the number is visually presented.

The skill also uses context-aware checks instead of treating isolated Arabic words as fixed semantic signals. For example, `قد أعلنت` and `قد تعلن` should not automatically be interpreted the same way.

## Four-pass review loop

```text
Route
  ↓
Risk
  ↓
Fidelity / document ledger
  ↓
Edit
  ↓
Language + fidelity audit
  ↓
Missed-opportunity review
  ↓
Adversarial regression review
  ↓
Return
```

Every substantial edit is conceptually reviewed through four passes:

1. **Edit** — make the requested improvement.
2. **Arabic + fidelity audit** — check language and protected meaning.
3. **Missed opportunities** — identify meaningful improvements that were overlooked.
4. **Regression review** — ask what became worse because of the edit.

This is intended to reduce both under-editing and over-editing.

## Numeric policy

Available policies:

- `preserve-exact`
- `normalize-arabic`
- `normalize-western`
- `document-consistent`

Numeric presentation may be normalized only when the semantic value is verified as unchanged.

## What this project does **not** claim

- CI passing does **not** prove that one version of Arabic prose is objectively better than another.
- Deterministic checks are review signals, not automatic semantic proof.
- The skill should not invent missing facts, references, dates, URLs, or bibliography metadata.
- High-stakes academic, financial, legal, regulatory, medical, or policy text still requires appropriate human review.

The goal is not to remove judgment from writing. The goal is to make AI-assisted editing more disciplined, inspectable, and less likely to improve style by silently damaging meaning.

## Quality assurance

Run the high-fidelity helpers directly:

```bash
python .agents/skills/arab-writer/scripts/qa_pair.py before.txt after.txt
python .agents/skills/arab-writer/scripts/fidelity_graph.py before.txt after.txt
python .agents/skills/arab-writer/scripts/editorial_gain.py before.txt after.txt
```

Validate deterministic behavior:

```bash
python .agents/skills/arab-writer/scripts/validate_skill.py
python -m unittest discover -s tests -v
python evals/benchmark_matrix.py evals/benchmark_matrix.json
python tools/release_gate.py --mode structural
```

Run Codex baseline-vs-skill evaluation:

```bash
python evals/run_ab_codex.py --model <model> --reasoning medium --limit 20
```

Configured model/reasoning values are recorded separately from observed runtime values. If runtime observation is unavailable, it remains `unknown`.

## What's new in v1.3

v1.3 moves further from keyword/window heuristics toward context-aware relations and evidence-based edit decisions:

- context-aware semantic sentinels;
- Fidelity Relation Graph;
- Editorial Gain Gate;
- semantic repetition analysis;
- numeral semantics separated from presentation;
- voice tolerance bands;
- boundary-aware locale guard;
- persistent document ledger;
- schema-based bibliography audit;
- run provenance;
- benchmark matrix and release gates;
- explainable edit trail.

<details>
<summary><strong>Repository structure</strong></summary>

```text
.agents/skills/arab-writer/
├── SKILL.md
├── agents/openai.yaml
├── references/
└── scripts/
    ├── fidelity_graph.py
    ├── semantic_sentinels.py
    ├── numeral_policy.py
    ├── editorial_gain.py
    ├── semantic_repetition.py
    ├── voice_profile.py
    ├── locale_guard.py
    ├── document_ledger.py
    ├── bibliography_schema.py
    ├── edit_trail.py
    ├── run_provenance.py
    ├── gec_adjudicator.py
    └── qa_pair.py

evals/
├── benchmark_matrix.json
├── benchmark_matrix.py
├── run_ab_codex.py
└── ...

tools/
└── release_gate.py
```

</details>

## Evaluation philosophy

A quality claim should be supported by more than a green CI run. The project is structured to combine:

- deterministic fidelity checks;
- multiple domains, tasks, and Arabic registers;
- benchmark evidence where licensing permits;
- adversarial regression cases;
- blind human review when evaluating actual writing quality.

More detail:

- `docs/DESIGN.md`
- `docs/EVALUATION.md`
- `docs/V130_ACCEPTANCE.md`

## Contributing

Bug reports and difficult real-world Arabic examples are particularly useful — especially cases where an edit sounds better but changes meaning, evidence, modality, terminology, or voice.

See `CONTRIBUTING.md` for contribution guidance and `SECURITY.md` for security reporting.

## License

MIT License.