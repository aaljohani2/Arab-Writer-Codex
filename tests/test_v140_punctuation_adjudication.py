import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCORER_PATH = ROOT / "evals" / "score_punctuation_holdout.py"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


pun = load_module("score_punctuation_holdout_v140", SCORER_PATH)


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
