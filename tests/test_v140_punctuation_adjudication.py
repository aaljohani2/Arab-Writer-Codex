import importlib.util
import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / "evals"
SCORER_PATH = EVALS / "score_punctuation_holdout.py"
HOLDOUT_FILES = sorted(EVALS.glob("punctuation_holdout_v1_*.jsonl"))
HOLDOUT_SOURCES = EVALS / "punctuation_holdout_v1_sources.json"
CHALLENGE_SOURCES = EVALS / "challenge" / "source_registry.json"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def load_jsonl(paths):
    rows = []
    for path in paths:
        for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not raw.strip():
                continue
            try:
                rows.append(json.loads(raw))
            except json.JSONDecodeError as exc:
                raise AssertionError(f"invalid JSONL {path}:{line_no}: {exc}") from exc
    return rows


pun = load_module("score_punctuation_holdout_v140", SCORER_PATH)


class PunctuationHoldoutSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_jsonl(HOLDOUT_FILES)
        cls.source_registry = json.loads(HOLDOUT_SOURCES.read_text(encoding="utf-8"))
        cls.rule_sources = {s["id"]: s for s in cls.source_registry["rule_sources"]}
        challenge = json.loads(CHALLENGE_SOURCES.read_text(encoding="utf-8"))
        cls.context_sources = {s["id"]: s for s in challenge["sources"]}

    def test_holdout_has_two_files_and_eighteen_unique_cases(self):
        self.assertEqual(len(HOLDOUT_FILES), 2)
        self.assertEqual(len(self.rows), 18)
        ids = [row["id"] for row in self.rows]
        self.assertEqual(len(ids), len(set(ids)))

    def test_class_balance_is_six_each(self):
        self.assertEqual(
            Counter(row["pun_class"] for row in self.rows),
            Counter({
                "PUN-D1-DETERMINISTIC": 6,
                "PUN-S2-STRUCTURAL": 6,
                "PUN-J3-EDITORIAL": 6,
            }),
        )

    def test_period_balance_is_nine_nine(self):
        self.assertEqual(
            Counter(row["source_period"] for row in self.rows),
            Counter({"heritage": 9, "modern": 9}),
        )

    def test_preservation_and_variant_coverage(self):
        self.assertGreaterEqual(sum(row["action"] == "PRESERVE" for row in self.rows), 6)
        self.assertGreaterEqual(
            sum(bool(row.get("acceptable_outputs")) for row in self.rows), 4
        )
        self.assertGreaterEqual(
            sum("paired-mark" in row.get("tags", []) or row["rule"].startswith("PUN-PAIRED") for row in self.rows),
            2,
        )
        self.assertGreaterEqual(
            sum("enumeration" in row.get("tags", []) or "DIVISION" in row["rule"] for row in self.rows),
            4,
        )

    def test_required_fields_and_source_traceability(self):
        required = {
            "id", "family", "pun_class", "source_period", "rule", "status",
            "confidence", "severity", "case_type", "mode", "locale", "task",
            "input", "source", "expected", "acceptable_outputs", "action",
            "house_style", "adjudication_required", "protected", "rationale",
            "provenance", "rule_source", "difficulty", "challenge_axis", "tags",
        }
        for row in self.rows:
            with self.subTest(case=row["id"]):
                self.assertTrue(required.issubset(row))
                self.assertEqual(row["family"], "PUN")
                self.assertEqual(row["input"], row["source"])
                self.assertEqual(row["difficulty"], "hard")
                self.assertIn(row["provenance"]["source_id"], self.context_sources)
                self.assertIn(row["rule_source"]["id"], self.rule_sources)
                self.assertIsInstance(row["acceptable_outputs"], list)
                self.assertIsInstance(row["protected"], list)
                self.assertIsInstance(row["adjudication_required"], bool)

    def test_deterministic_cases_are_unique_gold_and_not_human_routed(self):
        for row in self.rows:
            if row["pun_class"] == "PUN-D1-DETERMINISTIC":
                with self.subTest(case=row["id"]):
                    self.assertEqual(row["action"], "CORRECT")
                    self.assertNotEqual(row["source"], row["expected"])
                    self.assertEqual(row["acceptable_outputs"], [])
                    self.assertFalse(row["adjudication_required"])

    def test_editorial_cases_preserve_source(self):
        for row in self.rows:
            if row["pun_class"] == "PUN-J3-EDITORIAL":
                with self.subTest(case=row["id"]):
                    self.assertEqual(row["action"], "PRESERVE")
                    self.assertEqual(row["source"], row["expected"])
                    self.assertTrue(row["adjudication_required"])

    def test_protected_literals_survive_all_registered_accepted_forms(self):
        for row in self.rows:
            forms = [row["expected"], *row["acceptable_outputs"]]
            for token in row["protected"]:
                with self.subTest(case=row["id"], token=token):
                    self.assertIn(token, row["source"])
                    for form in forms:
                        self.assertIn(token, form)


