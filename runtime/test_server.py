import unittest

import server


class RuntimeTests(unittest.TestCase):
    def test_status_contains_policy_and_ledger_state(self):
        status = server.runtime_status()
        self.assertEqual(status["state"], "online")
        self.assertEqual(status["policy_gate"], "enabled")
        self.assertEqual(status["event_ledger"], "in-memory")

    def test_allowlisted_command_runs(self):
        result = server.execute_command("help")
        self.assertTrue(result["ok"])
        self.assertIn("diagnostics", result["result"]["available_commands"])

    def test_command_is_normalized(self):
        result = server.execute_command(" STATUS ")
        self.assertEqual(result["command"], "status")

    def test_arbitrary_shell_command_is_rejected(self):
        with self.assertRaises(ValueError):
            server.execute_command("powershell Remove-Item important.txt")

    def test_unknown_command_is_rejected(self):
        with self.assertRaises(ValueError):
            server.execute_command("deploy-everything")


if __name__ == "__main__":
    unittest.main()
