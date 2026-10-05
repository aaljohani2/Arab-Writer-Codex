# Arabic Linguistic Challenge Set v1 — Design

Status: **DRAFT — batch 01 authored (20/70 cases)**  
Branch: `feature/v1.4-arabic-linguistic-core`

## Purpose

The existing 64-case pilot is useful for controlled A/B measurement, but GPT-6.1 Sol already reaches a very high substantive score on it. Challenge Set v1 is a harder, source-grounded benchmark intended to expose real gaps in Arabic linguistic judgment before the v1.4 linguistic knowledge layer is added.

This benchmark measures **Arabic linguistic handling**, not subject-matter expertise. A case may be drawn from fiqh, hadith commentary, theology, literature, history, science, health, engineering, or public policy, but the scored issue is grammatical, morphological, orthographic, punctuation-related, agreement-related, numerical, or editorial/ambiguity judgment.

## Target composition

Target total: **70 cases**

| Family | Target |
|---|---:|
| SYN | 20 |
| MOR | 15 |
| NUM | 10 |
| AMB | 10 |
| AGR | 5 |
| ORT | 5 |
| PUN | 5 |
| **Total** | **70** |

Era balance target:

| Era | Target |
|---|---:|
| Classical / heritage | 35 |
| Modern / contemporary | 35 |

Batch 01 currently contributes 20 cases: 10 classical and 10 modern.

## Source policy

Each case must carry explicit provenance through `provenance.source_id`, resolved in `evals/challenge/source_registry.json`.

Allowed source domains include:

- Qur'anic exegesis, fiqh, usul al-fiqh, hadith commentary, creed, sira, and other Islamic scholarship;
- literary and rhetorical prose;
- history, sociology, philosophy, logic, and intellectual history;
- medicine, health policy, mathematics, engineering, computing, environment, and other scientific writing;
- education, economics, management, law, and public policy.

The benchmark does **not** score whether a medical, legal, theological, or scientific claim is substantively correct. Domain material supplies register, terminology, and syntactic pressure only.

### Sacred-text safeguard

Do not manufacture an error inside:
- a Qur'anic verse;
- a Prophetic hadith presented as a direct quotation.

Such text may appear only as a protected literal in fidelity/preservation cases. Correction cases in Islamic domains should target the prose of commentators, jurists, historians, or modern writers around the quotation.

### Modern-source safeguard

For modern copyrighted or institutional publications:
- use domain, register, and structural patterns;
- adapt the challenge sentence rather than reproducing long verbatim passages;
- preserve short quotations only when the quotation itself is the fidelity target.

## Challenge design

Cases should emphasize one or more of these axes:

1. **Correct but tempting to edit** — unusual but licensed Arabic that must be preserved.
2. **Single hidden defect** — one grammatical or morphological defect inside otherwise polished prose.
3. **Contextual ambiguity** — correction depends on antecedent, scope, register, or construction.
4. **Long-distance dependency** — agreement, case, or reference is separated from its trigger.
5. **Minimality** — the correct answer fixes the defect without stylistic rewriting.
6. **Fidelity** — numbers, technical terms, quotations, and established variants remain protected.
7. **Classical/modern register separation** — a classical structure is not “modernized” merely because it is unfamiliar.
8. **Domain pressure** — terminology and sentence length should make the linguistic judgment harder without requiring specialist knowledge.

## Case schema additions

In addition to the existing pilot fields, challenge cases include:

```json
{
  "difficulty": "hard",
  "challenge_axis": ["..."],
  "provenance": {
    "source_id": "...",
    "anchor": "...",
    "adaptation": "..."
  },
  "rule_source": {
    "work": "...",
    "author": "...",
    "topic": "..."
  }
}
```

`source`, `expected`, and `protected` remain the scoring authority for the benchmark. `provenance` documents where the register/structure came from; it is not passed to the model during the A/B task.

## Rule references

Canonical adjudication references may include:

- `كتاب سيبويه`
- `مغني اللبيب` — ابن هشام
- `شرح ابن عقيل على ألفية ابن مالك`
- `جامع الدروس العربية` — مصطفى الغلاييني
- `النحو الوافي` — عباس حسن
- `شذا العرف في فن الصرف` — أحمد الحملاوي
- `الترقيم وعلاماته في اللغة العربية` — أحمد زكي باشا
- `الإملاء والترقيم في الكتابة العربية` — عبد العليم إبراهيم

Where a matter is genuinely disputed or admits multiple standard forms, the case should be `AMB`/`PRESERVE` or receive explicit adjudication notes rather than forcing one school as universally correct.

## Leakage rule

Challenge files live under `evals/challenge/`. They are evaluation artifacts and **must not** be copied into `.agents/skills/arab-writer/references/` or exposed to the candidate during normal model execution.

The v1.4 knowledge layer must be built from independent linguistic references, not from challenge answers.

## Release gate for the challenge set

Do not call the set “baseline-ready” until all 70 cases:

- meet the target family and era allocation;
- have valid source IDs and rule-source metadata;
- pass deterministic schema tests;
- receive manual linguistic review;
- contain no unresolved disputed ruling disguised as deterministic gold;
- preserve sacred quotations and protected literals exactly;
- remain outside the skill runtime context.

Only then run the controlled v1.3 A/B baseline on Challenge Set v1.
