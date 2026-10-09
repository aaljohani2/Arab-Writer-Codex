import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / ".agents" / "skills" / "arab-writer"
SKILL = SKILL_ROOT / "SKILL.md"
VERIFY = SKILL_ROOT / "references" / "arabic-linguistic-verification.md"
PUNCT = SKILL_ROOT / "references" / "arabic-punctuation.md"


class V140PunctuationCoreTests(unittest.TestCase):
    def test_punctuation_core_exists_and_is_wired(self):
        self.assertTrue(PUNCT.is_file())
        skill_text = SKILL.read_text(encoding="utf-8")
        verify_text = VERIFY.read_text(encoding="utf-8")
        self.assertIn("references/arabic-punctuation.md", skill_text)
        self.assertIn("arabic-punctuation.md", verify_text)

    def test_three_level_decision_model_is_present(self):
        text = PUNCT.read_text(encoding="utf-8")
        for marker in [
            "D1 — deterministic/mechanical",
            "S2 — structural/contextual",
            "J3 — editorial/judgment",
            "## 5. Announced enumeration and division",
            "## 6. Explanation after a summary expression",
            "## 8. Comma versus semicolon",
            "## 9. Heritage-sensitive punctuation",
            "## 11. Minimality gate",
        ]:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_reference_anchors_include_historical_and_modern_sources(self):
        text = PUNCT.read_text(encoding="utf-8")
        for name in ["أحمد زكي باشا", "جامعة الملك سعود", "مجمع الملك سلمان العالمي للغة العربية"]:
            with self.subTest(name=name):
                self.assertIn(name, text)

    def test_verification_distinguishes_mechanical_structural_and_editorial(self):
        text = VERIFY.read_text(encoding="utf-8")
        self.assertIn("D1 mechanical", text)
        self.assertIn("S2 structural", text)
        self.assertIn("J3 editorial", text)
        self.assertIn("Preserve J3", text)

    def test_runtime_knowledge_does_not_copy_punctuation_holdout(self):
        runtime = "\n".join([
            SKILL.read_text(encoding="utf-8"),
            VERIFY.read_text(encoding="utf-8"),
            PUNCT.read_text(encoding="utf-8"),
        ])
        forbidden = [
            "PUN-HO-",
            "فإن قيل: هل يثبت الحكم بخبر الواحد.",
            "والوجوه ثلاثة؛ الأول: ما دل عليه النص",
            "ومعنى ذلك أمر واحد وهو أن الحكم يدور",
            "تقوم الخطة على ثلاثة محاور هي الكفاءة",
            "بلغت التغطية 92% (بحسب التعريف المعتمد.",
        ]
        for value in forbidden:
            with self.subTest(value=value):
                self.assertNotIn(value, runtime)


if __name__ == "__main__":
    unittest.main()
