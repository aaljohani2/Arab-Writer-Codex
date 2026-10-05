#!/usr/bin/env python3
"""Score Arab Writer v1.4 linguistic-core A/B outputs.

The scorer separates strict minimality from substantive linguistic correctness:

- exact metrics preserve the authored gold/source after NFC + whitespace/code-fence
  normalization;
- substantive metrics additionally ignore optional Arabic harakat (tanwin, short
  vowels, shadda, sukun, dagger alif), so an otherwise correct correction is not
  marked linguistically wrong merely because the model added optional diacritics;
- preservation remains strict for minimal-edit evaluation, with a separate
  substantive-preservation metric to distinguish harmless surface additions from
  real textual changes;
- protected literals remain a separate fidelity signal.

A non-gold rewrite is not automatically called a grammatical error. Substantive
mismatches still require adjudication where multiple correct outputs are possible.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ARMS = ("baseline", "candidate")
PRESERVE_ACTIONS = {"PRESERVE", "FLAG"}
OPTIONAL_DIACRITICS_RE = re.compile(r"[\u064B-\u0652\u0670]")


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text or "").strip()
    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()
    return re.sub(r"\s+", " ", text)


def strip_optional_diacritics(text: str) -> str:
    """Remove optional harakat while preserving letters, punctuation, and spacing."""
    text = unicodedata.normalize("NFC", text or "")
    return OPTIONAL_DIACRITICS_RE.sub("", text)


def normalize_substantive(text: str) -> str:
    return strip_optional_diacritics(normalize(text))


def surface_only_difference(a: str, b: str) -> bool:
    """True when strict normalized strings differ only by optional harakat."""
    na = normalize(a)
    nb = normalize(b)
    return na != nb and normalize_substantive(na) == normalize_substantive(nb)


def load_results(path: Path) -> list[dict]:
    rows = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid JSONL at {path}:{line_no}: {exc}") from exc
        if "case" not in row or "id" not in row:
            raise SystemExit(f"missing case/id at {path}:{line_no}")
        rows.append(row)
    return rows


def score_arm(rows: list[dict], arm: str) -> dict:
    overall = Counter()
    families: dict[str, Counter] = defaultdict(Counter)
    mismatches = []

    for row in rows:
        case = row["case"]
        result = row.get(arm, {})
        raw_output = result.get("output", "")
        raw_expected = case.get("expected", case.get("source", case.get("input", "")))
        raw_source = case.get("source", case.get("input", ""))

        output = normalize(raw_output)
        expected = normalize(raw_expected)
        source = normalize(raw_source)
        output_sub = normalize_substantive(raw_output)
        expected_sub = normalize_substantive(raw_expected)
        source_sub = normalize_substantive(raw_source)

        family = case.get("family", "UNCLASSIFIED")
        action = case.get("action", "")
        case_type = case.get("case_type", "")
        returncode = result.get("returncode", 0)

        overall["cases"] += 1
        families[family]["cases"] += 1
        if returncode == 0:
            overall["runtime_ok"] += 1
            families[family]["runtime_ok"] += 1

        exact = output == expected
        substantive = output_sub == expected_sub
        if exact:
            overall["exact_gold"] += 1
            families[family]["exact_gold"] += 1
        if substantive:
            overall["substantive_gold"] += 1
            families[family]["substantive_gold"] += 1

        if action == "CORRECT":
            overall["correction_cases"] += 1
            families[family]["correction_cases"] += 1
            if exact:
                overall["exact_correction_success"] += 1
                families[family]["exact_correction_success"] += 1
            if substantive:
                overall["correction_success"] += 1
                families[family]["correction_success"] += 1

        preservation_case = case_type == "no_change" or action in PRESERVE_ACTIONS
        if preservation_case:
            overall["preservation_cases"] += 1
            families[family]["preservation_cases"] += 1
            strict_preserved = output == source
            substantive_preserved = output_sub == source_sub
            if strict_preserved:
                overall["source_preserved"] += 1
                families[family]["source_preserved"] += 1
            else:
                overall["false_change"] += 1
                families[family]["false_change"] += 1
            if substantive_preserved:
                overall["substantive_source_preserved"] += 1
                families[family]["substantive_source_preserved"] += 1
            else:
                overall["substantive_false_change"] += 1
                families[family]["substantive_false_change"] += 1
            if surface_only_difference(raw_output, raw_source):
                overall["diacritic_only_change"] += 1
                families[family]["diacritic_only_change"] += 1

        protected = case.get("protected", [])
        if protected:
            overall["protected_cases"] += 1
            families[family]["protected_cases"] += 1
            retained = all(normalize(str(token)) in output for token in protected)
            if retained:
                overall["protected_retained"] += 1
                families[family]["protected_retained"] += 1
            else:
                overall["protected_failure"] += 1
                families[family]["protected_failure"] += 1

        if not exact:
            mismatches.append({
                "id": row["id"],
                "family": family,
                "action": action,
                "case_type": case_type,
                "source": raw_source,
                "expected": case.get("expected", ""),
                "output": raw_output,
                "returncode": returncode,
                "substantive_gold_match": substantive,
                "difference_class": (
                    "optional_diacritics_only"
                    if surface_only_difference(raw_output, raw_expected)
                    else "substantive_or_other"
                ),
            })

    def report(c: Counter) -> dict:
        cases = c["cases"]
        correction_cases = c["correction_cases"]
        preservation_cases = c["preservation_cases"]
        protected_cases = c["protected_cases"]
        return {
            "cases": cases,
            "runtime_success_rate": round(c["runtime_ok"] / cases, 4) if cases else None,
            "exact_gold_rate": round(c["exact_gold"] / cases, 4) if cases else None,
            "substantive_gold_rate": round(c["substantive_gold"] / cases, 4) if cases else None,
            "correction_cases": correction_cases,
            "correction_accuracy": (
                round(c["correction_success"] / correction_cases, 4)
                if correction_cases else None
            ),
            "exact_correction_accuracy": (
                round(c["exact_correction_success"] / correction_cases, 4)
                if correction_cases else None
            ),
            "preservation_cases": preservation_cases,
            "correct_source_preservation": (
                round(c["source_preserved"] / preservation_cases, 4)
                if preservation_cases else None
            ),
            "substantive_source_preservation": (
                round(c["substantive_source_preserved"] / preservation_cases, 4)
                if preservation_cases else None
            ),
            "false_change_rate": (
                round(c["false_change"] / preservation_cases, 4)
                if preservation_cases else None
            ),
            "substantive_false_change_rate": (
                round(c["substantive_false_change"] / preservation_cases, 4)
                if preservation_cases else None
            ),
            "diacritic_only_changes": c["diacritic_only_change"],
            "diacritic_only_change_rate": (
                round(c["diacritic_only_change"] / preservation_cases, 4)
                if preservation_cases else None
            ),
            "protected_cases": protected_cases,
            "protected_literal_retention": (
                round(c["protected_retained"] / protected_cases, 4)
                if protected_cases else None
            ),
            "protected_failures": c["protected_failure"],
        }

    return {
        "summary": report(overall),
        "by_family": {
            family: report(counts) for family, counts in sorted(families.items())
        },
        "mismatches": mismatches,
    }


def compare(baseline: dict, candidate: dict) -> dict:
    b = baseline["summary"]
    c = candidate["summary"]

    def delta(key: str):
        if b.get(key) is None or c.get(key) is None:
            return None
        return round(c[key] - b[key], 4)

    return {
        "exact_gold_delta": delta("exact_gold_rate"),
        "substantive_gold_delta": delta("substantive_gold_rate"),
        "correction_accuracy_delta": delta("correction_accuracy"),
        "exact_correction_accuracy_delta": delta("exact_correction_accuracy"),
        "source_preservation_delta": delta("correct_source_preservation"),
        "substantive_source_preservation_delta": delta(
            "substantive_source_preservation"
        ),
        "false_change_delta": delta("false_change_rate"),
        "substantive_false_change_delta": delta("substantive_false_change_rate"),
        "diacritic_only_change_rate_delta": delta("diacritic_only_change_rate"),
        "protected_retention_delta": delta("protected_literal_retention"),
    }


def score(rows: list[dict]) -> dict:
    baseline = score_arm(rows, "baseline")
    candidate = score_arm(rows, "candidate")
    return {
        "schema": "arab-writer-linguistic-pilot-score-v2",
        "cases": len(rows),
        "baseline": baseline,
        "candidate": candidate,
        "delta_candidate_minus_baseline": compare(baseline, candidate),
        "interpretation_note": (
            "Exact metrics measure minimality. Substantive metrics ignore optional Arabic "
            "harakat only; they do not ignore letters, punctuation, wording, numbers, or "
            "word order. A substantive mismatch is still an evaluation mismatch rather "
            "than automatic proof of grammatical error; use blind human review where "
            "multiple correct formulations are possible."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("results", help="A/B JSONL produced by evals/run_ab_codex.py")
    ap.add_argument("--out", help="Optional JSON report path")
    args = ap.parse_args()

    report = score(load_results(Path(args.results)))
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
