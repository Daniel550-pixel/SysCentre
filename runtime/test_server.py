import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import server
from policy import evaluate_command, policy_catalog


class RuntimeTests(unittest.TestCase):
    def test_repository_architecture_inventory_is_evidence_backed_and_unique(self):
        inventory = server.repository_architecture_inventory()
        projects = inventory["repositories"]
        project_ids = [item["project_id"] for item in projects]
        self.assertEqual(len(projects), 28)
        self.assertEqual(len(project_ids), len(set(project_ids)))
        self.assertIn("archos-repo", project_ids)
        self.assertIn("networklab", project_ids)
        allowed_statuses = {"source-verified", "source-limited", "documentation-only", "empty"}
        for project in projects:
            self.assertIn(project["architecture_status"], allowed_statuses)
            self.assertIsInstance(project["layers"], list)
            snapshot = project["source_snapshot"]
            self.assertIn("commit", snapshot)
            self.assertIn("tree_sha", snapshot)
            self.assertRegex(snapshot["source_checked_at"], r"^\\d{4}-\\d{2}-\\d{2}$")
            self.assertIsInstance(project["repository_hygiene_findings"], list)
            self.assertFalse(snapshot["deployment_verified"])
            self.assertFalse(snapshot["runtime_health_verified"])

        by_id = {item["project_id"]: item for item in projects}
        radar = by_id["ai-venture-radar"]
        self.assertEqual(radar["architecture_status"], "source-limited")
        self.assertTrue(any("core/scoring.py" in layer["evidence_paths"] for layer in radar["layers"]))
        self.assertTrue(any("core/adversarial.py" in layer["evidence_paths"] for layer in radar["layers"]))

        factory = by_id["the-factory"]
        self.assertEqual(factory["architecture_status"], "source-verified")
        self.assertTrue(any("factory/kernel/policy.py" in layer["evidence_paths"] for layer in factory["layers"]))
        self.assertTrue(any("factory/kernel/events.py" in layer["evidence_paths"] for layer in factory["layers"]))

        secret_findings = by_id["finsight-global-ai-dashboard"]["repository_hygiene_findings"]
        self.assertTrue(any(".env" in finding["evidence_paths"] and finding["severity"] == "high" for finding in secret_findings))
        self.assertNotIn("API_KEY=", " ".join(finding["description"] for finding in secret_findings))

        business_findings = by_id["business-os"]["repository_hygiene_findings"]
        self.assertTrue(any(".business-os-data/security-events.jsonl" in finding["evidence_paths"] for finding in business_findings))

        empty_projects = [item for item in projects if item["architecture_status"] == "empty"]
        self.assertEqual({item["project_id"] for item in empty_projects}, {"ai-trading-dashboard-2", "ai-os-global-wealth-engine"})
        for project in empty_projects:
            self.assertIsNone(project["source_snapshot"]["commit"])
            self.assertIsNone(project["source_snapshot"]["tree_sha"])

    def test_status_contains_policy_and_persistent_ledger_state(self):
        status = server.runtime_status()
        self.assertEqual(status["state"], "online")
        self.assertEqual(status["policy_gate"], "enabled")
        self.assertEqual(status["event_ledger"], "sqlite")
        self.assertTrue(status["event_ledger_path"])

    def test_cors_allows_static_fallback_and_local_dev_origins_only(self):
        self.assertTrue(server._origin_is_allowed("https://daniel550-pixel.github.io"))
        self.assertTrue(server._origin_is_allowed("http://127.0.0.1:5173"))
        self.assertTrue(server._origin_is_allowed("http://localhost:5173"))
        self.assertFalse(server._origin_is_allowed("https://example.org"))
        self.assertFalse(server._origin_is_allowed("*"))
        self.assertFalse(server._origin_is_allowed(None))

    def test_send_json_sets_cors_headers_for_allowed_origin(self):
        origin = "https://daniel550-pixel.github.io"
        handler = object.__new__(server.Handler)
        handler.headers = {
            "Origin": origin,
            "Access-Control-Request-Private-Network": "true",
        }
        handler.send_response = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        captured = {}
        handler.send_header = lambda name, value: captured.__setitem__(name, value)

        handler._send_json(200, {"ok": True})

        self.assertEqual(captured["Access-Control-Allow-Origin"], origin)
        self.assertEqual(captured["Access-Control-Allow-Methods"], "GET, POST, OPTIONS")
        self.assertEqual(captured["Access-Control-Allow-Headers"], "Content-Type")
        self.assertEqual(captured["Access-Control-Allow-Private-Network"], "true")
        self.assertEqual(captured["Vary"], "Origin")

    def test_send_json_omits_cors_headers_for_unapproved_origin(self):
        handler = object.__new__(server.Handler)
        handler.headers = {"Origin": "https://example.org"}
        handler.send_response = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        captured = {}
        handler.send_header = lambda name, value: captured.__setitem__(name, value)

        handler._send_json(200, {"ok": True})

        self.assertNotIn("Access-Control-Allow-Origin", captured)

    def test_register_inventory_project_persists_new_identity_without_guessing_repository(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inventory_path = root / "project_inventory.json"
            inventory_path.write_text(json.dumps({"schema_version": 1, "projects": []}), encoding="utf-8")
            with patch.object(server, "__file__", str(root / "server.py")), patch.object(server, "record_event") as event:
                result = server.register_inventory_project({
                    "name": "Future Project Alpha",
                    "category": "AI Platform",
                    "description": "A future independent system",
                })
            saved = json.loads(inventory_path.read_text(encoding="utf-8"))
            self.assertEqual(result["project"]["id"], "future-project-alpha")
            self.assertEqual(saved["projects"][0]["status"], "repository_match_required")
            self.assertEqual(saved["projects"][0]["candidate_repositories"], [])
            self.assertEqual(saved["projects"][0]["origin"], "syscentre_intake")
            event.assert_called_once()

    def test_register_inventory_project_validates_github_url_and_rejects_duplicate(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inventory_path = root / "project_inventory.json"
            inventory_path.write_text(json.dumps({"schema_version": 1, "projects": []}), encoding="utf-8")
            with patch.object(server, "__file__", str(root / "server.py")), patch.object(server, "record_event"):
                result = server.register_inventory_project({
                    "name": "Project With Repo",
                    "category": "Developer Tools",
                    "repository_url": "https://github.com/example/project",
                })
                self.assertEqual(result["project"]["candidate_repositories"], ["project"])
                with self.assertRaisesRegex(ValueError, "already"):
                    server.register_inventory_project({"name": "Project With Repo"})
                with self.assertRaisesRegex(ValueError, "exact https"):
                    server.register_inventory_project({"name": "Bad URL", "repository_url": "https://example.org/project"})

    def test_allowlisted_command_runs(self):
        result = server.execute_command("help")
        self.assertTrue(result["ok"])
        self.assertIn("diagnostics", result["result"]["available_commands"])

    def test_command_is_normalized(self):
        result = server.execute_command(" STATUS ")
        self.assertEqual(result["command"], "status")

    def test_arbitrary_shell_command_is_rejected(self):
        decision = evaluate_command("powershell Remove-Item important.txt")
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.risk, "blocked")
        with self.assertRaises(ValueError):
            server.execute_command("powershell Remove-Item important.txt")

    def test_unknown_command_is_rejected(self):
        with self.assertRaises(ValueError):
            server.execute_command("deploy-everything")

    def test_empty_command_is_rejected(self):
        self.assertFalse(evaluate_command("  ").allowed)

    def test_policy_catalog_only_exposes_known_commands(self):
        names = {item["command"] for item in policy_catalog()}
        self.assertEqual(names, {"status", "help", "diagnostics"})

    def test_events_are_persisted_and_returned_newest_first(self):
        event = server.record_event("test.persist", "Persistence test event", {"test": True})
        events = server.recent_events(10)
        self.assertTrue(any(item["id"] == event["id"] for item in events))
        stored = next(item for item in events if item["id"] == event["id"])
        self.assertEqual(stored["details"]["test"], True)


if __name__ == "__main__":
    unittest.main()
