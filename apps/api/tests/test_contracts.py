from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from mind_detective_api.app import app


class ApiContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_create_returns_case_v2(self) -> None:
        response = self.client.post(
            "/api/v1/case/create",
            json={
                "case_id": "case-1",
                "item_label": "ключи",
                "now": "2026-09-10T07:00:00Z",
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()["case"]
        self.assertEqual(payload["schema"], "mind-detective-case/v2")
        self.assertEqual(payload["current_mode"], "unselected")
        self.assertEqual(payload["interaction_journal"], [])
        self.assertEqual(payload["action_feedback"], [])

    def test_validate_migrates_v1_without_inventing_history(self) -> None:
        legacy: dict[str, object] = {
            "schema": "mind-detective-case/v1",
            "case_id": "legacy-1",
            "item_label": "паспорт",
            "created_at": "2026-09-09T18:00:00Z",
            "updated_at": "2026-09-09T18:05:00Z",
            "lifecycle": "active",
            "statements": [],
            "timeline": None,
            "search_checks": [],
            "candidates": [],
            "next_action": None,
            "constraints": [],
            "outcome": None,
        }
        response = self.client.post("/api/v1/case/validate", json={"case": legacy})
        self.assertEqual(response.status_code, 200)
        payload = response.json()["case"]
        self.assertEqual(payload["schema"], "mind-detective-case/v2")
        self.assertEqual(payload["current_mode"], "unselected")
        self.assertEqual(payload["interaction_journal"], [])

    def test_validate_rejects_future_schema_with_machine_code(self) -> None:
        response = self.client.post(
            "/api/v1/case/validate",
            json={"case": {"schema": "mind-detective-case/v999"}},
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["code"], "MD_STORE_SCHEMA_VERSION")

    def test_cors_allows_configured_local_web_origin_only(self) -> None:
        allowed = self.client.options(
            "/api/v1/case/create",
            headers={
                "Origin": "http://127.0.0.1:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(allowed.headers.get("access-control-allow-origin"), "http://127.0.0.1:3000")

        denied = self.client.options(
            "/api/v1/case/create",
            headers={
                "Origin": "https://untrusted.example",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        self.assertNotEqual(denied.headers.get("access-control-allow-origin"), "https://untrusted.example")


if __name__ == "__main__":
    unittest.main()
