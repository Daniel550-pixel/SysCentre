# SysCentre Project Lifecycle API

This API provides a controlled process lifecycle for projects whose launch commands have been explicitly reviewed. It does **not** clone repositories, install dependencies, infer entrypoints, or run any of the 28 catalogued projects automatically.

## Routes

- `GET /api/runtime-projects` — catalogued runtime adapter metadata.
- `GET /api/runtime-sessions` — in-memory process state and log paths.
- `POST /api/runtime-projects/{project_id}/start` — start an enabled profile.
- `POST /api/runtime-projects/{project_id}/stop` — stop a process started by this runtime.
- `POST /api/runtime-projects/{project_id}/restart` — stop then start an enabled profile.

Lifecycle POST requests require a JSON object body (use `{}` when no fields are needed). A blocked or unconfigured action returns HTTP 409 with a reason. Unknown route IDs are not interpreted as commands.

## Enabling a project

1. Review the repository and identify the real entrypoint and dependency instructions.
2. Prepare an isolated working copy at `~/.syscentre/workspaces/{project_id}` (or under the path configured by `SYSCENTRE_WORKSPACES`).
3. Install dependencies manually and review required configuration. Never commit secrets.
4. Add a profile to `runtime/launch_profiles.json` only after the above checks. Example structure:

```json
{
  "schema_version": 1,
  "profiles": {
    "example-project": {
      "enabled": true,
      "adapter_type": "local_process",
      "argv": ["npm", "run", "dev", "--", "--host", "127.0.0.1"],
      "cwd": ".",
      "healthcheck_url": "http://127.0.0.1:3000/health"
    }
  }
}
```

The example is illustrative, not a verified command for any existing repository. Use an actual command only after confirming its manifest and entrypoint. The process manager uses argument arrays with `shell=False`, restricts executable names to an allowlist, constrains the working directory to the project's workspace, and writes stdout/stderr to `~/.syscentre/logs/{project_id}.log`.

## Current limitations

- `launch_profiles.json` intentionally contains no enabled profiles yet.
- Supported lifecycle adapter: `local_process` only.
- Process state is in memory and is lost when SysCentre restarts; child processes are not automatically adopted after restart.
- The `healthcheck_url` field is reserved for the next health-check implementation; a started process is not automatically considered healthy.
- Stop controls only manage processes started by this runtime. It does not terminate arbitrary processes by PID.
- This API is local-first and is not an authentication boundary for exposing SysCentre to untrusted networks.

Do not enable finance, trading, infrastructure, security, or destructive automation projects until their credentials, external side effects, approval gates, and recovery behavior have been reviewed.
