#!/usr/bin/env python3
"""Score punctuation holdouts without collapsing style variants into hard failures.

This scorer is intentionally separate from score_linguistic_pilot.py so historical
Challenge Set v1 results remain stable. It supports punctuation cases with:

- pun_class: PUN-D1-DETERMINISTIC | PUN-S2-STRUCTURAL | PUN-J3-EDITORIAL
- acceptable_outputs: zero or more additional accepted strings
- adjudication_required: bool

D1 cases can fail automatically when no accepted output matches. S2/J3 unmatched
outputs are routed to human adjudication rather than called incorrect automatically.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from score_linguistic_pilot import normalize, normalize_substantive

ARMS = ("baseline", "candidate")
PUN_CLASSES = {
    "PUN-D1-DETERMINISTIC",
    "PUN-S2-STRUCTURAL",
    "PUN-J3-EDITORIAL",
}


def load_results(path: Path) -> list[dict]:
    rows = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid JSONL at {path}:{line_no}: {exc}") from exc
        case = row.get("case")
        if not isinstance(case, dict) or not row.get("id"):
            raise SystemExit(f"missing case/id at {path}:{line_no}")
        if case.get("pun_class") not in PUN_CLASSES:
            raise SystemExit(
                f"invalid or missing pun_class for {row.get('id')}: {case.get('pun_class')!r}"
            )
        rows.append(row)
    return rows


def accepted_forms(case: dict) -> list[str]:
    forms = []
    expected = case.get("expected")
    if expected:
        forms.append(expected)
    for value in case.get("acceptable_outputs", []) or []:
        if value and value not in forms:
            forms.append(value)
    return forms


def score_arm(rows: list[dict], arm: str) -> dict:
    counts = Counter()
    items = []

    for row in rows:
        case = row["case"]
        result = row.get(arm, {})
        raw_output = result.get("output", "")
        output = normalize(raw_output)
        output_sub = normalize_substantive(raw_output)
        forms = accepted_forms(case)
        accepted_exact = any(output == normalize(form) for form in forms)
        accepted_substantive = any(
            output_sub == normalize_substantive(form) for form in forms
        )
        pun_class = case["pun_class"]
        returncode = result.get("returncode", 0)

        counts["cases"] += 1
        if returncode == 0:
            counts["runtime_ok"] += 1
        if accepted_exact:
            counts["accepted_exact"] += 1
        if accepted_substantive:
            counts["accepted_substantive"] += 1

        disposition = "PASS_ACCEPTED"
        if not accepted_substantive:
            if pun_class == "PUN-D1-DETERMINISTIC" and not case.get(
                "adjudication_required", False
            ):
                disposition = "FAIL_DETERMINISTIC"
                counts["deterministic_fail"] += 1
            else:
                disposition = "NEEDS_HUMAN_REVIEW"
                counts["needs_human_review"] += 1
        else:
            counts["pass_accepted"] += 1

        source = normalize(case.get("source", case.get("input", "")))
        if output == source:
            counts["source_preserved"] += 1

        protected = case.get("protected", []) or []
        if protected:
            counts["protected_cases"] += 1
            retained = all(normalize(str(token)) in output for token in protected)
            if retained:
                counts["protected_retained"] += 1
            else:
                counts["protected_failure"] += 1

        items.append(
            {
                "id": row["id"],
                "pun_class": pun_class,
                "output": raw_output,
                "accepted_exact": accepted_exact,
                "accepted_substantive": accepted_substantive,
                "disposition": disposition,
                "returncode": returncode,
            }
        )

    total = counts["cases"]
    protected_cases = counts["protected_cases"]
    return {
        "summary": {
            "cases": total,
            "runtime_success_rate": round(counts["runtime_ok"] / total, 4)
            if total
            else None,
            "accepted_exact_rate": round(counts["accepted_exact"] / total, 4)
            if total
            else None,
            "accepted_substantive_rate": round(
                counts["accepted_substantive"] / total, 4
            )
            if total
            else None,
            "pass_accepted": counts["pass_accepted"],
            "deterministic_failures": counts["deterministic_fail"],
            "needs_human_review": counts["needs_human_review"],
            "source_preserved": counts["source_preserved"],
            "protected_cases": protected_cases,
            "protected_literal_retention": (
                round(counts["protected_retained"] / protected_cases, 4)
                if protected_cases
                else None
            ),
            "protected_failures": counts["protected_failure"],
        },
        "items": items,
    }


def score(rows: list[dict]) -> dict:
    return {
        "schema": "arab-writer-punctuation-holdout-score-v1",
        "cases": len(rows),
        "baseline": score_arm(rows, "baseline"),
        "candidate": score_arm(rows, "candidate"),
        "interpretation_note": (
            "Accepted outputs may contain multiple punctuation variants. Unmatched "
            "S2/J3 outputs are routed to human adjudication rather than treated as "
            "automatic correctness failures. D1 automatic failures are reserved for "
            "cases authored as unique deterministic punctuation corrections."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("results", help="A/B JSONL produced by evals/run_ab_codex.py")
    ap.add_argument("--out", help="optional JSON report path")
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
