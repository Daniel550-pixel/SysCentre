"""SysCentre project-hosting subsystem.

This module is the stable hosting facade over reviewed launch profiles and the
isolated local-process lifecycle manager. It never infers commands from repository
metadata and never edits launch profiles at runtime.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from project_lifecycle import (
    LifecycleError,
    PROFILES_PATH,
    REGISTRY_PATH,
    WORKSPACES_ROOT,
    list_sessions,
    restart_project,
    start_project,
    stop_project,
)

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")
_ACTIONS = {
    "start": start_project,
    "stop": stop_project,
    "restart": restart_project,
}


def _read_object(path: Path, label: str) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Project hosting configuration is unavailable: {label}.") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"Project hosting configuration must be an object: {label}.")
    return value


def hosting_overview() -> dict[str, Any]:
    """Return a read-only, consolidated view of projects and host readiness."""
    registry = _read_object(REGISTRY_PATH, "project runtime registry")
    profile_document = _read_object(PROFILES_PATH, "launch profiles")
    profiles = profile_document.get("profiles", {})
    if not isinstance(profiles, dict):
        raise RuntimeError("Launch profiles must contain a profiles object.")

    sessions_response = list_sessions()
    sessions = {
        item.get("project_id"): item
        for item in sessions_response.get("sessions", [])
        if isinstance(item, dict) and isinstance(item.get("project_id"), str)
    }

    projects: list[dict[str, Any]] = []
    for record in registry.get("projects", []):
        if not isinstance(record, dict):
            continue
        project_id = record.get("project_id")
        if not isinstance(project_id, str) or not _ID_RE.fullmatch(project_id):
            continue
        session = sessions.get(project_id, {})
        profile = profiles.get(project_id, {})
        if not isinstance(profile, dict):
            profile = {}
        configured = session.get("configured") is True
        state = session.get("state", "not_configured")
        projects.append({
            "project_id": project_id,
            "name": record.get("name", project_id),
            "repository_url": record.get("repository_url", ""),
            "category": record.get("category", ""),
            "hosting": {
                "adapter_type": profile.get("adapter_type", "unconfigured"),
                "configured": configured,
                "ready": session.get("ready") is True,
                "state": state,
                "health": session.get("health", "not_configured"),
                "readiness_reason": session.get("readiness_reason", ""),
                "url": session.get("url"),
                "healthcheck_url": profile.get("healthcheck_url", ""),
                "required_paths": profile.get("required_paths", []),
                "workspace": str(WORKSPACES_ROOT / project_id) if configured else None,
                "pid": session.get("pid"),
                "started_at": session.get("started_at"),
                "log_path": session.get("log_path"),
                "available_actions": (
                    ["start", "stop", "restart"] if configured and session.get("ready") is True
                    else ["provision", "review_profile"] if configured
                    else ["review_profile"]
                ),
            },
        })

    counts = {
        "total": len(projects),
        "configured": sum(1 for item in projects if item["hosting"]["configured"]),
        "ready": sum(1 for item in projects if item["hosting"]["ready"]),
        "running": sum(1 for item in projects if item["hosting"]["state"] == "running"),
        "setup_required": sum(1 for item in projects if item["hosting"]["state"] == "setup_required"),
        "not_configured": sum(1 for item in projects if item["hosting"]["state"] == "not_configured"),
        "unhealthy": sum(1 for item in projects if item["hosting"]["health"] == "unhealthy"),
    }
    return {
        "ok": True,
        "subsystem": "syscentre-project-hosting",
        "schema_version": 1,
        "workspace_root": str(WORKSPACES_ROOT),
        "counts": counts,
        "projects": projects,
    }


def perform_hosting_action(project_id: str, action: str) -> dict[str, Any]:
    """Run a supported lifecycle action through the existing policy-checked manager."""
    if not isinstance(project_id, str) or not _ID_RE.fullmatch(project_id):
        raise LifecycleError("Invalid project ID.")
    if action not in _ACTIONS:
        raise LifecycleError("Unsupported hosting action.")
    result = _ACTIONS[action](project_id)
    return {
        **result,
        "subsystem": "syscentre-project-hosting",
        "action": action,
    }
