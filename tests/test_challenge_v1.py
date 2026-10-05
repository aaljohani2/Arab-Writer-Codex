import json
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHALLENGE = ROOT / "evals" / "challenge"
BATCH01 = sorted(CHALLENGE.glob("challenge_v1_batch01_*.jsonl"))
ALL_CASE_FILES = sorted(CHALLENGE.glob("challenge_v1_batch*.jsonl"))
REGISTRY = CHALLENGE / "source_registry.json"

TARGET_FAMILIES = Counter({
    "SYN": 20,
    "MOR": 15,
    "NUM": 10,
    "AMB": 10,
    "AGR": 5,
    "ORT": 5,
    "PUN": 5,
})

REQUIRED_FIELDS = {
    "id", "family", "rule", "status", "confidence", "severity", "case_type",
    "mode", "locale", "task", "input", "source", "expected", "action",
    "protected", "rationale", "tags", "provenance", "rule_source",
    "difficulty", "challenge_axis",
}


def load_jsonl(paths):
    rows = []
    for path in paths:
        for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not raw.strip():
                continue
            try:
                rows.append(json.loads(raw))
            except json.JSONDecodeError as exc:
                raise AssertionError(f"invalid JSON: {path}:{line_no}: {exc}") from exc
    return rows


class ChallengeSourceRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.sources = cls.registry["sources"]
        cls.by_id = {s["id"]: s for s in cls.sources}

    def test_registry_has_unique_ids_and_two_eras(self):
        self.assertEqual(len(self.by_id), len(self.sources))
        self.assertGreaterEqual(len(self.sources), 24)
        self.assertEqual({s["era"] for s in self.sources}, {"classical", "modern"})

    def test_source_records_are_traceable(self):
        for src in self.sources:
            with self.subTest(src=src["id"]):
                self.assertTrue(src["author"])
                self.assertTrue(src["work"])
                self.assertTrue(src["domain"])
                self.assertTrue(src["url"].startswith("http"))
                self.assertTrue(src["usage"])
                self.assertIn(src["era"], {"classical", "modern"})


class ChallengeBatch01Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.source_by_id = {s["id"]: s for s in cls.registry["sources"]}
        cls.rows = load_jsonl(BATCH01)

    def test_batch01_file_and_case_counts(self):
        self.assertEqual(len(BATCH01), 4)
        self.assertEqual(len(self.rows), 20)
        self.assertEqual(len({row["id"] for row in self.rows}), 20)

    def test_batch01_family_mix(self):
        self.assertEqual(
            Counter(row["family"] for row in self.rows),
            Counter({"SYN": 6, "MOR": 4, "NUM": 3, "AMB": 3, "PUN": 2, "AGR": 1, "ORT": 1}),
        )

    def test_batch01_era_balance_is_10_10(self):
        eras = Counter(
            self.source_by_id[row["provenance"]["source_id"]]["era"]
            for row in self.rows
        )
        self.assertEqual(eras, Counter({"classical": 10, "modern": 10}))


class ChallengeFullSetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.source_by_id = {s["id"]: s for s in cls.registry["sources"]}
        cls.rows = load_jsonl(ALL_CASE_FILES)

    def test_full_set_file_case_and_id_counts(self):
        self.assertEqual(len(ALL_CASE_FILES), 9)
        self.assertEqual(len(self.rows), 70)
        self.assertEqual(len({row["id"] for row in self.rows}), 70)

    def test_full_set_hits_family_targets(self):
        self.assertEqual(Counter(row["family"] for row in self.rows), TARGET_FAMILIES)

    def test_full_set_era_balance_is_35_35(self):
        eras = Counter(
            self.source_by_id[row["provenance"]["source_id"]]["era"]
            for row in self.rows
        )
        self.assertEqual(eras, Counter({"classical": 35, "modern": 35}))

    def test_each_family_contains_classical_and_modern_cases(self):
        family_eras = defaultdict(set)
        for row in self.rows:
            source_id = row["provenance"]["source_id"]
            family_eras[row["family"]].add(self.source_by_id[source_id]["era"])
        for family in TARGET_FAMILIES:
            with self.subTest(family=family):
                self.assertEqual(family_eras[family], {"classical", "modern"})

    def test_required_schema_and_provenance(self):
        for row in self.rows:
            with self.subTest(case=row["id"]):
                self.assertTrue(REQUIRED_FIELDS.issubset(row))
                self.assertEqual(row["difficulty"], "hard")
                self.assertIn(row["action"], {"CORRECT", "PRESERVE", "FLAG"})
                self.assertIsInstance(row["protected"], list)
                self.assertTrue(row["challenge_axis"])
                self.assertIn(row["provenance"]["source_id"], self.source_by_id)
                self.assertTrue(row["provenance"]["anchor"])
                self.assertTrue(row["provenance"]["adaptation"])
                self.assertTrue(row["rule_source"]["work"])
                self.assertTrue(row["rule_source"]["author"])
                self.assertTrue(row["rule_source"]["topic"])
                self.assertNotIn("TODO", row.get("tags", []))

    def test_preserve_cases_are_exact_no_change(self):
        for row in self.rows:
            if row["action"] == "PRESERVE":
                with self.subTest(case=row["id"]):
                    self.assertEqual(row["source"], row["expected"])

    def test_correct_cases_change_the_source(self):
        for row in self.rows:
            if row["action"] == "CORRECT":
                with self.subTest(case=row["id"]):
                    self.assertNotEqual(row["source"], row["expected"])

    def test_protected_literals_survive_expected(self):
        for row in self.rows:
            for token in row["protected"]:
                with self.subTest(case=row["id"], token=token):
                    self.assertIn(token, row["source"])
                    self.assertIn(token, row["expected"])


if __name__ == "__main__":
    unittest.main()
