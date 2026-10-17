"""Explicit, isolated project process lifecycle for SysCentre.

Projects are never launched from repository metadata. Only reviewed profiles in
launch_profiles.json may start a process; commands are argument arrays and shell
execution is disabled. Workspaces live below SYSCENTRE_WORKSPACES.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import threading
import time
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import urlopen
from pathlib import Path
from typing import Any

RUNTIME_DIR = Path(__file__).resolve().parent
REGISTRY_PATH = RUNTIME_DIR / "project_runtime_registry.json"
PROFILES_PATH = RUNTIME_DIR / "launch_profiles.json"
WORKSPACES_ROOT = Path(os.environ.get(
    "SYSCENTRE_WORKSPACES", str(Path.home() / ".syscentre" / "workspaces")
)).expanduser().resolve()
ALLOWED_EXECUTABLES = {"python", "python3", "node", "npm", "npx", "powershell", "pwsh", "dotnet"}
_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")
_LOCK = threading.RLock()
_PROCESSES: dict[str, dict[str, Any]] = {}


class LifecycleError(ValueError):
    """A lifecycle request is invalid or blocked by policy."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Runtime configuration unavailable: {path.name}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"Runtime configuration must be an object: {path.name}")
    return payload


def _project(project_id: str) -> dict[str, Any]:
    if not isinstance(project_id, str) or not _ID_RE.fullmatch(project_id):
        raise LifecycleError("Invalid project ID.")
    projects = _load_json(REGISTRY_PATH).get("projects", [])
    match = next((item for item in projects if item.get("project_id") == project_id), None)
    if match is None:
        raise LifecycleError("Unknown project ID.")
    return match


def _profile(project_id: str) -> dict[str, Any]:
    profiles = _load_json(PROFILES_PATH).get("profiles", {})
    profile = profiles.get(project_id) if isinstance(profiles, dict) else None
    if not isinstance(profile, dict) or profile.get("enabled") is not True:
        raise LifecycleError("Project is not launch-configured. Review its entrypoint, dependencies, and isolation before enabling it.")
    if profile.get("adapter_type") != "local_process":
        raise LifecycleError("Only reviewed local_process profiles are supported by this lifecycle API.")
    argv = profile.get("argv")
    if not isinstance(argv, list) or not argv or not all(isinstance(arg, str) and arg and "\x00" not in arg for arg in argv):
        raise LifecycleError("Launch profile argv must be a non-empty array of non-empty strings.")
    # Do not accept paths to arbitrary executables, even if the basename is allowlisted.
    executable = argv[0].lower()
    if executable.endswith(".exe"):
        executable = executable[:-4]
    if executable not in ALLOWED_EXECUTABLES:
        raise LifecycleError("Executable must be an allowlisted command name, not an arbitrary path.")
    # Normalize the configured root as well as the child. On Windows, tempfile
    # and user paths can use different 8.3/long-path spellings; comparing a
    # resolved child against an unresolved root incorrectly marks valid workspaces
    # as missing or outside the workspace root.
    workspace_root = WORKSPACES_ROOT.resolve()
    workspace = (workspace_root / project_id).resolve()
    if workspace.parent != workspace_root or not workspace.is_dir():
        raise LifecycleError("Project workspace is missing. Place reviewed source in its isolated workspace first.")
    cwd_value = profile.get("cwd", ".")
    if not isinstance(cwd_value, str) or Path(cwd_value).is_absolute():
        raise LifecycleError("Launch profile cwd must be a relative path inside the project workspace.")
    cwd = (workspace / cwd_value).resolve()
    if cwd != workspace and workspace not in cwd.parents:
        raise LifecycleError("Launch profile cwd escapes the project workspace.")
    if not cwd.is_dir():
        raise LifecycleError("Launch profile working directory does not exist.")
    required_paths = profile.get("required_paths", [])
    if not isinstance(required_paths, list) or not all(isinstance(item, str) and item for item in required_paths):
        raise LifecycleError("Launch profile required_paths must be an array of relative paths.")
    missing_paths = []
    for item in required_paths:
        relative = Path(item)
        if relative.is_absolute():
            raise LifecycleError("Required paths must remain inside the project workspace.")
        required_path = (workspace / relative).resolve()
        if required_path != workspace and workspace not in required_path.parents:
            raise LifecycleError("Required path escapes the project workspace.")
        if not required_path.exists():
            missing_paths.append(item)
    if missing_paths:
        raise LifecycleError("Project workspace is missing required files or dependencies: " + ", ".join(missing_paths))
    healthcheck_url = profile.get("healthcheck_url", "")
    display_url = profile.get("display_url", healthcheck_url)
    for field_name, candidate in (("healthcheck_url", healthcheck_url), ("display_url", display_url)):
        if candidate:
            parsed = urlsplit(candidate)
            if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"} or not parsed.port:
                raise LifecycleError(f"{field_name} must use an explicit HTTP loopback URL and port.")
    return {"argv": argv, "cwd": cwd, "healthcheck_url": healthcheck_url, "display_url": display_url}


