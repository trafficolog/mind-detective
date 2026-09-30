"""0.5.0 Glass Modern mobile slice of the portable kernel (ADR 016).

Test names carry the prototype test ids (T01–T47) from
docs/design/2026-09-30-glass-modern-mobile/TEST_CASES.md.
"""

import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from scripts.portable_contract import SUPPORTED_COMMAND_TYPES  # noqa: E402
from scripts.portable_intrinsics import PortableKernelError  # noqa: E402
from scripts.portable_kernel import (  # noqa: E402
    apply_command,
    create_case,
    create_case_with_kind,
    item_kind_json,
)

T0 = "2026-09-30T10:00:00Z"


class Session:
    """Applies commands sequentially with monotonically increasing timestamps."""

    def __init__(self, tc: unittest.TestCase, case: dict[str, object]) -> None:
        self.tc = tc
        self.case = case
        self.tick = 0

    def run(self, command_type: str, payload: dict[str, object] | None = None) -> dict[str, object]:
        self.tick += 1
        now = f"2026-09-30T10:{self.tick:02d}:00Z"
        self.case = apply_command(
            self.case,
            {
                "command_id": f"cmd-{self.tick}",
                "expected_updated_at": self.case["updated_at"],
                "command_type": command_type,
                "now": now,
                "payload": payload or {},
            },
        )
        return self.case

    def expect_error(self, code: str, command_type: str, payload: dict[str, object] | None = None) -> None:
        with self.tc.assertRaises(PortableKernelError) as caught:
            self.run(command_type, payload)
        self.tc.assertEqual(caught.exception.code, code)
        self.tick -= 1


def session(tc: unittest.TestCase, kind: str = "physical", label: str = "Ключи") -> Session:
    return Session(tc, create_case_with_kind("case-1", label, T0, kind))


def search_session(tc: unittest.TestCase, kind: str = "physical") -> Session:
    s = session(tc, kind)
    s.run("set_mode", {"mode": "search"})
    return s


def recon_session(tc: unittest.TestCase, kind: str = "physical") -> Session:
    s = session(tc, kind)
    s.run("set_mode", {"mode": "reconstruction"})
    s.run("record_free_account", {"entry_id": "fa-1", "text": "Вышел из офиса."})
    return s


def event(event_id: str, label: str, precision: str, time: str | None) -> dict[str, object]:
    return {
        "id": event_id,
        "label": label,
        "statement_ids": [],
        "event_time": time,
        "time_precision": precision,
    }


def timeline(events: list[dict[str, object]]) -> dict[str, object]:
    return {"events": events, "last_supported_interaction_id": None, "first_noticed_missing_id": None}


def check(check_id: str, target: str, method: str, result: str = "not_found", based_on: list[str] | None = None) -> dict[str, object]:
    return {"check_id": check_id, "target": target, "method": method, "result": result, "based_on": based_on or []}


class MobileSliceContractTests(unittest.TestCase):
    def test_new_commands_are_part_of_the_portable_contract(self):
        self.assertIn("add_search_target", SUPPORTED_COMMAND_TYPES)
        self.assertIn("revise_free_account", SUPPORTED_COMMAND_TYPES)


class ItemKindTests(unittest.TestCase):
    def test_t01_blank_title_rejected(self):
        for label in ("", "   ", "\n\t"):
            with self.assertRaises(PortableKernelError) as caught:
                create_case_with_kind("case-1", label, T0, "physical")
            self.assertEqual(caught.exception.code, "MD_WEB_COMMAND_PAYLOAD")

    def test_t36_item_kind_default_and_invalid(self):
        physical = create_case_with_kind("case-1", "Ключи", T0, "physical")
        digital = create_case_with_kind("case-2", "Фото", T0, "digital")
        self.assertEqual(physical["constraints"], [])
        self.assertEqual(digital["constraints"], ["item_kind:digital"])
        self.assertEqual(item_kind_json(physical), "physical")
        self.assertEqual(item_kind_json(digital), "digital")
        with self.assertRaises(PortableKernelError) as caught:
            create_case_with_kind("case-3", "A", T0, "x")
        self.assertEqual(caught.exception.code, "MD_CASE_ITEM_KIND_INVALID")

    def test_t39_legacy_case_is_physical(self):
        self.assertEqual(item_kind_json(create_case("case-1", "ключи", T0)), "physical")

    def test_create_case_with_kind_matches_legacy_shape(self):
        legacy = create_case("case-1", "Ключи", T0)
        self.assertEqual(create_case_with_kind("case-1", "Ключи", T0, "physical"), legacy)


