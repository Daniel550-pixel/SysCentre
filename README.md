# SysCentre

SysCentre is a standalone local-first systems platform with a browser dashboard, a controlled Python runtime, a deterministic policy engine, and a persistent SQLite audit ledger.

## Architecture

- **WebApp:** React + TypeScript + Vite dashboard.
- **Runtime:** Python standard-library HTTP API on `127.0.0.1:8765`.
- **Policy engine:** deterministic explicit allowlist; unknown commands are denied and recorded.
- **Event ledger:** SQLite database stored by default at `~/.syscentre/syscentre.db` (on Windows, inside your user profile). Keeps up to 5,000 recent events across runtime restarts.
- **Terminal:** PowerShell launcher and a constrained command interface.
- **Safety model:** AI decision-making is separate from execution. User input is never forwarded to a shell.

## Requirements

- Python 3.11 or newer
- Node.js 20 or newer (npm included)
- Windows PowerShell 5.1 or PowerShell 7

## Start on Windows

From the repository root:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\Start-SysCentre.ps1
```

Open **http://127.0.0.1:5173**. The runtime API is **http://127.0.0.1:8765**.

To start components separately:

```powershell
python .\runtime\server.py
npm --prefix .\webapp install
npm --prefix .\webapp run dev
```

## Runtime API

- `GET /api/health` — liveness check
- `GET /api/status` — runtime state, versions, and ledger path
- `GET /api/events` — most recent persisted events
- `GET /api/policy` — current allowlisted command catalog
- `POST /api/command` — executes only `status`, `help`, or `diagnostics`

Example:

```powershell
Invoke-RestMethod http://127.0.0.1:8765/api/status
Invoke-RestMethod http://127.0.0.1:8765/api/policy
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8765/api/command -ContentType 'application/json' -Body '{"command":"diagnostics"}'
```

## Development checks

```powershell
python -m unittest discover -s runtime -p "test_*.py" -v
npm --prefix .\webapp install
npm --prefix .\webapp run build
```

## Current scope

This phase adds persistent audit history and a separate deterministic policy module. The commands remain read-only. AI providers, agent orchestration, approval workflows, authentication, and OS-level sandboxing are not implemented yet. Do not treat the allowlist as a complete security sandbox. Keep secrets in local environment files and never commit credentials.
