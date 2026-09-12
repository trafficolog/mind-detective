import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "apps/web/public"
PROPOSAL_COPY_KEYS = {
    "reconstruction.clarify_supported_sequence",
    "next_action.check_target",
    "empty.resolve_partial_check",
    "empty.add_supported_place_or_reconstruct",
}


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise AssertionError(f"not a PNG: {path}")
    return struct.unpack(">II", data[16:24])


class WebPwaContractTests(unittest.TestCase):
    def test_proposal_copy_key_is_typed_and_rendered_from_i18n(self):
        web_contract = (ROOT / "apps/web/app/lib/api/contracts.ts").read_text(encoding="utf-8")
        api_contract = (ROOT / "apps/api/mind_detective_api/contracts.py").read_text(encoding="utf-8")
        card = (ROOT / "apps/web/app/components/case/NextActionCard.vue").read_text(encoding="utf-8")
        ru = (ROOT / "apps/web/app/lib/i18n/ru.ts").read_text(encoding="utf-8")
        en = (ROOT / "apps/web/app/lib/i18n/en.ts").read_text(encoding="utf-8")

        self.assertIn("export type ProposalCopyKey =", web_contract)
        self.assertIn("copy_key: ProposalCopyKey", web_contract)
        self.assertIn("ProposalCopyKey = Literal[", api_contract)
        self.assertIn("copy_key: ProposalCopyKey", api_contract)
        self.assertIn("t(props.proposal.copy_key)", card)
        for key in PROPOSAL_COPY_KEYS:
            self.assertIn(f"'{key}'", web_contract)
            self.assertIn(f'"{key}"', api_contract)
            self.assertIn(f"'{key}'", ru)
            self.assertIn(f"'{key}'", en)

    def test_pwa_has_installable_png_icon_set_and_apple_touch_icon(self):
        manifest = json.loads((PUBLIC / "manifest.webmanifest").read_text(encoding="utf-8"))
        icons = {
            (icon["src"], icon["sizes"], icon["type"], icon.get("purpose"))
            for icon in manifest["icons"]
        }
        self.assertIn(("/icon-192.png", "192x192", "image/png", "any maskable"), icons)
        self.assertIn(("/icon-512.png", "512x512", "image/png", "any maskable"), icons)

        self.assertEqual(png_dimensions(PUBLIC / "icon-192.png"), (192, 192))
        self.assertEqual(png_dimensions(PUBLIC / "icon-512.png"), (512, 512))
        self.assertEqual(png_dimensions(PUBLIC / "apple-touch-icon.png"), (180, 180))

        nuxt = (ROOT / "apps/web/nuxt.config.ts").read_text(encoding="utf-8")
        self.assertIn("apple-touch-icon.png", nuxt)
        self.assertIn("icon-192.png", nuxt)
        self.assertIn("icon-512.png", nuxt)
        self.assertIn("png", nuxt)


if __name__ == "__main__":
    unittest.main()