class FreeAccountTests(unittest.TestCase):
    def test_t03_free_account_and_revision_are_verbatim(self):
        s = session(self)
        s.run("set_mode", {"mode": "reconstruction"})
        text = "  ну…  вышел \n"
        s.run("record_free_account", {"entry_id": "fa-1", "text": text})
        revised = "  ну…  вышел \nи сел в машину"
        case = s.run("revise_free_account", {"entry_id": "fa-2", "text": revised})
        journal = case["interaction_journal"]
        self.assertEqual([e["entry_type"] for e in journal], ["free_account", "free_account_revision"])
        self.assertEqual([e["text"] for e in journal], [text, revised])
        self.assertEqual({e["mode"] for e in journal}, {"reconstruction"})
        self.assertEqual({e["author"] for e in journal}, {"user"})

    def test_revision_requires_existing_free_account(self):
        s = session(self)
        s.run("set_mode", {"mode": "reconstruction"})
        s.expect_error("MD_RECON_FREE_ACCOUNT_REQUIRED", "revise_free_account", {"entry_id": "fa-2", "text": "x"})

    def test_free_account_may_be_recorded_after_explicit_search_transition(self):
        s = search_session(self)
        case = s.run("record_free_account", {"entry_id": "fa-1", "text": "Рассказ"})
        self.assertEqual(case["interaction_journal"][-1]["mode"], "reconstruction")
        self.assertEqual(case["current_mode"], "search")

    def test_free_account_still_requires_selected_mode(self):
        s = session(self)
        s.expect_error("MD_RECON_MODE_REQUIRED", "record_free_account", {"entry_id": "fa-1", "text": "x"})


class StatementTests(unittest.TestCase):
    def test_t04_statement_requires_text_and_type(self):
        s = recon_session(self)
        base = {"statement_id": "s-1", "source": "user", "user_confirmation": True}
        s.expect_error("MD_WEB_COMMAND_PAYLOAD", "add_statement", {**base, "statement_type": "recollection", "original_text": "   "})
        s.expect_error("MD_WEB_COMMAND_PAYLOAD", "add_statement", {**base, "statement_type": "x", "original_text": "a"})


class TimelineTests(unittest.TestCase):
    def test_t05_unknown_time_event_is_unknown_interval(self):
        s = recon_session(self)
        case = s.run("rebuild_timeline", timeline([event("e-1", "Дорога", "unknown", None)]))
        self.assertEqual(case["timeline"]["unknown_intervals"], ["event:e-1"])
        self.assertEqual(case["timeline"]["contradictions"], [])

    def test_t06_invalid_clock_time_rejected(self):
        s = recon_session(self)
        for bad in ("25:99", "8", "08-00", "", "24:00"):
            s.expect_error("MD_RECON_EVENT_TIME_INVALID", "rebuild_timeline", timeline([event("e-1", "A", "exact", bad)]))
        s.expect_error("MD_RECON_EVENT_TIME_INVALID", "rebuild_timeline", timeline([event("e-1", "A", "approximate", None)]))
        s.expect_error("MD_RECON_EVENT_TIME_INVALID", "rebuild_timeline", timeline([event("e-1", "A", "unknown", "08:00")]))
        s.expect_error("MD_RECON_EVENT_TIME_INVALID", "rebuild_timeline", timeline([event("e-1", "A", "roughly", "08:00")]))
        ok = s.run("rebuild_timeline", timeline([event("e-1", "A", "exact", "00:00"), event("e-2", "B", "approximate", "23:59")]))
        self.assertEqual([e["event_time"] for e in ok["timeline"]["events"]], ["00:00", "23:59"])

    def test_iso_timestamps_remain_valid_for_0_4_0_cases(self):
        s = recon_session(self)
        case = s.run("rebuild_timeline", timeline([event("e-1", "A", "exact", "2026-09-12T08:00:00Z")]))
        self.assertEqual(case["timeline"]["events"][0]["event_time"], "2026-09-12T08:00:00Z")

    def test_t08_same_exact_time_different_labels_is_contradiction(self):
        s = recon_session(self)
        case = s.run(
            "rebuild_timeline",
            timeline([
                event("e-1", "Офис", "exact", "08:00"),
                event("e-2", "Кафе", "exact", "08:00"),
                event("e-3", "Дом", "exact", "09:00"),
            ]),
        )
        self.assertEqual(case["timeline"]["contradictions"], ["MD_TIME_SAME_EXACT_TIME:08:00"])

    def test_same_label_at_same_exact_time_is_not_a_contradiction(self):
        s = recon_session(self)
        case = s.run(
            "rebuild_timeline",
            timeline([event("e-1", "Офис", "exact", "08:00"), event("e-2", "офис", "exact", "08:00")]),
        )
        self.assertEqual(case["timeline"]["contradictions"], [])

    def test_t09_approximate_times_do_not_contradict(self):
        s = recon_session(self)
        case = s.run(
            "rebuild_timeline",
            timeline([event("e-1", "Офис", "approximate", "08:00"), event("e-2", "Кафе", "approximate", "08:00")]),
        )
        self.assertEqual(case["timeline"]["contradictions"], [])

    def test_timeline_can_be_extended_after_transition_to_search(self):
        s = recon_session(self)
        s.run("set_mode", {"mode": "search"})
        case = s.run("rebuild_timeline", timeline([event("e-1", "Кафе", "approximate", "08:40")]))
        self.assertEqual(case["current_mode"], "search")
        self.assertEqual(len(case["timeline"]["events"]), 1)


