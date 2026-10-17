# SysCentre Project Hosting Subsystem

The Project Hosting subsystem is the single API facade for viewing and operating reviewed project runtimes. It sits above the project registry, explicit launch profiles, isolated workspaces, and the process lifecycle manager. It does not replace project repositories or infer commands from source metadata.

## Responsibilities

- Consolidate project identity, launch-profile configuration, workspace readiness, runtime state, HTTP health, URLs, PIDs, and log locations into one host view.
- Expose consistent start, stop, and restart operations.
- Keep projects isolated at `~/.syscentre/workspaces/{project_id}` (or the root set by `SYSCENTRE_WORKSPACES`).
- Report unconfigured projects honestly; registration or indexing never makes a project executable.
- Keep launch profiles as reviewed, version-controlled configuration. The API cannot create or modify executable profiles.
- Reuse `project_lifecycle.py` for path checks, executable allowlisting, `shell=False`, loopback health checks, and process lifecycle behavior.

## API

- `GET /api/hosting` — hosting overview, counts, workspace root, and all registered runtime projects.
- `GET /api/hosting/projects` — alias for the hosting overview.
- `POST /api/hosting/projects/{project_id}/start` — start a configured and ready project.
- `POST /api/hosting/projects/{project_id}/stop` — stop a process managed by SysCentre.
- `POST /api/hosting/projects/{project_id}/restart` — restart a configured and ready project.

POST actions require a JSON object body such as `{}`. A blocked action returns HTTP 409 with a reason. The existing `/api/runtime-projects` and `/api/runtime-sessions` endpoints remain available for backward compatibility.

Example PowerShell calls:

```powershell
$HostApi = "http://127.0.0.1:8765/api/hosting"
Invoke-RestMethod $HostApi
Invoke-RestMethod -Method Post -Uri "$HostApi/projects/networklab/start" -ContentType "application/json" -Body "{}"
Invoke-RestMethod -Method Post -Uri "$HostApi/projects/networklab/stop" -ContentType "application/json" -Body "{}"
```

## Response model

Each project includes identity metadata and a `hosting` object with:

- `configured`, `ready`, `state`, and `readiness_reason`
- `adapter_type`, `health`, `url`, and `healthcheck_url`
- `workspace`, `required_paths`, `pid`, `started_at`, and `log_path`
- `available_actions`, derived from actual readiness rather than assumed capability

The overview includes counts for total, configured, ready, running, setup-required, not-configured, and unhealthy projects.

## Security and operating boundaries

Launch profiles are still explicit, reviewed records in `runtime/launch_profiles.json`. They are not generated from repository manifests. The hosting facade only offers lifecycle actions; it does not clone repositories, install dependencies, modify launch profiles, provision infrastructure, or execute arbitrary shell commands. Provisioning and dependency installation remain explicit operator actions.

A running local HTTP endpoint proves only that its configured health check responds. It does not establish production readiness or validate external integrations. Process state remains in memory and is not automatically adopted after the runtime restarts. Keep the runtime bound to loopback unless an authenticated access layer is added.

## Adding a project

1. Confirm the exact repository identity and inspect its source.
2. Provision a separate workspace and install dependencies only after reviewing setup scripts.
3. Verify the real entrypoint, required files, local port, and health check.
4. Add an explicit profile with an allowlisted executable and argument array.
5. Test readiness and start/health/restart/stop before describing the project as hosted.
6. Add regression tests and update the runtime registry metadata.

Finance, trading, security, infrastructure, and destructive automation projects require a separate side-effect and approval review before being enabled.
