import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from scripts.search_log import (  # noqa: E402
    SearchCheck,
    SearchLog,
    SearchMethod,
    SearchResult,
    is_duplicate_target,
    normalize_target,
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
            notes=(),
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
