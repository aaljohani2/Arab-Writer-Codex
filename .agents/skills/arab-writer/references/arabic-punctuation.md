# Arabic Punctuation Core

Use this reference for Arabic proofreading when punctuation affects sentence structure, reading, or fidelity. It is an operational synthesis of historical and modern Arabic punctuation guidance.

The goal is not to maximize punctuation density. The goal is to distinguish **mechanical defects**, **structural punctuation needs**, and **editorial variants**.

## Governing principle

Punctuation has three decision levels:

1. **D1 — deterministic/mechanical**
   - a direct question ends with an appropriate question mark;
   - paired marks such as quotation marks and parentheses are balanced;
   - accidental repeated terminal marks are repaired;
   - Arabic punctuation shape/spacing is normalized only when the document or task establishes that house style.

2. **S2 — structural/contextual**
   - punctuation should reveal a relation already present in the syntax: announced enumeration, explanation, definition, or staged division;
   - more than one separator strength may be defensible;
   - correct the structural boundary, but do not force one stylistic variant when several preserve the same relation.

3. **J3 — editorial/judgment**
   - comma versus semicolon between closely related clauses;
   - semicolon versus comma in some causal relations;
   - colon versus dash in some explanatory relations;
   - punctuation density in heritage prose;
   - other choices that change pause strength without repairing a real defect.

In proofreading, fix D1. Fix S2 when the structure is materially under-signalled or the current mark encodes the wrong relation. Preserve J3 unless the user supplied a house style or explicitly asked for punctuation normalization.

## Discovery pass

Before returning punctuation unchanged, scan for:

- direct interrogatives;
- unmatched quotation marks, parentheses, brackets, or other paired delimiters;
- duplicated terminal punctuation;
- announced lists or divisions such as “ثلاثة أقسام”، “وجهان”، “مرحلتان”، “الآتي”;
- a summary noun or phrase followed by its explanation or definition;
- long inline enumerations whose boundaries are hard to recover;
- causal or contrastive relations where a separator already exists;
- punctuation inside protected values, citations, URLs, code, formulas, identifiers, or quotations.

Do not make a punctuation edit until you can state which relation it reveals or which mechanical defect it repairs.

## 1. Direct questions

A genuine direct question in modern Arabic prose normally ends with `؟`.

Fresh examples:

- `هل اكتملت المراجعة؟`
- `متى يبدأ التسجيل؟`

Do not add a question mark merely because the sentence contains a request for information expressed imperatively:

- `اذكر أسباب القرار.`

Distinguish direct interrogation from reported or embedded questioning.

## 2. Paired punctuation

Quotation marks, parentheses, brackets, and similar paired signs should be balanced when the text clearly opens a pair.

Fresh examples:

- `قال الباحث: «النتيجة تحتاج إلى تحقق».`
- `ارتفعت النسبة (وفق التعريف الجديد).`

When repairing a missing partner:

- preserve the quoted wording;
- preserve protected literals;
- make the smallest pairing repair;
- do not silently modernize the quotation mark style unless the document establishes one.

The exact placement of a full stop relative to a closing quotation mark can be house-style sensitive. Treat pairing itself as deterministic; treat style-specific placement as a separate decision.

## 3. Accidental repetition and ellipsis

Repair accidental duplicate terminal marks such as `..` when context does not indicate intentional omission or a recognized ellipsis.

Do not collapse:

- a deliberate ellipsis `...`;
- punctuation used in quoted historical material;
- intentional expressive punctuation in a mode where voice preservation matters.

Proofreading should distinguish a typing duplicate from a meaningful mark.

## 4. Arabic comma and spacing

In Arabic prose, the Arabic comma `،` is the normal comma when the document follows an Arabic punctuation house style.

Check:

- no unintended space before punctuation;
- appropriate space after punctuation when prose continues;
- accidental Latin comma `,` in an otherwise Arabic punctuation system.

Do not normalize commas inside URLs, code, identifiers, formulas, citations, or official foreign names.

Do not infer a house style from one isolated mark. If the source consistently uses another convention and the user did not ask for normalization, preserve it unless readability is impaired.

## 5. Announced enumeration and division

A phrase that explicitly announces a set is structurally different from the members of that set.

Common signals include:

- `أقسامه أربعة`
- `للخطة مساران`
- `تمر العملية بثلاث مراحل`
- `النتائج الآتية`

When the announcing clause is complete and the following material supplies its members, a colon is the clearest modern structural marker in many Arabic writing guides.

Fresh examples:

- `للبرنامج ثلاثة مسارات: التدريب، والبحث، والشراكات.`
- `تمر المراجعة بمرحلتين: الفحص الأولي، ثم التحقق النهائي.`

### Separator strength inside the list

Between short parallel members, comma is often sufficient.

Between longer members that contain internal commas or have greater syntactic independence, a semicolon may improve structure.

Therefore:

- the **announcement → list** boundary can be a high-confidence S2 correction;
- the **member → member** separator may remain editorial when both comma and semicolon are clear.

Do not rewrite lexical content merely to create a list.