def _probe_health(url: str) -> str:
    if not url:
        return "not_configured"
    try:
        with urlopen(url, timeout=0.5) as response:
            return "healthy" if 200 <= response.status < 400 else "unhealthy"
    except (OSError, URLError, ValueError):
        return "unhealthy"


def list_sessions() -> dict[str, Any]:
    with _LOCK:
        sessions = []
        profiles = _load_json(PROFILES_PATH).get("profiles", {})
        if not isinstance(profiles, dict):
            profiles = {}
        for project in _load_json(REGISTRY_PATH).get("projects", []):
            project_id = project.get("project_id")
            proc_info = _PROCESSES.get(project_id)
            proc = proc_info.get("process") if proc_info else None
            running = bool(proc and proc.poll() is None)
            profile = profiles.get(project_id)
            configured = isinstance(profile, dict) and profile.get("enabled") is True
            ready = False
            readiness_reason = "Project is not launch-configured."
            if configured:
                try:
                    _profile(project_id)
                    ready = True
                    readiness_reason = ""
                except LifecycleError as exc:
                    readiness_reason = str(exc)
            state = "running" if running else ("stopped" if ready else ("setup_required" if configured else "not_configured"))
            health = _probe_health(profile.get("healthcheck_url", "")) if running and isinstance(profile, dict) else ("stopped" if ready else ("setup_required" if configured else "not_configured"))
            sessions.append({
                "project_id": project_id,
                "name": project.get("name", project_id),
                "configured": configured,
                "ready": ready,
                "readiness_reason": readiness_reason,
                "state": state,
                "health": health,
                "pid": proc.pid if running else None,
                "started_at": proc_info.get("started_at") if running and proc_info else None,
                "log_path": proc_info.get("log_path") if proc_info else None,
                "url": profile.get("display_url") if running and isinstance(profile, dict) else None,
            })
        return {"sessions": sessions, "count": len(sessions), "workspace_root": str(WORKSPACES_ROOT)}


def start_project(project_id: str) -> dict[str, Any]:
    project = _project(project_id)
    profile = _profile(project_id)
    with _LOCK:
        current = _PROCESSES.get(project_id)
        if current and current["process"].poll() is None:
            return {"ok": True, "project_id": project_id, "state": "running", "health": "pending", "url": profile["display_url"], "pid": current["process"].pid, "already_running": True}
        log_dir = Path.home() / ".syscentre" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / f"{project_id}.log"
        try:
            log_handle = log_path.open("ab")
            process = subprocess.Popen(
                profile["argv"],
                cwd=str(profile["cwd"]),
                stdin=subprocess.DEVNULL,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                shell=False,
                close_fds=True,
                creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
            )
        except OSError as exc:
            raise LifecycleError(f"Process could not start: {exc.__class__.__name__}. Check the workspace dependencies and executable.") from exc
        finally:
            if "log_handle" in locals():
                log_handle.close()
        _PROCESSES[project_id] = {
            "process": process, "configured": True, "started_at": time.time(),
            "log_path": str(log_path), "project_name": project.get("name", project_id),
        }
        return {"ok": True, "project_id": project_id, "state": "starting", "health": "pending", "url": profile["display_url"], "pid": process.pid, "log_path": str(log_path)}


def stop_project(project_id: str) -> dict[str, Any]:
    _project(project_id)
    with _LOCK:
        current = _PROCESSES.get(project_id)
        if not current or current["process"].poll() is not None:
            return {"ok": True, "project_id": project_id, "state": "stopped", "already_stopped": True}
        process = current["process"]
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        return {"ok": True, "project_id": project_id, "state": "stopped", "pid": process.pid}


def restart_project(project_id: str) -> dict[str, Any]:
    stop_project(project_id)
    return start_project(project_id)
