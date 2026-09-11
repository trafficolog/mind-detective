from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CONTRACTS = ROOT / "apps/web/app/lib/eval/contracts.ts"
ANALYZER = ROOT / "scripts/analyze_evaluation.py"

OBSOLETE_EVENTS = {
    "next_action_started",
    "pending_command_started",
    "pending_command_retried",
    "pending_command_failed",
    "found_context_recorded",
}

METRIC_EVENT_EMITTERS = {
    "case_started": "apps/web/app/lib/eval/store.ts",
    "next_action_shown": "apps/web/app/pages/cases/[id].vue",
    "next_action_rejected": "apps/web/app/pages/cases/[id].vue",
    "check_finished": "apps/web/app/pages/cases/[id].vue",
    "found": "apps/web/app/lib/eval/store.ts",
    "case_closed_unresolved": "apps/web/app/lib/eval/store.ts",
    "case_abandoned": "apps/web/app/lib/eval/store.ts",
    "duplicate_check_detected": "apps/web/app/pages/cases/[id].vue",
    "post_case_rating": "apps/web/app/components/evaluation/EvaluationPostCaseRatings.vue",
    "proposal_safety_annotation": "apps/web/app/pages/evaluation/observer/[sessionId].vue",
    "handoff_rubric": "apps/web/app/pages/evaluation/observer/[sessionId].vue",
    "assistant_offline_fallback": "apps/web/app/pages/cases/[id].vue",
    "local_execution_failed": "apps/web/app/pages/cases/[id].vue",
}


def declared_events() -> set[str]:
    text = CONTRACTS.read_text(encoding="utf-8")
    block = text.split("export type EvalEventName =", 1)[1].split("export type EvaluationProtocol", 1)[0]
    return set(re.findall(r"'([a-z0-9_]+)'", block))


class EvaluationEventPathTests(unittest.TestCase):
    def test_obsolete_unemitted_events_are_not_part_of_the_v1_vocabulary(self) -> None:
        events = declared_events()
        self.assertEqual(events & OBSOLETE_EVENTS, set())

    def test_each_decision_metric_event_has_a_production_emitter_and_analyzer_consumer(self) -> None:
        events = declared_events()
        analyzer = ANALYZER.read_text(encoding="utf-8")
        for event, emitter_path in METRIC_EVENT_EMITTERS.items():
            with self.subTest(event=event):
                self.assertIn(event, events)
                emitter = (ROOT / emitter_path).read_text(encoding="utf-8")
                self.assertRegex(emitter, rf"['\"]{re.escape(event)}['\"]")
                self.assertRegex(analyzer, rf"['\"]{re.escape(event)}['\"]")


if __name__ == "__main__":
    unittest.main()
