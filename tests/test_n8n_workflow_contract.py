import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "integrations/n8n/mind-detective-assistant.workflow.json"
SERVER_TS = ROOT / "apps/web/app/lib/assistant/server.ts"


class N8nWorkflowContractTests(unittest.TestCase):
    """ADR 017: the shipped n8n workflow matches the app transport contract."""

    def setUp(self) -> None:
        self.workflow = json.loads(WORKFLOW.read_text(encoding="utf-8"))
        self.nodes = {node["name"]: node for node in self.workflow["nodes"]}

    def webhook(self, path: str) -> dict:
        for node in self.nodes.values():
            if node["type"] == "n8n-nodes-base.webhook" and node["parameters"]["path"] == path:
                return node
        self.fail(f"missing webhook {path}")

    def test_webhook_paths_match_the_app_endpoints(self) -> None:
        server = SERVER_TS.read_text(encoding="utf-8")
        for path in ("md-propose", "md-transcribe"):
            self.assertIn(f"/webhook/{path}", server)
            hook = self.webhook(path)
            self.assertEqual(hook["parameters"]["httpMethod"], "POST")
            self.assertEqual(hook["parameters"]["authentication"], "headerAuth")
            self.assertEqual(hook["parameters"]["responseMode"], "responseNode")

    def test_transcribe_reads_the_indexed_binary_property(self) -> None:
        # Webhook v2 stores multipart files as `${binaryPropertyName}${index}`.
        prefix = self.webhook("md-transcribe")["parameters"]["options"]["binaryPropertyName"]
        whisper = self.nodes["STT · Whisper"]
        fields = [
            parameter
            for parameter in whisper["parameters"]["bodyParameters"]["parameters"]
            if parameter.get("parameterType") == "formBinaryData"
        ]
        self.assertEqual([field["inputDataFieldName"] for field in fields], [f"{prefix}0"])

    def test_model_failures_map_to_502_and_no_execution_data_is_kept(self) -> None:
        for node_name in ("LLM · chat completion", "STT · Whisper"):
            self.assertEqual(self.nodes[node_name]["onError"], "continueErrorOutput")
        for node_name in ("Respond · 502", "Respond · 502 stt"):
            self.assertEqual(self.nodes[node_name]["parameters"]["options"]["responseCode"], 502)
        settings = self.workflow["settings"]
        self.assertEqual(settings["saveDataSuccessExecution"], "none")
        self.assertEqual(settings["saveDataErrorExecution"], "none")

    def test_propose_forwards_only_the_prompt(self) -> None:
        body = self.nodes["LLM · chat completion"]["parameters"]["jsonBody"]
        self.assertIn("$json.body.prompt", body)
        self.assertNotIn("$json.body.case", body)


if __name__ == "__main__":
    unittest.main()
