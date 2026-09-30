from __future__ import annotations

import json
import random
from collections.abc import Callable

from .portable_intrinsics import PortableKernelError
from .portable_kernel import (
    apply_command,
    build_checklist_proposal_json,
    create_case,
    create_case_with_kind,
    item_kind_json,
    select_next_action_json,
)

SEED = 303001


def _command(
    case: dict[str, object],
    command_type: str,
    *,
    command_id: str,
    now: str,
    payload: dict[str, object] | None = None,
    expected_updated_at: str | None = None,
) -> dict[str, object]:
    expected = expected_updated_at
    if expected is None:
        value = case["updated_at"]
        if not isinstance(value, str):
            raise AssertionError("fixture case updated_at must be a string")
        expected = value
    return {
        "command_id": command_id,
        "expected_updated_at": expected,
        "command_type": command_type,
        "now": now,
        "payload": payload or {},
    }


def _candidate(
    candidate_id: str,
    *,
    urgency: str = "normal",
    basis: str = "episode",
    route: str = "direct",
    state: str = "unchecked",
    effort: str = "low",
    safety: str = "safe",
) -> dict[str, object]:
    return {
        "id": candidate_id,
        "target": f"target-{candidate_id}",
        "route_relation": route,
        "check_state": state,
        "effort": effort,
        "safety": safety,
        "urgency_relevance": urgency,
        "basis": basis,
        "based_on": [],
        "rationale": [],
    }


def _capture(call: Callable[[], object]) -> dict[str, object]:
    try:
        return {"result": call()}
    except PortableKernelError as exc:
        return {"error_code": exc.code}


def _vector(vector_id: str, operation: str, input_value: dict[str, object]) -> dict[str, object]:
    if operation == "create_case":
        expected = _capture(
            lambda: create_case(
                str(input_value["case_id"]),
                str(input_value["item_label"]),
                str(input_value["now"]),
            )
        )
    elif operation == "create_case_with_kind":
        expected = _capture(
            lambda: create_case_with_kind(
                str(input_value["case_id"]),
                str(input_value["item_label"]),
                str(input_value["now"]),
                str(input_value["item_kind"]),
            )
        )
    elif operation == "item_kind":
        kind_case = input_value["case"]
        if not isinstance(kind_case, dict):
            raise AssertionError("item_kind vector shape")
        expected = _capture(lambda: item_kind_json(kind_case))
    elif operation == "command":
        raw_case = input_value["case"]
        raw_command = input_value["command"]
        if not isinstance(raw_case, dict) or not isinstance(raw_command, dict):
            raise AssertionError("command vector shape")
        case: dict[str, object] = {}
        for key, value in raw_case.items():
            if not isinstance(key, str):
                raise AssertionError("command case keys must be strings")
            case[key] = value
        command: dict[str, object] = {}
        for key, value in raw_command.items():
            if not isinstance(key, str):
                raise AssertionError("command envelope keys must be strings")
            command[key] = value
        expected = _capture(lambda: apply_command(case, command))
    elif operation == "proposal":
        proposal_case = input_value["case"]
        mode = input_value["mode"]
        if not isinstance(proposal_case, dict) or not isinstance(mode, str):
            raise AssertionError("proposal vector shape")
        expected = _capture(lambda: build_checklist_proposal_json(proposal_case, mode))
    elif operation == "planner":
        candidates = input_value["candidates"]
        if not isinstance(candidates, list):
            raise AssertionError("planner vector shape")
        expected = _capture(lambda: select_next_action_json(candidates))
    else:
        raise AssertionError(f"unsupported fixture operation: {operation}")
    return {"id": vector_id, "operation": operation, "input": input_value, "expected": expected}