## 6. Explanation after a summary expression

When a complete summary expression is immediately followed by material that defines, explains, or specifies it, punctuation should expose that explanatory relation.

Fresh examples:

- `السبب الرئيس واحد: ضعف التحقق المسبق.`
- `الخيار الأنسب واضح: تأجيل الإطلاق حتى اكتمال الاختبار.`

A colon is often appropriate when the second part directly answers “what is it?” or “what does that summary mean?”.

A comma plus a connective may also be acceptable in some constructions:

- `النتيجة واحدة، وهي انخفاض زمن الانتظار.`

A dash can be a stylistic alternative in some modern prose.

### Proofreading decision

If the text has **no boundary at all** and the explanation can be misread as ordinary continuation, add a structural separator.

If the text already has a defensible explanatory marker, do not replace it merely to prefer another style.

## 7. Colon after reporting or introductory wording

Modern Arabic guidance commonly uses the colon after reporting verbs or introductory phrases when what follows is the reported content, and between a general item and its detailed divisions.

Fresh examples:

- `قال المتحدث: إن التنفيذ سيبدأ غدًا.`
- `تنقسم المخاطر إلى نوعين: تشغيلية، ومالية.`

Do not apply the colon mechanically after every occurrence of `قال` or every noun phrase. Confirm that the second part is actually presented as content, explanation, or division.

## 8. Comma versus semicolon

The comma commonly joins clauses that remain closely connected in meaning.

The semicolon can mark a stronger internal boundary, and modern guides frequently use it where the second clause gives a reason, result, or tightly linked explanation.

Fresh examples:

- `اكتمل الفحص، وبدأت مرحلة التحقق.`
- `أُجّل الإطلاق؛ لأن الاختبار لم يكتمل.`

But punctuation strength is partly editorial. In pure proofreading:

- do not upgrade every comma to a semicolon;
- do not downgrade every semicolon to a comma;
- preserve a clear existing relation unless the mark actively misleads or a house style requires normalization.

## 9. Heritage-sensitive punctuation

Classical Arabic texts predate the modern punctuation system in its current form, and modern editions may differ in how densely they punctuate inherited prose.

When editing heritage-sensitive prose:

- preserve a defensible sparse or strong pause if meaning remains clear;
- do not modernize every clause boundary;
- use punctuation to clarify structure, not to make the text look contemporary;
- keep quotations from sacred or historical texts exact when they are protected.

A modern punctuation layer may be added when the user explicitly requests a modernized edition or a house style. That is a different task from minimal proofreading.

## 10. Protected spans

Punctuation edits must not alter:

- numbers, percentages, units, dates, currencies;
- URLs, email addresses, identifiers;
- code, formulas, file paths;
- citation strings;
- exact quotations unless the user explicitly authorizes editing inside them.

If punctuation immediately adjacent to a protected span is defective, repair the boundary without changing the protected token.

## 11. Minimality gate

Before accepting a punctuation change, ask:

1. Is this a D1 mechanical defect?
2. If not, does the mark reveal a real syntactic/semantic boundary that is currently missing or misleading?
3. Is the proposed replacement uniquely required, or merely one acceptable editorial variant?
4. Does the edit preserve every protected literal and quotation?
5. Would leaving the source unchanged still be clear and conventionally acceptable?

If 1 is yes, fix it.
If 2 is yes and 3 is no, use the smallest S2 repair and avoid overclaiming uniqueness.
If 3 is “editorial variant only”, preserve in proofread mode unless a house style is specified.
If 5 is yes and there is no D1/S2 defect, do not edit.

## 12. Final punctuation gate

Before returning a proofreading result:

- verify paired signs are balanced;
- verify direct questions and terminal marks;
- verify announced enumerations and explanatory boundaries;
- verify list separators do not obscure hierarchy;
- verify you did not change a valid J3 choice merely for preference;
- verify protected spans remain exact.

## Reference anchors

### Historical systematic reference

- أحمد زكي باشا — `الترقيم وعلاماته في اللغة العربية` (1912). A foundational systematic Arabic treatment of punctuation and degrees of pause.

### Modern Arabic writing guidance

- كلية العلوم الإنسانية والاجتماعية، جامعة الملك سعود — `أساسيات الكتابة العربية`. It presents common modern uses including the comma between connected clauses and list members, the semicolon in causal relations, the colon before divisions/definitions and after reporting expressions, the question mark for direct questions, quotation marks, and parentheses.
- مجمع الملك سلمان العالمي للغة العربية — studies of Arabic writing-system variation and punctuation. Use these as evidence that punctuation practice has a historical and editorial dimension rather than treating every separator choice as uniquely grammatical.

## Evaluation boundary

Do not copy evaluation IDs, source sentences, gold answers, acceptable-output lists, or case-specific rationales into runtime knowledge.

Punctuation quality claims should separate:

- deterministic mechanical accuracy;
- structural clarity;
- editorial/style adjudication;
- preservation and fidelity.

A single exact-gold punctuation score is insufficient when multiple conventional outputs are valid.
