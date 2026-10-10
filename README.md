# SysCentre

SysCentre is a standalone local-first systems platform. It starts with a controlled Python runtime, a browser dashboard, and a PowerShell developer workflow.

## Architecture

- **WebApp:** React + TypeScript + Vite dashboard.
- **Runtime:** Python standard-library HTTP API on `127.0.0.1:8765`.
- **Terminal:** PowerShell launcher and a small allowlisted runtime command interface.
- **Safety model:** AI decision-making is kept separate from execution. Runtime actions must be explicitly allowlisted; arbitrary shell execution is not exposed by the API.

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

The launcher starts the runtime and Vite development server. Open **http://127.0.0.1:5173**. The runtime API is **http://127.0.0.1:8765**.

To start components separately:

```powershell
python .\runtime\server.py
npm --prefix .\webapp install
npm --prefix .\webapp run dev
```

## Runtime API

- `GET /api/health` — liveness check
- `GET /api/status` — runtime status
- `GET /api/events` — recent in-memory event ledger
- `POST /api/command` — allowlisted commands: `status`, `help`, `diagnostics`

Example:

```powershell
Invoke-RestMethod http://127.0.0.1:8765/api/status
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8765/api/command -ContentType 'application/json' -Body '{"command":"diagnostics"}'
```

## Development checks

```powershell
python -m unittest discover -s runtime -p "test_*.py" -v
npm --prefix .\webapp install
npm --prefix .\webapp run build
```

## Current scope

This is the initial working foundation, not a claim that an AI agent or persistent memory system is already implemented. The event ledger is currently in-memory; persistent storage, model providers, authentication, and advanced policy configuration are future phases. Keep secrets in local environment files and never commit credentials.