class PunctuationAdjudicationScorerTests(unittest.TestCase):
    def test_accepts_registered_style_variant(self):
        rows = [{
            "id": "PUN-H-001",
            "case": {
                "pun_class": "PUN-S2-STRUCTURAL",
                "expected": "الأقسام: الأول؛ والثاني؛ والثالث.",
                "acceptable_outputs": ["الأقسام: الأول، والثاني، والثالث."],
                "source": "الأقسام؛ الأول والثاني والثالث.",
                "protected": [],
                "adjudication_required": True,
            },
            "baseline": {"returncode": 0, "output": "الأقسام: الأول، والثاني، والثالث."},
            "candidate": {"returncode": 0, "output": "الأقسام: الأول؛ والثاني؛ والثالث."},
        }]
        report = pun.score(rows)
        self.assertEqual(report["baseline"]["summary"]["accepted_substantive_rate"], 1.0)
        self.assertEqual(report["candidate"]["summary"]["accepted_substantive_rate"], 1.0)
        self.assertEqual(report["baseline"]["summary"]["needs_human_review"], 0)

    def test_unmatched_structural_variant_routes_to_human_review(self):
        rows = [{
            "id": "PUN-H-002",
            "case": {
                "pun_class": "PUN-S2-STRUCTURAL",
                "expected": "قال: نعم.",
                "acceptable_outputs": [],
                "source": "قال، نعم.",
                "protected": [],
                "adjudication_required": True,
            },
            "baseline": {"returncode": 0, "output": "قال — نعم."},
            "candidate": {"returncode": 0, "output": "قال: نعم."},
        }]
        report = pun.score(rows)
        self.assertEqual(report["baseline"]["summary"]["needs_human_review"], 1)
        self.assertEqual(report["baseline"]["summary"]["deterministic_failures"], 0)
        self.assertEqual(report["candidate"]["summary"]["pass_accepted"], 1)

    def test_unmatched_deterministic_case_is_hard_failure(self):
        rows = [{
            "id": "PUN-D-001",
            "case": {
                "pun_class": "PUN-D1-DETERMINISTIC",
                "expected": "هل وصل التقرير؟",
                "acceptable_outputs": [],
                "source": "هل وصل التقرير.",
                "protected": [],
                "adjudication_required": False,
            },
            "baseline": {"returncode": 0, "output": "هل وصل التقرير."},
            "candidate": {"returncode": 0, "output": "هل وصل التقرير؟"},
        }]
        report = pun.score(rows)
        self.assertEqual(report["baseline"]["summary"]["deterministic_failures"], 1)
        self.assertEqual(report["baseline"]["summary"]["needs_human_review"], 0)
        self.assertEqual(report["candidate"]["summary"]["pass_accepted"], 1)

    def test_protected_literal_retention_is_separate(self):
        rows = [{
            "id": "PUN-D-002",
            "case": {
                "pun_class": "PUN-D1-DETERMINISTIC",
                "expected": "هل بلغت النسبة 25%؟",
                "acceptable_outputs": [],
                "source": "هل بلغت النسبة 25%.",
                "protected": ["25%"],
                "adjudication_required": False,
            },
            "baseline": {"returncode": 0, "output": "هل بلغت النسبة 25%؟"},
            "candidate": {"returncode": 0, "output": "هل بلغت النسبة ربعًا؟"},
        }]
        report = pun.score(rows)
        self.assertEqual(report["baseline"]["summary"]["protected_literal_retention"], 1.0)
        self.assertEqual(report["candidate"]["summary"]["protected_failures"], 1)


if __name__ == "__main__":
    unittest.main()
