import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / "evals"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


runner = load_module("run_ab_codex_v140", EVALS / "run_ab_codex.py")
scorer = load_module("score_linguistic_pilot_v140", EVALS / "score_linguistic_pilot.py")


class LinguisticPilotLoaderTests(unittest.TestCase):
    def test_glob_loads_all_pilot_cases(self):
        files = runner.load_eval_files(None, "evals/linguistic_core_pilot_*.jsonl")
        cases = runner.load_cases(files)
        self.assertEqual(len(files), 4)
        self.assertEqual(len(cases), 64)
        self.assertEqual(len({c["id"] for c in cases}), 64)

    def test_default_internal_suite_remains_available(self):
        files = runner.load_eval_files(None, None)
        self.assertEqual(files, [ROOT / "tests/evals.jsonl"])
        self.assertGreaterEqual(len(runner.load_cases(files)), 25)


class LinguisticPilotScorerTests(unittest.TestCase):
    def test_candidate_gain_and_preservation_are_separate(self):
        rows = [
            {
                "id": "MOR-X",
                "case": {
                    "family": "MOR", "action": "CORRECT", "case_type": "correction",
                    "source": "لن يكتبون.", "expected": "لن يكتبوا.", "protected": []
                },
                "baseline": {"returncode": 0, "output": "لن يكتبون."},
                "candidate": {"returncode": 0, "output": "لن يكتبوا."},
            },
            {
                "id": "AMB-X",
                "case": {
                    "family": "AMB", "action": "PRESERVE", "case_type": "adversarial",
                    "source": "لو اجتهدتم لنجحتم.", "expected": "لو اجتهدتم لنجحتم.", "protected": []
                },
                "baseline": {"returncode": 0, "output": "لو اجتهدتم لنجحتم."},
                "candidate": {"returncode": 0, "output": "لو اجتهدتم لنجحتم."},
            },
        ]
        report = scorer.score(rows)
        self.assertEqual(report["baseline"]["summary"]["correction_accuracy"], 0.0)
        self.assertEqual(report["candidate"]["summary"]["correction_accuracy"], 1.0)
        self.assertEqual(report["candidate"]["summary"]["correct_source_preservation"], 1.0)
        self.assertEqual(report["candidate"]["summary"]["false_change_rate"], 0.0)
        self.assertEqual(report["delta_candidate_minus_baseline"]["correction_accuracy_delta"], 1.0)

    def test_protected_literal_failure_is_visible(self):
        rows = [{
            "id": "NUM-X",
            "case": {
                "family": "NUM", "action": "CORRECT", "case_type": "fidelity",
                "source": "لدى الشركة 20 موظفون.", "expected": "لدى الشركة 20 موظفا.",
                "protected": ["20"]
            },
            "baseline": {"returncode": 0, "output": "لدى الشركة 20 موظفون."},
            "candidate": {"returncode": 0, "output": "لدى الشركة عشرون موظفا."},
        }]
        report = scorer.score(rows)
        self.assertEqual(report["candidate"]["summary"]["protected_failures"], 1)
        self.assertEqual(report["candidate"]["summary"]["protected_literal_retention"], 0.0)

    def test_normalization_handles_whitespace_and_code_fence(self):
        self.assertEqual(scorer.normalize("  نص   عربي  "), "نص عربي")
        self.assertEqual(scorer.normalize("```\nنص عربي\n```"), "نص عربي")


if __name__ == "__main__":
    unittest.main()
