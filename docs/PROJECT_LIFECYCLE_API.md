# SysCentre Project Lifecycle API

This API provides a controlled process lifecycle for projects whose launch commands have been explicitly reviewed. It does **not** clone repositories, install dependencies, infer entrypoints, or run any of the 28 catalogued projects automatically.

## Routes

- `GET /api/runtime-projects` — catalogued runtime adapter metadata.
- `GET /api/runtime-sessions` — in-memory process state and log paths.
- `POST /api/runtime-projects/{project_id}/start` — start an enabled profile.
- `POST /api/runtime-projects/{project_id}/stop` — stop a process started by this runtime.
- `POST /api/runtime-projects/{project_id}/restart` — stop then start an enabled profile.

Lifecycle POST requests require a JSON object body (use `{}` when no fields are needed). A blocked or unconfigured action returns HTTP 409 with a reason. Unknown route IDs are not interpreted as commands.

## First integration: Localhost-webapp

The first enabled profile is **Localhost-webapp**, a Next.js starter with a checked-in `package-lock.json`. It runs locally on `127.0.0.1:4180`, with no external API keys or external service actions configured. This is a runtime integration test, not a claim that the starter is a finished product.

From the SysCentre repository root in PowerShell:

```powershell
.\scripts\Install-SysCentreProject.ps1 -ProjectId localhost-webapp
.\scripts\Install-SysCentreProject.ps1 -ProjectId localhost-webapp -InstallDependencies
```

The first command verifies/clones the repository into `~/.syscentre/workspaces/localhost-webapp`. The second installs locked dependencies; npm package lifecycle scripts may execute, so run it only after reviewing the repository. It does not overwrite or reset an existing checkout. Once dependencies are installed, use **Start** for Localhost-webapp in the SysCentre hub. The dashboard reports process state and HTTP health, and exposes **Open app** when the process is running. Logs are written to `~/.syscentre/logs/localhost-webapp.log`.

If `SYSCENTRE_WORKSPACES` is set, the provisioning script and runtime use that workspace root.

## Enabling additional projects

1. Review the repository and identify the real entrypoint and dependency instructions.
2. Prepare an isolated working copy at `~/.syscentre/workspaces/{project_id}` (or under the path configured by `SYSCENTRE_WORKSPACES`).
3. Install dependencies only after reviewing the project's source and dependency lifecycle scripts. Never commit secrets.
4. Add a profile to `runtime/launch_profiles.json` only after those checks. Example structure:

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

The example is illustrative. Use an actual command only after confirming its manifest and entrypoint. The process manager uses argument arrays with `shell=False`, restricts executable names to an allowlist, constrains the working directory to the project's workspace, restricts health probes to explicit loopback URLs, and writes stdout/stderr to `~/.syscentre/logs/{project_id}.log`.

## Current limitations

- Only Localhost-webapp has an enabled launch profile; the other catalogued projects remain disabled.
- Supported lifecycle adapter: `local_process` only.
- Process state is in memory and is lost when SysCentre restarts; child processes are not automatically adopted after restart.
- Health is checked with a short HTTP request to the configured loopback URL. A process may need a few seconds after start before the health check passes.
- Stop controls only manage processes started by this runtime. It does not terminate arbitrary processes by PID.
- This API is local-first and is not an authentication boundary for exposing SysCentre to untrusted networks.

Do not enable finance, trading, infrastructure, security, or destructive automation projects until their credentials, external side effects, approval gates, and recovery behavior have been reviewed.
