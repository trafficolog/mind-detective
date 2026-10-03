import http.client
import json
import tempfile
import unittest
from pathlib import Path

from scripts.wait_for_pages_build import local_build_id, wait_for_build


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def time(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


class WaitForPagesBuildTests(unittest.TestCase):
    def test_reads_local_build_id_from_nuxt_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "_nuxt/builds").mkdir(parents=True)
            (root / "_nuxt/builds/latest.json").write_text(json.dumps({"id": "abc", "timestamp": 1}), encoding="utf-8")
            self.assertEqual(local_build_id(root), "abc")

    def test_returns_as_soon_as_the_live_build_matches(self) -> None:
        clock = FakeClock()
        answers = iter([{"id": "old"}, OSError("503"), http.client.IncompleteRead(b""), {"id": "new"}])
        seen: list[str] = []

        def fetch(url: str) -> dict:
            seen.append(url)
            answer = next(answers)
            if isinstance(answer, Exception):
                raise answer
            return answer

        ok = wait_for_build("https://o.github.io/repo", "new", timeout=120, interval=10, fetch=fetch, clock=clock)
        self.assertTrue(ok)
        manifest = "https://o.github.io/repo/_nuxt/builds/latest.json"
        self.assertTrue(all(url.startswith(manifest + "?attempt=") for url in seen))
        self.assertEqual(len(set(seen)), len(seen), "each poll bypasses the CDN cache with a distinct URL")
        self.assertEqual(clock.sleeps, [10, 10, 10])

    def test_gives_up_after_the_timeout(self) -> None:
        clock = FakeClock()
        ok = wait_for_build("https://o.github.io/repo/", "new", timeout=30, interval=10, fetch=lambda _: {"id": "old"}, clock=clock)
        self.assertFalse(ok)
        self.assertLessEqual(clock.now, 30)


if __name__ == "__main__":
    unittest.main()
