# Arabic Linguistic Challenge Set v1 — Design

Status: **AUTHORED — 70/70 cases; structural validation added; manual linguistic review pending**  
Branch: `feature/v1.4-arabic-linguistic-core`

## Purpose

The existing 64-case pilot is useful for controlled A/B measurement, but GPT-6.1 Sol already reaches a very high substantive score on it. Challenge Set v1 is a harder, source-grounded benchmark intended to expose real gaps in Arabic linguistic judgment before the v1.4 linguistic knowledge layer is added.

This benchmark measures **Arabic linguistic handling**, not subject-matter expertise. A case may be drawn from fiqh, hadith commentary, creed, usul al-fiqh, literature, rhetoric, history, classical medicine, science, health, engineering, economics, education, AI, environment, or public policy, but the scored issue is linguistic rather than disciplinary.

## Completed composition

Total: **70 cases**

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

Era balance:

| Era | Cases |
|---|---:|
| Classical / heritage | 35 |
| Modern / contemporary | 35 |
| **Total** | **70** |

Every linguistic family contains both classical and modern cases.

Corpus files:

- `evals/challenge/challenge_v1_batch01_a.jsonl`
- `evals/challenge/challenge_v1_batch01_b.jsonl`
- `evals/challenge/challenge_v1_batch01_c.jsonl`
- `evals/challenge/challenge_v1_batch01_d.jsonl`
- `evals/challenge/challenge_v1_batch02_a.jsonl`
- `evals/challenge/challenge_v1_batch02_b.jsonl`
- `evals/challenge/challenge_v1_batch02_c.jsonl`
- `evals/challenge/challenge_v1_batch02_d.jsonl`
- `evals/challenge/challenge_v1_batch02_e.jsonl`

## Source policy

Each case carries explicit provenance through `provenance.source_id`, resolved in `evals/challenge/source_registry.json`.

The registry now includes classical and modern sources across several registers. Classical sources include, among others:

- ابن خلدون — `المقدمة`
- الجاحظ — `البيان والتبيين`
- الشافعي — `الرسالة`
- النووي — `المنهاج شرح صحيح مسلم`
- ابن قدامة — `المغني`
- ابن رشد — `بداية المجتهد`
- الغزالي — `إحياء علوم الدين`
- عبد القاهر الجرجاني — `دلائل الإعجاز`
- ابن تيمية — `العقيدة الواسطية`
- الشاطبي — `الموافقات`
- ابن سينا — `القانون في الطب`

Modern sources include literary/intellectual books and institutional Arabic from WHO, KAUST, the United Nations, Saudi Vision 2030, GASTAT, the Saudi Central Bank, UNEP, ITU, and UNESCO.

The benchmark does **not** score whether a medical, legal, theological, scientific, economic, or policy claim is substantively correct. Domain material supplies register, terminology, sentence length, and syntactic pressure only.

### Sacred-text safeguard

Do not manufacture an error inside:

- a Qur'anic verse;
- a Prophetic hadith presented as a direct quotation.

Such text may appear only as a protected literal in fidelity/preservation cases. Correction cases in Islamic domains target the prose of commentators, jurists, theologians, historians, or adapted authorial prose around the quotation.

### Modern-source safeguard

For modern copyrighted or institutional publications:

- use domain, register, and structural patterns;
- adapt the challenge sentence rather than reproduce long verbatim passages;
- preserve short quotations only when the quotation itself is the fidelity target.

## Challenge design

Cases emphasize one or more of these axes:

1. **Correct but tempting to edit** — unusual but licensed Arabic that must be preserved.
2. **Single hidden defect** — one grammatical, morphological, orthographic, numerical, agreement, or punctuation defect inside otherwise polished prose.
3. **Contextual ambiguity** — correction depends on antecedent, scope, register, or construction.
4. **Long-distance dependency** — agreement, case, or reference is separated from its trigger.
5. **Minimality** — the correct answer fixes the defect without stylistic rewriting.
6. **Fidelity** — numbers, technical terms, quotations, and established variants remain protected.
7. **Classical/modern register separation** — a classical structure is not “modernized” merely because it is unfamiliar.
8. **Domain pressure** — terminology and sentence length make the linguistic judgment harder without requiring specialist knowledge.

Examples of intentionally difficult phenomena in the completed set include:

- delayed nouns of `إن` and `كان` after fronted prepositional predicates;
- semantic agreement with `من` and collective nouns;
- `من` الزائدة after negation;
- `لا` النافية للجنس with an annexed noun;
- dual nun deletion in idafa;
- passive ditransitives and deputy subjects;
- weak verbs under jussive, imperative, and prohibition;
- maqsur, manqus, and mamdud noun alternations;
- compound-number gender/case and digit-form tamyiz;
- accepted orthographic and modern-usage variants that must not be overcorrected;
- punctuation-only edits in dense argumentative and institutional prose.

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

`source`, `expected`, and `protected` remain the scoring authority. `provenance` documents where the register or structural pressure came from; it is not passed to the model during the A/B task.

## Rule references

Canonical adjudication references include:

- `كتاب سيبويه`
- `مغني اللبيب` — ابن هشام
- `شرح ابن عقيل على ألفية ابن مالك`
- `جامع الدروس العربية` — مصطفى الغلاييني
- `النحو الوافي` — عباس حسن
- `شذا العرف في فن الصرف` — أحمد الحملاوي
- `الترقيم وعلاماته في اللغة العربية` — أحمد زكي باشا
- `الإملاء والترقيم في الكتابة العربية` — عبد العليم إبراهيم
- `قرارات مجمع اللغة العربية بالقاهرة` where an accepted modern orthographic variant is the point of the case
- `معجم الصواب اللغوي` and `معجم اللغة العربية المعاصرة` for specifically modern usage/derivation controls

Where a matter genuinely admits multiple standard forms, the case is assigned to `AMB`/`PRESERVE` rather than forcing one editorial preference as a universal error.

## Structural validation

`tests/test_challenge_v1.py` now validates the entire set, including:

- 9 challenge JSONL files;
- exactly 70 unique case IDs;
- exact family targets;
- exact 35/35 classical-modern balance;
- classical and modern coverage inside every family;
- required schema and provenance;
- registry traceability;
- correct `PRESERVE` and `CORRECT` source/expected relationships;
- survival of protected literals.

## Leakage rule

Challenge files live under `evals/challenge/`. They are evaluation artifacts and **must not** be copied into `.agents/skills/arab-writer/references/` or exposed to the candidate during normal model execution.

The v1.4 knowledge layer must be built from independent linguistic references, not from challenge answers.

## Remaining gate before controlled baseline

Authorship is complete, but the set should not yet be called final/baseline-ready until it receives a second linguistic adjudication pass focused on:

- whether each gold correction is uniquely defensible;
- whether any `AMB` case accidentally encodes a school preference as mandatory;
- whether punctuation cases allow materially equivalent alternatives that the exact scorer would unfairly reject;
- whether diacritics are carrying a distinction that should instead be represented by letters or syntax;
- whether provenance anchors accurately describe the source/register used;
- whether any case is still too easy to contribute to a hard-set benchmark.

After that review passes, run a controlled v1.3 A/B baseline on all 70 cases with the same pinned model/reasoning and skill-isolation protocol used for the 64-case pilot.
