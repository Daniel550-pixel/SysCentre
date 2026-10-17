import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import project_lifecycle as lifecycle


class ProjectLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.registry = self.root / "registry.json"
        self.profiles = self.root / "profiles.json"
        self.workspaces = self.root / "workspaces"
        self.workspaces.mkdir()
        self.workspace = self.workspaces / "demo-project"
        self.workspace.mkdir()
        self.registry.write_text(json.dumps({"projects": [
            {"project_id": "demo-project", "name": "Demo Project"}
        ]}), encoding="utf-8")
        self.profiles.write_text(json.dumps({"profiles": {}}), encoding="utf-8")
        self.patches = [
            patch.object(lifecycle, "REGISTRY_PATH", self.registry),
            patch.object(lifecycle, "PROFILES_PATH", self.profiles),
            patch.object(lifecycle, "WORKSPACES_ROOT", self.workspaces),
            patch.dict(lifecycle._PROCESSES, {}, clear=True),
        ]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)

    def write_profile(self, profile):
        self.profiles.write_text(json.dumps({"profiles": {"demo-project": profile}}), encoding="utf-8")

    def test_unconfigured_project_is_not_launchable(self):
        with self.assertRaisesRegex(lifecycle.LifecycleError, "not launch-configured"):
            lifecycle.start_project("demo-project")

    def test_unknown_and_traversal_project_ids_are_rejected(self):
        for project_id in ("../demo-project", "unknown"):
            with self.subTest(project_id=project_id):
                with self.assertRaises(lifecycle.LifecycleError):
                    lifecycle.start_project(project_id)

    def test_shell_and_unapproved_executables_are_rejected(self):
        self.write_profile({"enabled": True, "adapter_type": "local_process",
                            "argv": ["bash", "-c", "echo unsafe"], "cwd": "."})
        with self.assertRaisesRegex(lifecycle.LifecycleError, "allowlist"):
            lifecycle.start_project("demo-project")
        self.write_profile({"enabled": True, "adapter_type": "local_process",
                            "argv": ["python", "-c", "print('x')"], "cwd": ".", "shell": True})
        # The process manager never enables shell, regardless of profile data.
        with patch.object(lifecycle.subprocess, "Popen") as popen:
            popen.return_value.poll.return_value = None
            popen.return_value.pid = 1234
            result = lifecycle.start_project("demo-project")
            self.assertEqual(result["state"], "starting")
            self.assertIs(popen.call_args.kwargs["shell"], False)

    def test_absolute_or_escaping_working_directory_is_rejected(self):
        self.write_profile({"enabled": True, "adapter_type": "local_process",
                            "argv": ["python", "-V"], "cwd": "../"})
        with self.assertRaisesRegex(lifecycle.LifecycleError, "escapes"):
            lifecycle.start_project("demo-project")

    def test_list_sessions_includes_registry_projects_without_launching_them(self):
        result = lifecycle.list_sessions()
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["sessions"][0]["state"], "not_configured")
        self.assertEqual(result["sessions"][0]["pid"], None)


if __name__ == "__main__":
    unittest.main()