class SearchTests(unittest.TestCase):
    def test_t10_check_requires_search_mode(self):
        s = recon_session(self)
        s.expect_error("MD_SEARCH_MODE_REQUIRED", "record_search_check", check("c-1", "A", "hand"))
        s.expect_error("MD_SEARCH_MODE_REQUIRED", "add_search_target", {"statement_id": "t-1", "target": "A"})

    def test_t11_check_keeps_method_and_marks_target(self):
        s = search_session(self)
        case = s.run("add_search_target", {"statement_id": "t-1", "target": "Рюкзак"})
        candidate = case["candidates"][0]
        self.assertEqual(candidate["target"], "Рюкзак")
        self.assertEqual(candidate["check_state"], "unchecked")
        self.assertEqual(case["statements"][0]["statement_type"], "search_suggestion")
        self.assertEqual(case["statements"][0]["source"], "user")
        case = s.run("record_search_check", check("c-1", "Рюкзак", "visual", "not_found", [candidate["id"]]))
        self.assertEqual(case["search_checks"][0]["method"], "visual")
        self.assertEqual(case["candidates"][0]["check_state"], "checked")
        case = s.run("record_search_check", check("c-2", "Рюкзак", "hand", "partial", [candidate["id"]]))
        self.assertEqual(case["candidates"][0]["check_state"], "partial")

    def test_t17_duplicate_target_rejected(self):
        s = search_session(self)
        s.run("add_search_target", {"statement_id": "t-1", "target": "Карман ёлки"})
        s.expect_error("MD_SEARCH_TARGET_EXISTS", "add_search_target", {"statement_id": "t-2", "target": "  карман   елки "})
        s.expect_error("MD_WEB_COMMAND_PAYLOAD", "add_search_target", {"statement_id": "t-3", "target": "   "})

    def test_t37_methods_depend_on_item_kind(self):
        digital = search_session(self, "digital")
        case = digital.run("record_search_check", check("c-1", "Корзина", "trash"))
        self.assertEqual(case["search_checks"][0]["method"], "trash")
        digital.expect_error("MD_SEARCH_METHOD_KIND", "record_search_check", check("c-2", "A", "flashlight"))
        digital.expect_error("MD_SEARCH_METHOD_KIND", "record_search_check", check("c-3", "A", "tactile"))
        physical = search_session(self, "physical")
        physical.expect_error("MD_SEARCH_METHOD_KIND", "record_search_check", check("c-1", "A", "trash"))
        for method in ("visual", "hand", "flashlight", "opened", "moved", "asked", "tactile", "reported_check"):
            physical.run("record_search_check", check(f"c-{method}", "A", method))
        for method in ("name_search", "date_filter", "browsed", "trash", "shared", "asked"):
            digital.run("record_search_check", check(f"d-{method}", "A", method))

    def test_t16_closed_case_is_immutable(self):
        s = search_session(self)
        s.run("close_unresolved", {"outcome": {}})
        s.expect_error("MD_CASE_TERMINAL", "add_search_target", {"statement_id": "t-1", "target": "X"})
        s.expect_error("MD_CASE_TERMINAL", "revise_free_account", {"entry_id": "fa-2", "text": "x"})

    def test_t18_pause_and_resume(self):
        s = search_session(self)
        self.assertEqual(s.run("pause")["lifecycle"], "paused")
        self.assertEqual(s.run("resume")["lifecycle"], "active")


if __name__ == "__main__":
    unittest.main()
