# SysCentre

SysCentre is a standalone local-first systems control plane. It catalogs existing projects, indexes repository metadata and readable source files into a local SQLite database, and preserves each project's independent repository and runtime boundary.

## Core architecture

- **WebApp:** React + TypeScript + Vite dashboard with a project registry and indexing controls.
- **Runtime:** Python standard-library HTTP API on `127.0.0.1:8765`.
- **Policy engine:** deterministic explicit allowlist; unknown commands are denied and recorded.
- **Event ledger:** SQLite database at `~/.syscentre/syscentre.db`, with up to 5,000 recent audit events.
- **Project registry:** `runtime/repository_catalog.json` records the projects known to SysCentre.
- **Repository indexer:** `runtime/repository_ingest.py` imports repository metadata, commit/tree identity, file paths, blob hashes, file sizes, and readable UTF-8 source/documentation content.
- **Project isolation:** indexed source is data, not executable instructions. Repositories are not merged and indexing does not run their code.

## Repository ingestion

The dashboard Project Registry lists repositories registered in the catalog. Select **Index repo** to index one project from its configured GitHub URL. GitHub API rate limits apply; set `GITHUB_TOKEN` or `GH_TOKEN` in the runtime environment for authenticated API access.

The indexer deliberately excludes sensitive-looking paths (for example, `.env`, private keys, and credential files), generated/dependency directories, binary files, and individual files larger than 1.5 MB from the text content index. Their paths and exclusion reasons are retained as metadata. A truncated GitHub tree or failed file fetch aborts the run rather than falsely reporting a complete index. The source repository is never modified.

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

## Runtime API

- `GET /api/health` — liveness check
- `GET /api/status` — runtime state and environment
- `GET /api/events` — persisted audit events
- `GET /api/policy` — current allowlisted command catalog
- `GET /api/repositories` — catalog plus indexing status
- `GET /api/repositories/{project_id}/files?path=term&limit=100` — indexed file records and source text (maximum 200 per response)
- `POST /api/repositories/ingest` with `{"project_id":"networklab"}` — index one catalogued repository
- `POST /api/command` — accepts only `status`, `help`, or `diagnostics`

Example PowerShell calls:

```powershell
Invoke-RestMethod http://127.0.0.1:8765/api/repositories
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8765/api/repositories/ingest -ContentType 'application/json' -Body '{"project_id":"networklab"}'
Invoke-RestMethod 'http://127.0.0.1:8765/api/repositories/networklab/files?limit=10'
```

## Development checks

```powershell
python -m unittest discover -s runtime -p "test_*.py" -v
npm --prefix .\webapp install
npm --prefix .\webapp run build
```

## Current boundaries

The project registry and source index are the foundation for cross-project discovery. Automated dependency mapping, project-level semantic search, agent orchestration, approval workflows, and execution adapters are subsequent capabilities. Keep credentials out of the repository and do not treat policy allowlisting as a complete OS sandbox.
