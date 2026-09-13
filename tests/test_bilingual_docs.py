import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.bilingual_docs import REQUIRED_PAIRS, validate_bilingual_docs  # noqa: E402


class BilingualDocsTests(unittest.TestCase):
    def test_required_ru_en_pairs_exist_and_link_to_each_other(self):
        self.assertEqual(validate_bilingual_docs(ROOT), [])
        self.assertGreaterEqual(len(REQUIRED_PAIRS), 10)

    def test_root_readme_uses_supported_product_positioning_without_forbidden_claims(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8").casefold()
        self.assertIn("помощник систематического поиска потерянных вещей", text)
        for forbidden in (
            "восстанавливает память",
            "определяет механизм забывания",
            "знает, где находится предмет",
            "гарантирует найти",
        ):
            self.assertNotIn(forbidden, text)

    def test_product_evaluation_contains_three_arms_and_censored_outcomes(self):
        text = (ROOT / "docs/PRODUCT_EVALUATION.md").read_text(encoding="utf-8")
        self.assertIn("A — обычный поиск", text)
        self.assertIn("B — структурированный чек-лист", text)
        self.assertIn("C — чек-лист + журнал поиска + диалоговый AI", text)
        self.assertIn("unresolved", text)
        self.assertIn("abandoned", text)

    def test_product_evaluation_does_not_overclaim_live_model_reconstruction(self):
        text = (ROOT / "docs/PRODUCT_EVALUATION.md").read_text(encoding="utf-8").casefold()
        self.assertIn("staged b↔c", text)
        self.assertIn("live-model reconstruction", text)
        self.assertIn("не является доказательством", text)

    def test_privacy_states_explicit_case_local_save_delete_and_no_cross_case_index(self):
        text = (ROOT / "docs/PRIVACY.md").read_text(encoding="utf-8").casefold()
        self.assertIn("явному действию пользователя", text)
        self.assertIn(".mind-detective/cases/<case-id>/case.json", text)
        self.assertIn("не создаёт cross-case index", text)
        self.assertIn("free_account", text)
        self.assertIn("reconstruction", text)
        self.assertIn("дослов", text)

    def test_ru_en_public_docs_describe_the_same_web_reconstruction_boundary(self):
        ru = "\n".join(
            (ROOT / path).read_text(encoding="utf-8").casefold()
            for path in (
                "README.md",
                "docs/ARCHITECTURE.md",
                "docs/GETTING_STARTED.md",
            )
        )
        en = "\n".join(
            (ROOT / path).read_text(encoding="utf-8").casefold()
            for path in (
                "README.en.md",
                "docs/ARCHITECTURE.en.md",
                "docs/GETTING_STARTED.en.md",
            )
        )

        for stale in (
            "web/pwa — search/checklist surface",
            "полная reconstruction остаётся plugin/agent capability",
            "web surface — физический search/checklist workflow",
        ):
            self.assertNotIn(stale, ru)
        for stale in (
            "the web/pwa is a search/checklist surface",
            "full reconstruction remaining a plugin/agent capability",
            "the web surface is the physical search/checklist workflow",
        ):
            self.assertNotIn(stale, en)

        for expected in (
            "свободный рассказ",
            "дослов",
            "подтверждён",
            "неизвест",
            "противореч",
            "локальн",
            "детерминирован",
            "mind-detective-case/v2",
        ):
            self.assertIn(expected, ru)
        for expected in (
            "free account",
            "verbatim",
            "user-confirmed",
            "unknowns",
            "contradictions",
            "local deterministic reconstruction",
            "mind-detective-case/v2",
        ):
            self.assertIn(expected, en)


if __name__ == "__main__":
    unittest.main()