def _mobile_vectors(reconstruction_with_free_account: dict[str, object]) -> list[dict[str, object]]:
    """0.5.0 Glass Modern mobile slice (ADR 016)."""
    vectors: list[dict[str, object]] = []
    vectors.append(
        _vector(
            "mobile_create_digital_case",
            "create_case_with_kind",
            {"case_id": "case-photo", "item_label": "Фото с дня рождения", "now": "2026-09-30T10:00:00Z", "item_kind": "digital"},
        )
    )
    vectors.append(
        _vector(
            "mobile_create_invalid_kind",
            "create_case_with_kind",
            {"case_id": "case-x", "item_label": "A", "now": "2026-09-30T10:00:00Z", "item_kind": "x"},
        )
    )
    digital = create_case_with_kind("case-photo", "Фото с дня рождения", "2026-09-30T10:00:00Z", "digital")
    vectors.append(_vector("mobile_item_kind_digital", "item_kind", {"case": digital}))

    set_search = _command(digital, "set_mode", command_id="cmd-m-search", now="2026-09-30T10:00:01Z", payload={"mode": "search"})
    digital_search = apply_command(digital, set_search)
    add_target = _command(
        digital_search,
        "add_search_target",
        command_id="cmd-m-target",
        now="2026-09-30T10:00:02Z",
        payload={"statement_id": "target-trash", "target": "Телефон → Фото → Недавно удалённые"},
    )
    vectors.append(_vector("mobile_add_search_target", "command", {"case": digital_search, "command": add_target}))
    with_target = apply_command(digital_search, add_target)
    duplicate = _command(
        with_target,
        "add_search_target",
        command_id="cmd-m-target-dup",
        now="2026-09-30T10:00:03Z",
        payload={"statement_id": "target-dup", "target": "телефон → фото → недавно  удалённые"},
    )
    vectors.append(_vector("mobile_add_search_target_duplicate", "command", {"case": with_target, "command": duplicate}))
    vectors.append(
        _vector(
            "mobile_add_search_target_requires_search",
            "command",
            {
                "case": reconstruction_with_free_account,
                "command": _command(
                    reconstruction_with_free_account,
                    "add_search_target",
                    command_id="cmd-m-target-recon",
                    now="2026-09-30T10:00:04Z",
                    payload={"statement_id": "target-recon", "target": "Рюкзак"},
                ),
            },
        )
    )
    vectors.append(
        _vector(
            "mobile_check_requires_search",
            "command",
            {
                "case": reconstruction_with_free_account,
                "command": _command(
                    reconstruction_with_free_account,
                    "record_search_check",
                    command_id="cmd-m-check-recon",
                    now="2026-09-30T10:00:05Z",
                    payload={"check_id": "check-recon", "target": "Рюкзак", "method": "hand", "result": "not_found"},
                ),
            },
        )
    )
    digital_check = _command(
        with_target,
        "record_search_check",
        command_id="cmd-m-check-trash",
        now="2026-09-30T10:00:06Z",
        payload={
            "check_id": "check-trash",
            "target": "Телефон → Фото → Недавно удалённые",
            "method": "trash",
            "result": "not_found",
            "based_on": ["candidate-target-trash"],
        },
    )
    vectors.append(_vector("mobile_digital_check_method", "command", {"case": with_target, "command": digital_check}))
    vectors.append(
        _vector(
            "mobile_digital_rejects_physical_method",
            "command",
            {
                "case": with_target,
                "command": _command(
                    with_target,
                    "record_search_check",
                    command_id="cmd-m-check-flash",
                    now="2026-09-30T10:00:07Z",
                    payload={"check_id": "check-flash", "target": "Облако", "method": "flashlight", "result": "not_found"},
                ),
            },
        )
    )
    vectors.append(
        _vector(
            "mobile_revise_free_account",
            "command",
            {
                "case": reconstruction_with_free_account,
                "command": _command(
                    reconstruction_with_free_account,
                    "revise_free_account",
                    command_id="cmd-m-revise",
                    now="2026-09-30T10:00:08Z",
                    payload={"entry_id": "free-2", "text": "Вышел из офиса, зашёл в кафе.\nПотом сел в машину."},
                ),
            },
        )
    )
    vectors.append(
        _vector(
            "mobile_timeline_unknown_and_same_time_contradiction",
            "command",
            {
                "case": reconstruction_with_free_account,
                "command": _command(
                    reconstruction_with_free_account,
                    "rebuild_timeline",
                    command_id="cmd-m-timeline",
                    now="2026-09-30T10:00:09Z",
                    payload={
                        "events": [
                            {"id": "ev-office", "label": "Офис", "statement_ids": [], "event_time": "08:00", "time_precision": "exact"},
                            {"id": "ev-cafe", "label": "Кафе", "statement_ids": [], "event_time": "08:00", "time_precision": "exact"},
                            {"id": "ev-cafe2", "label": "Кафе", "statement_ids": [], "event_time": "08:40", "time_precision": "approximate"},
                            {"id": "ev-road", "label": "Дорога домой", "statement_ids": [], "event_time": None, "time_precision": "unknown"},
                        ],
                        "last_supported_interaction_id": None,
                        "first_noticed_missing_id": None,
                    },
                ),
            },
        )
    )
    vectors.append(
        _vector(
            "mobile_timeline_invalid_clock_time",
            "command",
            {
                "case": reconstruction_with_free_account,
                "command": _command(
                    reconstruction_with_free_account,
                    "rebuild_timeline",
                    command_id="cmd-m-timeline-bad",
                    now="2026-09-30T10:00:10Z",
                    payload={
                        "events": [
                            {"id": "ev-bad", "label": "A", "statement_ids": [], "event_time": "25:99", "time_precision": "exact"},
                        ],
                        "last_supported_interaction_id": None,
                        "first_noticed_missing_id": None,
                    },
                ),
            },
        )
    )
    return vectors


