import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

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

    def test_stratified_smoke_covers_every_pilot_family_once(self):
        files = runner.load_eval_files(None, "evals/linguistic_core_pilot_*.jsonl")
        cases = runner.load_cases(files)
        smoke = runner.select_stratified_smoke(cases)
        self.assertEqual(len(smoke), len(runner.DEFAULT_SMOKE_FAMILIES))
        self.assertEqual(
            [case["family"] for case in smoke],
            list(runner.DEFAULT_SMOKE_FAMILIES),
        )
        self.assertEqual(len({case["id"] for case in smoke}), len(smoke))


class SkillIsolationTests(unittest.TestCase):
    def test_disable_override_is_path_scoped_not_name_scoped(self):
        p = Path("/tmp/example/.agents/skills/arab-writer/SKILL.md")
        override = runner.skill_disable_override([p])
        self.assertIn("skills.config=[", override)
        self.assertIn("enabled=false", override)
        self.assertIn("arab-writer", override)
        self.assertNotIn('name="arab-writer"', override)

    def test_windows_path_is_escaped_for_toml(self):
        p = Path(r"C:\Users\tester\.agents\skills\arab-writer\SKILL.md")
        override = runner.skill_disable_override([p])
        self.assertIn("skills.config=[", override)
        self.assertIn("arab-writer", override)
        self.assertIn("enabled=false", override)

    def test_baseline_visibility_detects_skill_name(self):
        text = (
            "<skills_instructions>\n"
            "- arab-writer: Arabic editor "
            "C:/Users/test/.agents/skills/arab-writer/SKILL.md\n"
            "</skills_instructions>"
        )
        v = runner.inspect_skill_prompt(text)
        self.assertTrue(v["skill_named"])

    def test_candidate_visibility_distinguishes_local_and_global_paths(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            local = root / "candidate/.agents/skills/arab-writer/SKILL.md"
            global_path = root / "global/.agents/skills/arab-writer/SKILL.md"
            sentinel = "AW_ISOLATION_TEST123"
            text = (
                "<skills_instructions>\n"
                f"- arab-writer: Arabic editor {sentinel} {local.as_posix()}\n"
                "</skills_instructions>"
            )
            v = runner.inspect_skill_prompt(
                text,
                local_skill_path=local,
                global_skill_paths=[global_path],
                sentinel=sentinel,
            )
            self.assertTrue(v["skill_named"])
            self.assertTrue(v["local_path_visible"])
            self.assertTrue(v["sentinel_visible"])
            self.assertEqual(v["global_paths_visible"], [])

    def test_global_path_visibility_is_reported(self):
        with tempfile.TemporaryDirectory() as td:
            global_path = Path(td) / ".agents/skills/arab-writer/SKILL.md"
            text = f"skill path: {global_path.as_posix()}"
            v = runner.inspect_skill_prompt(
                text,
                global_skill_paths=[global_path],
            )
            self.assertEqual(v["global_paths_visible"], [str(global_path)])

    def test_isolation_sentinel_is_injected_into_description(self):
        with tempfile.TemporaryDirectory() as td:
            skill = Path(td) / "SKILL.md"
            skill.write_text(
                "---\nname: arab-writer\ndescription: Arabic editor.\n---\n\n# Skill\n",
                encoding="utf-8",
            )
            sentinel = "AW_ISOLATION_TEST456"
            runner.inject_isolation_sentinel(skill, sentinel)
            text = skill.read_text(encoding="utf-8")
            self.assertIn("description: Arabic editor. Isolation sentinel:", text)
            self.assertIn(sentinel, text)
            self.assertTrue(
                runner.inspect_skill_prompt(text, sentinel=sentinel)["sentinel_visible"]
            )

    def test_controlled_run_requires_pinned_runtime_and_clean_git(self):
        args = SimpleNamespace(
            controlled=True,
            model=None,
            reasoning=None,
            skip_skill_isolation_preflight=False,
        )
        with self.assertRaises(SystemExit) as ctx:
            runner.validate_controlled_run(args, " M deleted-fixture")
        msg = str(ctx.exception)
        self.assertIn("--model is required", msg)
        self.assertIn("--reasoning is required", msg)
        self.assertIn("git worktree is dirty", msg)

    def test_controlled_run_accepts_clean_pinned_setup(self):
        args = SimpleNamespace(
            controlled=True,
            model="example-model",
            reasoning="medium",
            skip_skill_isolation_preflight=False,
        )
        runner.validate_controlled_run(args, "")


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
        self.assertEqual(
            report["delta_candidate_minus_baseline"]["correction_accuracy_delta"],
            1.0,
        )

    def test_optional_diacritic_does_not_fail_substantive_correction(self):
        rows = [{
            "id": "MOR-DIAC",
            "case": {
                "family": "MOR", "action": "CORRECT", "case_type": "correction",
                "source": "لن يكتبون التقارير غدا.",
                "expected": "لن يكتبوا التقارير غدا.",
                "protected": [],
            },
            "baseline": {"returncode": 0, "output": "لن يكتبوا التقارير غدًا."},
            "candidate": {"returncode": 0, "output": "لن يكتبوا التقارير غدًا."},
        }]
        report = scorer.score(rows)
        summary = report["candidate"]["summary"]
        self.assertEqual(summary["correction_accuracy"], 1.0)
        self.assertEqual(summary["exact_correction_accuracy"], 0.0)
        self.assertEqual(summary["substantive_gold_rate"], 1.0)
        self.assertEqual(summary["exact_gold_rate"], 0.0)
        self.assertEqual(
            report["candidate"]["mismatches"][0]["difference_class"],
            "optional_diacritics_only",
        )

    def test_diacritic_only_preserve_change_counts_as_overedit_but_not_substantive_change(self):
        rows = [{
            "id": "MOR-PRESERVE-DIAC",
            "case": {
                "family": "MOR", "action": "PRESERVE", "case_type": "no_change",
                "source": "الموظفون يكتبون التقارير يوميا.",
                "expected": "الموظفون يكتبون التقارير يوميا.",
                "protected": [],
            },
            "baseline": {"returncode": 0, "output": "الموظفون يكتبون التقارير يوميًا."},
            "candidate": {"returncode": 0, "output": "الموظفون يكتبون التقارير يوميًا."},
        }]
        report = scorer.score(rows)
        summary = report["candidate"]["summary"]
        self.assertEqual(summary["correct_source_preservation"], 0.0)
        self.assertEqual(summary["false_change_rate"], 1.0)
        self.assertEqual(summary["substantive_source_preservation"], 1.0)
        self.assertEqual(summary["substantive_false_change_rate"], 0.0)
        self.assertEqual(summary["diacritic_only_changes"], 1)

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
        self.assertEqual(
            report["candidate"]["summary"]["protected_literal_retention"],
            0.0,
        )

    def test_normalization_handles_whitespace_code_fence_and_optional_harakat(self):
        self.assertEqual(scorer.normalize("  نص   عربي  "), "نص عربي")
        self.assertEqual(scorer.normalize("```\nنص عربي\n```"), "نص عربي")
        self.assertEqual(
            scorer.normalize_substantive("غدًا"),
            scorer.normalize_substantive("غدا"),
        )
        self.assertNotEqual(scorer.normalize("غدًا"), scorer.normalize("غدا"))


if __name__ == "__main__":
    unittest.main()
