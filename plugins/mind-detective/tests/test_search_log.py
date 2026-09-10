import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from scripts.search_log import (  # noqa: E402
    SearchCheck,
    SearchLog,
    SearchLogError,
    SearchMethod,
    SearchResult,
    is_duplicate_target,
    normalize_target,
    refine_search_check_method,
)


class SearchLogTests(unittest.TestCase):
    def _check(self, check_id: str, method: SearchMethod) -> SearchCheck:
        return SearchCheck(
            id=check_id,
            target="Карманы куртки",
            method=method,
            started_at="2026-09-09T18:00:00Z",
            completed_at="2026-09-09T18:01:00Z",
            result=SearchResult.NOT_FOUND,
            inaccessible_parts=(),
            based_on=("s1",),
            notes=("original",),
        )

    def test_repeated_checks_remain_distinct_entries(self):
        log = SearchLog()
        first = self._check("c1", SearchMethod.GLANCE)
        second = self._check("c2", SearchMethod.EMPTY_AND_CHECK)
        self.assertEqual(log.add(first), (first,))
        self.assertEqual(log.add(second), (first, second))

    def test_near_duplicate_target_is_detected_deterministically(self):
        self.assertTrue(is_duplicate_target("Карманы куртки", "карманы вчерашней куртки"))
        self.assertEqual(normalize_target("В карманах куртки"), ("карманах", "куртки"))

    def test_one_content_token_subset_is_not_enough(self):
        self.assertFalse(is_duplicate_target("сумка", "сумка в машине"))

    def test_reported_check_is_neutral_method(self):
        check = self._check("c1", SearchMethod.REPORTED_CHECK)
        self.assertEqual(check.method.value, "reported_check")

    def test_refinement_preserves_original_check_identity_and_evidence(self):
        reported = self._check("c1", SearchMethod.REPORTED_CHECK)
        refined = refine_search_check_method((reported,), "c1", SearchMethod.EMPTY_AND_CHECK)
        self.assertEqual(refined[0].id, "c1")
        self.assertEqual(refined[0].started_at, reported.started_at)
        self.assertEqual(refined[0].completed_at, reported.completed_at)
        self.assertEqual(refined[0].result, reported.result)
        self.assertEqual(refined[0].based_on, reported.based_on)
        self.assertEqual(refined[0].notes, reported.notes)
        self.assertEqual(refined[0].method, SearchMethod.EMPTY_AND_CHECK)

    def test_inaccessible_cannot_be_used_as_new_refinement_method(self):
        reported = self._check("c1", SearchMethod.REPORTED_CHECK)
        with self.assertRaises(SearchLogError) as ctx:
            refine_search_check_method((reported,), "c1", SearchMethod.INACCESSIBLE)
        self.assertEqual(ctx.exception.code, "MD_SEARCH_METHOD_INVALID")


if __name__ == "__main__":
    unittest.main()
