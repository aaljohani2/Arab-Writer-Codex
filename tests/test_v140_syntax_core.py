import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / ".agents" / "skills" / "arab-writer"
SKILL = SKILL_ROOT / "SKILL.md"
SYNTAX = SKILL_ROOT / "references" / "arabic-syntax.md"
VERIFY = SKILL_ROOT / "references" / "arabic-linguistic-verification.md"


class V140SyntaxCoreTests(unittest.TestCase):
    def test_syntax_core_exists_and_is_wired(self):
        self.assertTrue(SYNTAX.is_file())
        skill_text = SKILL.read_text(encoding="utf-8")
        self.assertIn("references/arabic-syntax.md", skill_text)
        self.assertIn("grammatical discovery pass", skill_text)
        self.assertIn("passive verbs that take two objects", skill_text)
        self.assertIn("direct adjective/predicate agreement with non-human plurals", skill_text)

    def test_verification_routes_to_syntax_core(self):
        text = VERIFY.read_text(encoding="utf-8")
        self.assertIn("arabic-syntax.md", text)
        self.assertIn("Minimality must not become passivity", text)
        self.assertIn("Visible morphology rule", text)
        self.assertIn("Non-human plural attachment check", text)
        self.assertIn("Passive ditransitive check", text)

    def test_syntax_core_covers_priority_blind_failure_families(self):
        text = SYNTAX.read_text(encoding="utf-8")
        required = [
            "Mandatory visible-form checks before `no change`",
            "## 2. `إن` and sisters",
            "## 3. `كان` and sisters",
            "## 5. Exception with `إلا`",
            "## 6. Passive voice and deputy subject",
            "Passive-ditransitive decision procedure",
            "## 7. Human and non-human plural agreement",
            "Local attachment: do not spread agreement across the sentence",
            "## 9. Relative pronouns",
            "## 11. `غير` and similar dependent expressions",
            "## 14. Visible case vs invisible case",
            "## 15. Minimality is not passivity",
            "Final syntax gate before returning",
        ]
        for heading in required:
            with self.subTest(heading=heading):
                self.assertIn(heading, text)

    def test_agreement_guidance_distinguishes_direct_attachment_from_separate_relation(self):
        text = SYNTAX.read_text(encoding="utf-8")
        self.assertIn("feminine singular is the standard agreement target", text)
        self.assertIn("syntactic attachment, not nearest-noun attraction", text)
        self.assertIn("separate predicative relation", text)

    def test_passive_ditransitive_guidance_requires_promoted_first_object(self):
        text = SYNTAX.read_text(encoding="utf-8")
        self.assertIn("promoted first object", text)
        self.assertIn("نائب الفاعل", text)
        self.assertIn("require nominative form", text)
        self.assertIn("dual and sound-plural endings", text)

    def test_reference_anchors_include_classical_and_modern_grammars(self):
        text = SYNTAX.read_text(encoding="utf-8")
        for name in ["سيبويه", "ابن هشام", "ابن عقيل", "الغلاييني", "عباس حسن"]:
            with self.subTest(name=name):
                self.assertIn(name, text)

    def test_runtime_knowledge_does_not_copy_challenge_ids_or_target_sentences(self):
        runtime = "\n".join(
            [
                SKILL.read_text(encoding="utf-8"),
                VERIFY.read_text(encoding="utf-8"),
                SYNTAX.read_text(encoding="utf-8"),
            ]
        )
        self.assertNotIn("CH-SYN-", runtime)
        self.assertNotIn("CH-AGR-", runtime)
        self.assertNotIn("هذه الرواياتُ مختلفون", runtime)
        self.assertNotIn("المبادرات اللاتي خُصصت", runtime)
        self.assertNotIn("أُعطي الباحثين صلاحيةَ الوصول", runtime)
        self.assertNotIn("ما رجّح المصنف في هذا الموضع", runtime)


if __name__ == "__main__":
    unittest.main()
