import json
import tempfile
import unittest
from pathlib import Path

from scripts.check_pages_build import check_pages_build

BASE = "/mind-detective/"


def site(root: Path, *, html_ref: str, css_ref: str, js_ref: str, start_url: str, fallback: str) -> None:
    (root / "_nuxt").mkdir(parents=True)
    (root / "brand").mkdir()
    (root / "brand/logo.svg").write_text("<svg/>", encoding="utf-8")
    (root / "cases").mkdir()
    (root / "cases/index.html").write_text("<html></html>", encoding="utf-8")
    page = f'<link rel="manifest" href="{html_ref}"><a href="https://example.com/x">x</a>'
    for name in ("index.html", "404.html"):
        (root / name).write_text(page, encoding="utf-8")
    (root / "_nuxt/app.css").write_text(f"a{{background:url({css_ref})}}", encoding="utf-8")
    (root / "_nuxt/app.js").write_text(f'const logo=`{js_ref}`;navigateTo("/cases")', encoding="utf-8")
    manifest = {"start_url": start_url, "scope": start_url, "icons": [{"src": "icon-192.png"}]}
    (root / "manifest.webmanifest").write_text(json.dumps(manifest), encoding="utf-8")
    (root / "sw.js").write_text(f'new NavigationRoute(createHandlerBoundToURL("{fallback}"))', encoding="utf-8")


class PagesBuildCheckTests(unittest.TestCase):
    def test_sub_path_build_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            site(root, html_ref=f"{BASE}manifest.webmanifest", css_ref="../fonts/a.woff2",
                 js_ref=f"{BASE}brand/logo.svg", start_url="./", fallback=BASE)
            self.assertEqual(check_pages_build(root, BASE), [])

    def test_root_build_is_valid_for_root_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            site(root, html_ref="/manifest.webmanifest", css_ref="/fonts/a.woff2",
                 js_ref="/brand/logo.svg", start_url="./", fallback="/")
            self.assertEqual(check_pages_build(root, "/"), [])

    def test_root_absolute_references_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            site(root, html_ref="/manifest.webmanifest", css_ref="/fonts/a.woff2",
                 js_ref="/brand/logo.svg", start_url="/", fallback="/")
            errors = check_pages_build(root, BASE)
            self.assertIn("MD_PAGES_ROOT_REF:index.html:/manifest.webmanifest", errors)
            self.assertIn("MD_PAGES_ROOT_CSS_URL:_nuxt/app.css:/fonts/a.woff2", errors)
            self.assertIn("MD_PAGES_ROOT_JS_REF:_nuxt/app.js:/brand", errors)
            self.assertIn("MD_PAGES_ROOT_MANIFEST_REF:/", errors)
            self.assertIn("MD_PAGES_SW_NAVIGATE_FALLBACK", errors)
            self.assertNotIn("MD_PAGES_ROOT_JS_REF:_nuxt/app.js:/cases", errors)

    def test_spa_404_fallback_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            site(root, html_ref=f"{BASE}m", css_ref="a", js_ref="b", start_url="./", fallback=BASE)
            (root / "404.html").unlink()
            self.assertEqual(check_pages_build(root, BASE), ["MD_PAGES_MISSING:404.html"])


class PagesWorkflowTests(unittest.TestCase):
    def test_pages_workflow_is_pinned_and_verifies_the_base_path(self) -> None:
        workflow = (Path(__file__).resolve().parents[1] / ".github/workflows/pages.yml").read_text(encoding="utf-8")
        for line in workflow.splitlines():
            if "uses:" in line:
                self.assertRegex(line.split("@", 1)[-1].split()[0], r"^[0-9a-f]{40}$")
        self.assertIn("pnpm install --frozen-lockfile", workflow)
        self.assertIn("NUXT_APP_BASE_URL", workflow)
        self.assertIn("python scripts/check_pages_build.py", workflow)
        self.assertIn("branches: [main]", workflow)


if __name__ == "__main__":
    unittest.main()
