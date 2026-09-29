# Arab Writer for Codex

**Arab Writer v1.3** is a Codex-native Arabic writing and editing skill built around one rule:

> Improve the writing without silently changing the evidence.

It combines Arabic editing, context-aware fidelity checks, editorial-depth control, voice/locale preservation, long-document consistency, and reproducible evaluation.

This repository is Codex-first.

## What changed in v1.3

v1.3 moves from keyword/window heuristics toward **context-aware relations and evidence-based edit decisions**:

1. **Context-aware semantic sentinels** — distinguishes cases such as `قد أعلنت` from `قد تعلن`, and containment from guarantee language.
2. **Fidelity Relation Graph** — protects `measure/entity → value → time/status/unit`, not just token presence.
3. **Editorial Gain Gate** — a safe rewrite is retained only when its benefit justifies fidelity/voice/change cost.
4. **Semantic Repetition v2** — combines lexical, n-gram and proposition signals and classifies likely duplicate vs elaboration/summary.
5. **Numeral semantics vs presentation** — numeric value is protected; presentation can be normalized only under an explicit policy with semantic equivalence.
6. **Voice tolerance bands** — does not blindly maximize similarity; acceptable drift can be justified by real clarity/correctness gain.
7. **Boundary-aware locale guard** — avoids substring errors such as treating `مرة أخرى` as proof of dialect.
8. **Persistent document ledger** — carries terms, acronyms and protected relations across chapters.
9. **Schema-based bibliography audit** — missing metadata stays missing; no invented years/URLs/DOIs.
10. **Run provenance** — configured model/reasoning are separated from actually observed runtime settings.
11. **Benchmark matrix + release gates** — prevents a single Mobily-style case from becoming the whole evidence base.
12. **Explainable edit trail** — paragraph-level changes can be reviewed with reasons/signals and required verification.

## Core operating loop

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

### Four verification passes

- **Pass A — Edit**
- **Pass B — Arabic + fidelity audit**
- **Pass C — missed opportunities**
- **Pass D — what became worse because of the edit?**

The fourth pass is specifically intended to reduce over-editing after v1.2.1 fixed much of the earlier under-editing.

## Codex-native structure

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

## Install

In Codex:

```text
$skill-installer
```

Install from:

```text
https://github.com/aaljohani2/Arab-Writer-Codex/tree/main/.agents/skills/arab-writer
```

Or copy `.agents/skills/arab-writer` to:

```text
$HOME/.agents/skills/arab-writer
```

## Use

```text
$arab-writer
راجع هذا الفصل تحريرياً على مستوى rewrite + naturalize + voice-lock مع High Fidelity.
```

Proofreading only:

```text
$arab-writer
دقق هذا النص لغويًا فقط. لا تعِد صياغة الجمل الصحيحة.
```

High-fidelity financial/legal editing:

```text
$arab-writer
حرر النص مع الحفاظ على الأرقام وعلاقاتها بالفترات والبنود، وقوة الادعاء والشروط والاستثناءات.
```

## Numeric policy

Available policies:

- `preserve-exact`
- `normalize-arabic`
- `normalize-western`
- `document-consistent`

Example:

```text
٢٥,١٩1
```

may be normalized in presentation only when the semantic value is proven unchanged.

## High-fidelity QA

```bash
python .agents/skills/arab-writer/scripts/qa_pair.py before.txt after.txt
python .agents/skills/arab-writer/scripts/fidelity_graph.py before.txt after.txt
python .agents/skills/arab-writer/scripts/editorial_gain.py before.txt after.txt
```

These scripts produce review signals, not automatic semantic proof.

## Evaluation

Validate deterministic software behavior:

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

The benchmark records **configured** model/reasoning separately from **observed** runtime values. If runtime observation is unavailable, it stays `unknown`.

## Evidence policy

CI does **not** prove better writing.

A quality claim requires multiple domains/tasks/locales, deterministic fidelity checks, Arabic/external benchmark evidence where licensed, and blind human review.

See:
- `docs/DESIGN.md`
- `docs/EVALUATION.md`
- `docs/V130_ACCEPTANCE.md`

## License

MIT.
