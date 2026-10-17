# SysCentre lifecycle smoke test

Use this after provisioning one of the reviewed local projects. The script exercises the lifecycle API from the machine running SysCentre; it does not install dependencies, provision a workspace, or change project source.

## Prerequisites

- SysCentre runtime is running at `http://127.0.0.1:8765`.
- The selected project has been provisioned in its isolated workspace.
- For `localhost-webapp`, locked dependencies have been installed after reviewing the repository.
- The project's configured port is available.
- The selected project is not already running. The script refuses to disturb an existing session.

## Run

From the SysCentre repository root in PowerShell:

```powershell
.\scripts\Test-SysCentreProjectLifecycle.ps1 -ProjectId networklab
```

For Localhost-webapp:

```powershell
.\scripts\Test-SysCentreProjectLifecycle.ps1 -ProjectId localhost-webapp
```

Optional parameters:

- `-RuntimeBaseUrl http://127.0.0.1:8765` changes the runtime API base URL.
- `-StartupTimeoutSeconds 30` allows a slower project up to 30 seconds to respond.

The smoke test checks runtime reachability, starts the selected project, waits for its HTTP health endpoint, calls restart, verifies health again, and stops the process. A successful run prints a final `PASS` line. If an operation fails after the test starts a process, the script attempts cleanup by requesting stop. Inspect `~/.syscentre/logs/{project_id}.log` if startup or health verification fails.

## What this does not prove

- NetworkLab's `/healthz` response verifies the HTTP server only; it does not verify VirtualBox, VM state, DHCP, or end-to-end lab connectivity.
- Localhost-webapp responding over HTTP proves its local web process is serving a response, not that every product feature works.
- This is a manual local smoke test, not a CI test. It has not been run against the user's local Windows machine by the repository change itself.
