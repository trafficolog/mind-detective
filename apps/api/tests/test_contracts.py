from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from mind_detective_api.app import app


class ApiContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_create_returns_case_v2(self):
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

    def test_validate_migrates_v1_without_inventing_history(self):
        legacy = {
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

    def test_validate_rejects_future_schema_with_machine_code(self):
        response = self.client.post(
            "/api/v1/case/validate",
            json={"case": {"schema": "mind-detective-case/v999"}},
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["code"], "MD_STORE_SCHEMA_VERSION")


if __name__ == "__main__":
    unittest.main()
