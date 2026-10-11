import unittest
from unittest.mock import Mock

import server
from policy import evaluate_command, policy_catalog


class RuntimeTests(unittest.TestCase):
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
