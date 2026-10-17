"""Tests for the SysCentre project-hosting facade."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import project_hosting


class ProjectHostingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.registry = self.root / "registry.json"
        self.profiles = self.root / "profiles.json"
        self.registry.write_text(json.dumps({"projects": [
            {"project_id": "demo-app", "name": "Demo App", "repository_url": "https://github.com/example/demo-app"},
            {"project_id": "docs-only", "name": "Docs Only"},
        ]}), encoding="utf-8")
        self.profiles.write_text(json.dumps({"profiles": {
            "demo-app": {
                "enabled": True,
                "adapter_type": "local_process",
                "healthcheck_url": "http://127.0.0.1:4567/health",
                "required_paths": ["app.py"],
            }
        }}), encoding="utf-8")
        self.patches = [
            patch.object(project_hosting, "REGISTRY_PATH", self.registry),
            patch.object(project_hosting, "PROFILES_PATH", self.profiles),
            patch.object(project_hosting, "WORKSPACES_ROOT", self.root / "workspaces"),
            patch.object(project_hosting, "list_sessions", return_value={
                "workspace_root": str(self.root / "workspaces"),
                "sessions": [
                    {"project_id": "demo-app", "name": "Demo App", "configured": True,
                     "ready": True, "state": "running", "health": "healthy", "pid": 123,
                     "url": "http://127.0.0.1:4567/", "readiness_reason": "",
                     "started_at": 1.0, "log_path": "demo-app.log"},
                    {"project_id": "docs-only", "name": "Docs Only", "configured": False,
                     "ready": False, "state": "not_configured", "health": "not_configured",
                     "readiness_reason": "Project is not launch-configured."},
                ],
            }),
        ]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)

    def test_overview_aggregates_project_and_hosting_state(self):
        result = project_hosting.hosting_overview()
        self.assertEqual(result["subsystem"], "syscentre-project-hosting")
        self.assertEqual(result["counts"]["total"], 2)
        self.assertEqual(result["counts"]["configured"], 1)
        self.assertEqual(result["counts"]["ready"], 1)
        self.assertEqual(result["counts"]["running"], 1)
        demo = next(item for item in result["projects"] if item["project_id"] == "demo-app")
        self.assertEqual(demo["hosting"]["state"], "running")
        self.assertEqual(demo["hosting"]["available_actions"], ["start", "stop", "restart"])
        docs = next(item for item in result["projects"] if item["project_id"] == "docs-only")
        self.assertEqual(docs["hosting"]["available_actions"], ["review_profile"])

    def test_profile_schema_is_checked(self):
        self.profiles.write_text(json.dumps({"profiles": []}), encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "profiles object"):
            project_hosting.hosting_overview()

    def test_hosting_action_delegates_to_lifecycle_manager(self):
        with patch.dict(project_hosting._ACTIONS, {"start": lambda project_id: {
            "ok": True, "project_id": project_id, "state": "starting"
        }}):
            result = project_hosting.perform_hosting_action("demo-app", "start")
        self.assertEqual(result["state"], "starting")
        self.assertEqual(result["subsystem"], "syscentre-project-hosting")
        self.assertEqual(result["action"], "start")

    def test_invalid_project_id_and_action_are_rejected(self):
        with self.assertRaises(project_hosting.LifecycleError):
            project_hosting.perform_hosting_action("../demo-app", "start")
        with self.assertRaisesRegex(project_hosting.LifecycleError, "Unsupported"):
            project_hosting.perform_hosting_action("demo-app", "configure")


if __name__ == "__main__":
    unittest.main()
