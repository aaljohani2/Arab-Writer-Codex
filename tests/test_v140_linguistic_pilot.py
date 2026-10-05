import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / "evals"
FILES = sorted(EVALS.glob("linguistic_core_pilot_*.jsonl"))

ALLOWED_FAMILIES = {"ORT", "MOR", "SYN", "AGR", "NUM", "PUN", "AMB", "STY"}
ALLOWED_STATUS = {"DEFECT", "CONTEXTUAL_DEFECT", "EDITORIAL_OPPORTUNITY", "AMBIGUOUS"}
ALLOWED_CONFIDENCE = {"D1_DETERMINISTIC", "C2_HIGH_CONTEXT", "C3_MODEL_JUDGMENT", "H4_HUMAN_REVIEW"}
ALLOWED_SEVERITY = {"S1_MECHANICAL", "S2_GRAMMATICAL", "S3_CLARITY", "S4_MEANING_RISK"}
ALLOWED_ACTIONS = {"CORRECT", "CORRECT_AFTER_CONTEXT", "PRESERVE", "FLAG", "EDITORIAL_REWRITE_ONLY"}
ALLOWED_CASE_TYPES = {"correction", "no_change", "adversarial", "fidelity"}
REQUIRED = {
    "id", "family", "rule", "status", "confidence", "severity", "case_type",
    "mode", "locale", "task", "input", "source", "expected", "action",
    "protected", "rationale", "tags",
}


def load_cases():
    cases = []
    for path in FILES:
        for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not raw.strip():
                continue
            try:
                case = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise AssertionError(f"invalid JSONL in {path.name}:{line_no}: {exc}") from exc
            case["_file"] = path.name
            cases.append(case)
    return cases


class LinguisticPilotSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = load_cases()

    def test_pilot_has_expected_initial_size(self):
        self.assertEqual(len(self.cases), 64)

    def test_ids_are_unique(self):
        ids = [c["id"] for c in self.cases]
        self.assertEqual(len(ids), len(set(ids)))

    def test_required_fields_and_enums(self):
        for c in self.cases:
            self.assertTrue(REQUIRED.issubset(c), (c.get("id"), REQUIRED - set(c)))
            self.assertIn(c["family"], ALLOWED_FAMILIES)
            self.assertIn(c["status"], ALLOWED_STATUS)
            self.assertIn(c["confidence"], ALLOWED_CONFIDENCE)
            self.assertIn(c["severity"], ALLOWED_SEVERITY)
            self.assertIn(c["action"], ALLOWED_ACTIONS)
            self.assertIn(c["case_type"], ALLOWED_CASE_TYPES)
            self.assertEqual(c["input"], c["source"])
            self.assertTrue(c["rationale"].strip())

    def test_family_allocation(self):
        counts = Counter(c["family"] for c in self.cases)
        self.assertEqual(counts, Counter({"SYN": 20, "ORT": 10, "MOR": 10, "AGR": 8, "NUM": 8, "PUN": 4, "AMB": 4}))

    def test_case_type_mix(self):
        kinds = Counter(c["case_type"] for c in self.cases)
        self.assertGreaterEqual(kinds["correction"], 25)
        self.assertGreaterEqual(kinds["no_change"], 20)
        self.assertGreaterEqual(kinds["adversarial"], 5)
        self.assertGreaterEqual(kinds["fidelity"], 4)

    def test_no_change_and_preserve_cases_do_not_rewrite(self):
        for c in self.cases:
            if c["case_type"] == "no_change" or c["action"] in {"PRESERVE", "FLAG"}:
                self.assertEqual(c["source"], c["expected"], c["id"])

    def test_correction_cases_have_a_real_change(self):
        for c in self.cases:
            if c["action"] == "CORRECT":
                self.assertNotEqual(c["source"], c["expected"], c["id"])

    def test_protected_literals_survive_gold_correction(self):
        for c in self.cases:
            for token in c["protected"]:
                self.assertIn(token, c["source"], (c["id"], token, "source"))
                self.assertIn(token, c["expected"], (c["id"], token, "expected"))

    def test_high_value_guard_cases_exist(self):
        by_id = {c["id"]: c for c in self.cases}
        for case_id in (
            "MOR-03-001", "SYN-15-002", "SYN-12-002", "SYN-19-001",
            "AGR-06-001", "NUM-05-001", "AMB-03-001", "AMB-06-001",
        ):
            self.assertIn(case_id, by_id)


if __name__ == "__main__":
    unittest.main()