def generate_vectors() -> list[dict[str, object]]:
    vectors: list[dict[str, object]] = []

    vectors.append(
        _vector(
            "create-case-unicode",
            "create_case",
            {"case_id": "case-ключи-😀", "item_label": "Ключи 🔑", "now": "2026-09-10T17:30:00Z"},
        )
    )

    base = create_case("case-1", "ключи", "2026-09-10T17:31:00Z")
    set_search = _command(
        base,
        "set_mode",
        command_id="cmd-set-search",
        now="2026-09-10T17:31:01Z",
        payload={"mode": "search"},
    )
    vectors.append(_vector("command-set-mode", "command", {"case": base, "command": set_search}))
    search = apply_command(base, set_search)

    set_reconstruction = _command(
        base,
        "set_mode",
        command_id="cmd-set-reconstruction",
        now="2026-09-10T17:31:02Z",
        payload={"mode": "reconstruction"},
    )
    reconstruction = apply_command(base, set_reconstruction)

    free_account = _command(
        reconstruction,
        "record_free_account",
        command_id="cmd-free-account",
        now="2026-09-10T17:31:03Z",
        payload={
            "entry_id": "free-1",
            "text": "Я пришёл домой и положил ключи, но не помню куда.",
        },
    )
    vectors.append(
        _vector(
            "reconstruction_record_free_account",
            "command",
            {"case": reconstruction, "command": free_account},
        )
    )
    reconstruction_with_free_account = apply_command(reconstruction, free_account)

    statement_requires_free_account = _command(
        reconstruction,
        "add_statement",
        command_id="cmd-statement-requires-free-account",
        now="2026-09-10T17:31:04Z",
        payload={
            "statement_id": "stmt-before-free",
            "source": "user",
            "statement_type": "recollection",
            "original_text": "Ключи были у двери",
            "event_time": "2026-09-10T17:10:00Z",
            "user_confirmation": True,
            "supporting_evidence_ids": [],
            "limitations": [],
        },
    )
    vectors.append(
        _vector(
            "reconstruction_statement_requires_free_account",
            "command",
            {"case": reconstruction, "command": statement_requires_free_account},
        )
    )

    known_statement = _command(
        reconstruction_with_free_account,
        "add_statement",
        command_id="cmd-timeline-known",
        now="2026-09-10T17:31:05Z",
        payload={
            "statement_id": "stmt-timeline-known",
            "source": "user",
            "statement_type": "recollection",
            "original_text": "Последний раз держал ключи у двери",
            "event_time": "2026-09-10T17:10:00Z",
            "user_confirmation": True,
            "supporting_evidence_ids": [],
            "limitations": [],
        },
    )
    reconstruction_known = apply_command(reconstruction_with_free_account, known_statement)
    unknown_statement = _command(
        reconstruction_known,
        "add_statement",
        command_id="cmd-timeline-unknown",
        now="2026-09-10T17:31:06Z",
        payload={
            "statement_id": "stmt-timeline-unknown",
            "source": "user",
            "statement_type": "observation",
            "original_text": "Позже заметил, что ключей нет",
            "event_time": None,
            "user_confirmation": True,
            "supporting_evidence_ids": [],
            "limitations": ["точное время неизвестно"],
        },
    )
    reconstruction_unknown = apply_command(reconstruction_known, unknown_statement)
    rebuild_unknowns = _command(
        reconstruction_unknown,
        "rebuild_timeline",
        command_id="cmd-rebuild-unknowns",
        now="2026-09-10T17:31:07Z",
        payload={
            "events": [
                {
                    "id": "event-last-supported",
                    "label": "Последний подтверждённый контакт с ключами",
                    "statement_ids": ["stmt-timeline-known"],
                    "event_time": "2026-09-10T17:10:00Z",
                    "time_precision": "approximate",
                }
            ],
            "last_supported_interaction_id": "stmt-timeline-known",
            "first_noticed_missing_id": None,
        },
    )
    vectors.append(
        _vector(
            "reconstruction_rebuild_timeline_unknowns",
            "command",
            {"case": reconstruction_unknown, "command": rebuild_unknowns},
        )
    )
    reconstruction_with_timeline = apply_command(reconstruction_unknown, rebuild_unknowns)

    contradiction_last = _command(
        reconstruction_with_free_account,
        "add_statement",
        command_id="cmd-contradiction-last",
        now="2026-09-10T17:31:08Z",
        payload={
            "statement_id": "stmt-contradiction-last",
            "source": "user",
            "statement_type": "recollection",
            "original_text": "Последний контакт был позже",
            "event_time": "2026-09-10T17:20:00Z",
            "user_confirmation": True,
            "supporting_evidence_ids": [],
            "limitations": [],
        },
    )
    contradiction_case = apply_command(reconstruction_with_free_account, contradiction_last)
    contradiction_missing = _command(
        contradiction_case,
        "add_statement",
        command_id="cmd-contradiction-missing",
        now="2026-09-10T17:31:09Z",
        payload={
            "statement_id": "stmt-contradiction-missing",
            "source": "user",
            "statement_type": "observation",
            "original_text": "Пропажу заметил раньше",
            "event_time": "2026-09-10T17:15:00Z",
            "user_confirmation": True,
            "supporting_evidence_ids": [],
            "limitations": [],
        },
    )
    contradiction_case = apply_command(contradiction_case, contradiction_missing)
    rebuild_contradiction = _command(
        contradiction_case,
        "rebuild_timeline",
        command_id="cmd-rebuild-contradiction",
        now="2026-09-10T17:31:10Z",
        payload={
            "events": [],
            "last_supported_interaction_id": "stmt-contradiction-last",
            "first_noticed_missing_id": "stmt-contradiction-missing",
        },
    )
    vectors.append(
        _vector(
            "reconstruction_rebuild_timeline_contradiction",
            "command",
            {"case": contradiction_case, "command": rebuild_contradiction},
        )
    )

    transition_to_search = _command(
        reconstruction_with_timeline,
        "set_mode",
        command_id="cmd-reconstruction-to-search",
        now="2026-09-10T17:31:11Z",
        payload={"mode": "search"},
    )
    vectors.append(
        _vector(
            "reconstruction_transition_to_search_preserves_evidence",
            "command",
            {"case": reconstruction_with_timeline, "command": transition_to_search},
        )
    )

    reconstruction_statement = _command(
        reconstruction,
        "add_statement",
        command_id="cmd-recollection",
        now="2026-09-10T17:31:03Z",
        payload={
            "statement_id": "stmt-recollection",
            "source": "user",
            "statement_type": "recollection",
            "original_text": "Помню, что держал ключи у двери",
        },
    )
    vectors.append(
        _vector(
            "command-add-recollection",
            "command",
            {"case": reconstruction, "command": reconstruction_statement},
        )
    )

    search_suggestion = _command(
        search,
        "add_statement",
        command_id="cmd-search-suggestion",
        now="2026-09-10T17:31:04Z",
        payload={
            "statement_id": "stmt-bag",
            "source": "user",
            "statement_type": "search_suggestion",
            "original_text": "Карман синего рюкзака",
        },
    )
    vectors.append(
        _vector("command-add-search-suggestion", "command", {"case": search, "command": search_suggestion})
    )
    with_candidate = apply_command(search, search_suggestion)

    duplicate_unicode = _command(
        with_candidate,
        "add_statement",
        command_id="cmd-duplicate-unicode",
        now="2026-09-10T17:31:05Z",
        payload={
            "statement_id": "stmt-bag-2",
            "source": "user",
            "statement_type": "search_suggestion",
            "original_text": "  КАРМАН\u00a0СИНЕГО   РЮКЗАКА ",
        },
    )
    vectors.append(
        _vector(
            "command-search-suggestion-unicode-whitespace-dedup",
            "command",
            {"case": with_candidate, "command": duplicate_unicode},
        )
    )

    check = _command(
        with_candidate,
        "record_search_check",
        command_id="cmd-check",
        now="2026-09-10T17:31:06Z",
        payload={
            "check_id": "check-bag",
            "target": "Карман синего рюкзака",
            "based_on": ["candidate-stmt-bag"],
            "result": "not_found",
        },
    )
    vectors.append(_vector("command-record-reported-check", "command", {"case": with_candidate, "command": check}))
    checked = apply_command(with_candidate, check)

    partial_check = _command(
        with_candidate,
        "record_search_check",
        command_id="cmd-partial-check",
        now="2026-09-10T17:31:07Z",
        payload={
            "check_id": "check-partial",
            "target": "Карман синего рюкзака",
            "method": "glance",
            "based_on": ["candidate-stmt-bag"],
            "result": "partial",
            "inaccessible_parts": ["внутренний карман"],
        },
    )
    vectors.append(_vector("command-record-partial-check", "command", {"case": with_candidate, "command": partial_check}))
    partial = apply_command(with_candidate, partial_check)

    refine = _command(
        checked,
        "refine_search_check",
        command_id="cmd-refine",
        now="2026-09-10T17:31:08Z",
        payload={"check_id": "check-bag", "method": "empty_and_check", "inaccessible_parts": []},
    )
    vectors.append(_vector("command-refine-check", "command", {"case": checked, "command": refine}))

    reject = _command(
        with_candidate,
        "reject_next_action",
        command_id="cmd-reject",
        now="2026-09-10T17:31:09Z",
        payload={"feedback_id": "feedback-1", "candidate_id": "candidate-stmt-bag", "reason": "irrelevant"},
    )
    vectors.append(_vector("command-reject-action", "command", {"case": with_candidate, "command": reject}))
    rejected = apply_command(with_candidate, reject)

    pause = _command(search, "pause", command_id="cmd-pause", now="2026-09-10T17:31:10Z")
    vectors.append(_vector("command-pause", "command", {"case": search, "command": pause}))
    paused = apply_command(search, pause)
    resume = _command(paused, "resume", command_id="cmd-resume", now="2026-09-10T17:31:11Z")
    vectors.append(_vector("command-resume", "command", {"case": paused, "command": resume}))

    close_found = _command(
        search,
        "close_found",
        command_id="cmd-close-found",
        now="2026-09-10T17:31:12Z",
        payload={"outcome": {"found_context": "elsewhere_unplanned", "note": "нашлось у двери"}},
    )
    vectors.append(_vector("command-close-found", "command", {"case": search, "command": close_found}))
    closed_found = apply_command(search, close_found)

    close_unresolved = _command(
        search,
        "close_unresolved",
        command_id="cmd-close-unresolved",
        now="2026-09-10T17:31:13Z",
        payload={"outcome": {"reason": "stopped"}},
    )
    vectors.append(
        _vector("command-close-unresolved", "command", {"case": search, "command": close_unresolved})
    )

    vectors.append(
        _vector(
            "failure-stale-command",
            "command",
            {
                "case": search,
                "command": _command(
                    search,
                    "pause",
                    command_id="cmd-stale",
                    now="2026-09-10T17:31:14Z",
                    expected_updated_at="2020-01-01T00:00:00Z",
                ),
            },
        )
    )
    vectors.append(
        _vector(
            "failure-forbidden-probability-nested",
            "command",
            {
                "case": search,
                "command": _command(
                    search,
                    "close_found",
                    command_id="cmd-probability",
                    now="2026-09-10T17:31:15Z",
                    payload={"outcome": {"nested": {"probability": 80}}},
                ),
            },
        )
    )
    vectors.append(
        _vector(
            "failure-float",
            "command",
            {
                "case": search,
                "command": _command(
                    search,
                    "close_found",
                    command_id="cmd-float",
                    now="2026-09-10T17:31:16Z",
                    payload={"outcome": {"score": 0.25}},
                ),
            },
        )
    )
    vectors.append(
        _vector(
            "failure-terminal-mutation",
            "command",
            {
                "case": closed_found,
                "command": _command(
                    closed_found,
                    "pause",
                    command_id="cmd-terminal",
                    now="2026-09-10T17:31:17Z",
                ),
            },
        )
    )
    vectors.append(
        _vector(
            "failure-invalid-refinement-method",
            "command",
            {
                "case": checked,
                "command": _command(
                    checked,
                    "refine_search_check",
                    command_id="cmd-invalid-method",
                    now="2026-09-10T17:31:18Z",
                    payload={"check_id": "check-bag", "method": "inaccessible", "inaccessible_parts": []},
                ),
            },
        )
    )

    vectors.extend(_mobile_vectors(reconstruction_with_free_account))

    vectors.append(_vector("proposal-reconstruction", "proposal", {"case": reconstruction, "mode": "reconstruction"}))
    vectors.append(_vector("proposal-search-next-action", "proposal", {"case": with_candidate, "mode": "search"}))
    vectors.append(_vector("proposal-rejected-excluded", "proposal", {"case": rejected, "mode": "search"}))
    vectors.append(_vector("proposal-partial-clarification", "proposal", {"case": partial, "mode": "search"}))
    vectors.append(_vector("proposal-empty-search", "proposal", {"case": search, "mode": "search"}))

    planner_pairs = [
        (
            "planner-urgency",
            _candidate("normal", urgency="normal"),
            _candidate("urgent", urgency="high", basis="generic", route="none", state="checked", effort="high"),
        ),
        (
            "planner-basis",
            _candidate("generic", basis="generic"),
            _candidate("episode", basis="episode"),
        ),
        (
            "planner-route",
            _candidate("indirect", route="indirect"),
            _candidate("direct", route="direct"),
        ),
        (
            "planner-check-state",
            _candidate("checked", state="checked"),
            _candidate("partial", state="partial"),
        ),
        (
            "planner-effort",
            _candidate("high", effort="high"),
            _candidate("low", effort="low"),
        ),
        (
            "planner-id-unicode",
            _candidate("😀"),
            _candidate("𐐀"),
        ),
        (
            "planner-unsafe-excluded",
            _candidate("unsafe", safety="unsafe", urgency="high"),
            _candidate("safe", safety="safe"),
        ),
    ]
    for vector_id, left, right in planner_pairs:
        vectors.append(_vector(vector_id, "planner", {"candidates": [left, right]}))

    rng = random.Random(SEED)
    categories = {
        "urgency": ["high", "normal"],
        "basis": ["episode", "habit", "generic"],
        "route": ["direct", "indirect", "none"],
        "state": ["unchecked", "partial", "checked"],
        "effort": ["low", "medium", "high"],
        "safety": ["safe", "caution"],
    }
    for index in range(24):
        candidates: list[dict[str, object]] = []
        for candidate_index in range(4):
            candidates.append(
                _candidate(
                    f"seed-{index:02d}-{candidate_index}",
                    urgency=rng.choice(categories["urgency"]),
                    basis=rng.choice(categories["basis"]),
                    route=rng.choice(categories["route"]),
                    state=rng.choice(categories["state"]),
                    effort=rng.choice(categories["effort"]),
                    safety=rng.choice(categories["safety"]),
                )
            )
        vectors.append(_vector(f"planner-seeded-{index:02d}", "planner", {"candidates": candidates}))

    return vectors


def main() -> None:
    print(json.dumps(generate_vectors(), ensure_ascii=False, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
