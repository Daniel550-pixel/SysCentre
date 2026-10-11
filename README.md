# SysCentre

SysCentre is a standalone local-first systems control plane. It catalogs existing projects, indexes repository metadata and readable source files into a local SQLite database, and preserves each project's independent repository and runtime boundary.

## Core architecture

- **WebApp:** React + TypeScript + Vite dashboard with a project registry and indexing controls.
- **Runtime:** Python standard-library HTTP API on `127.0.0.1:8765`.
- **Policy engine:** deterministic explicit allowlist; unknown commands are denied and recorded.
- **Event ledger:** SQLite database at `~/.syscentre/syscentre.db`, with up to 5,000 recent audit events.
- **Project registry:** `runtime/repository_catalog.json` records the 28 projects known to SysCentre, including executive portfolio metadata. `bonus-app/systems.json` mirrors this catalog for the static GitHub Pages application. `runtime/project_inventory.json` tracks historical/new project identities that still need exact repository reconciliation.
- **Executive control plane:** portfolio-wide grouping by business-model hypothesis, system type, sector, and market category, with an executive register that combines all four filters, searches target markets and portfolio roles, and surfaces market-validation, lifecycle, and monetization-evidence gaps. Each repository remains individually inspectable with source links and classification basis.
- **Repository indexer:** `runtime/repository_ingest.py` imports repository metadata, commit/tree identity, file paths, blob hashes, file sizes, and readable UTF-8 source/documentation content.
- **Runtime adapter registry:** `runtime/project_runtime_registry.json` has an explicit, initially unconfigured adapter profile for every one of the 28 repositories. The dashboard shows readiness and does not pretend unconfigured projects are runnable. `GET /api/runtime-projects` exposes this read-only registry.
- **Application architecture inventory:** `runtime/repository_architectures.json` documents the observed stack, entrypoints, layers, data/state boundaries, declared integrations, evidence paths and source-tree commit for every catalog repository. `GET /api/repository-architectures` serves it to the searchable **Application architectures** explorer. Records distinguish verified source structure from partial scaffolds, documentation-only projects and empty repositories; they do not assert deployment or runtime health.
- **Extensible project intake:** the dashboard and `POST /api/project-inventory` can register future project identities with validation, duplicate protection, persistence, and an audit event. Registration does not confirm a repository mapping or enable execution.
- **Project isolation:** indexed source is data, not executable instructions. Repositories are not merged and indexing does not run their code.

## Repository ingestion

The dashboard Project Registry lists repositories registered in the catalog. Select **Index repo** to index one project or **Index all projects** to process the catalog sequentially. Use cross-project source search to find text inside indexed source files. GitHub API rate limits apply; set `GITHUB_TOKEN` or `GH_TOKEN` in the runtime environment for authenticated API access.

Historical project identities without a confirmed exact repository mapping are tracked separately in `runtime/project_inventory.json` and shown in the dashboard under **Historical projects awaiting repository match**. Candidate names are informational only; SysCentre does not guess repository URLs or ingest a candidate under the wrong project identity. Use `GET /api/project-inventory` to retrieve this reconciliation list.

Repository ingestion checkpoints completed file records in SQLite every 50 files. If a run fails, its last successful checkpoints remain available; retrying the same repository commit reuses files whose blob hashes have not changed and fetches only missing or changed files. The dashboard exposes progress and failure details through `GET /api/ingest-status`, and a successful run atomically promotes the completed checkpoint into the searchable index. A changed upstream commit starts a fresh checkpoint set.

The indexer deliberately excludes sensitive-looking paths (for example, `.env`, private keys, and credential files), generated/dependency directories, binary files, and individual files larger than 900 KB from the text content index. Their paths and exclusion reasons are retained as metadata. A truncated GitHub tree or failed file fetch aborts the run rather than falsely reporting a complete index. The source repository is never modified.

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
- `GET /api/ingest-status?project_id=syscentre` — persisted per-project ingestion progress, including interrupted runs and checkpoint counts
- `GET /api/runtime-projects` — runtime adapter configuration/readiness for all registered repository records
- `GET /api/repository-architectures` — 28 evidence-backed architecture records with stack, entrypoints, layers, data/state, integrations, snapshot SHAs and limitations
- `GET /api/repositories/{project_id}/files?path=term&limit=100` — indexed file records and source text (maximum 200 per response)
- `GET /api/search?q=policy&limit=50` — search indexed source across projects (maximum 100 matches)
- `POST /api/repositories/ingest` with `{"project_id":"networklab"}` — index one catalogued repository
- `POST /api/command` — accepts only `status`, `help`, or `diagnostics`

### Static continuity fallback and indexed-source search

The published [SysCentre fallback](https://daniel550-pixel.github.io/SysCentre/) remains a static site and its catalog works without the local runtime. Its **Indexed source search** panel sends read-only queries to `http://127.0.0.1:8765/api/search`; it does not trigger indexing or execute repository code. For results, start the local runtime on the same computer and index at least one repository in the local dashboard. Browsers may ask permission to access localhost from the hosted page.

The runtime returns cross-origin headers only for explicit allowed origins: `https://daniel550-pixel.github.io`, `http://127.0.0.1:5173`, and `http://localhost:5173` by default. Administrators can replace that list with comma-separated exact origins in `SYSCENTRE_ALLOWED_ORIGINS`. Wildcard origins are ignored.

Example PowerShell calls:

```powershell
Invoke-RestMethod http://127.0.0.1:8765/api/repositories
Invoke-RestMethod 'http://127.0.0.1:8765/api/search?q=policy&limit=20'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8765/api/repositories/ingest -ContentType 'application/json' -Body '{"project_id":"networklab"}'
Invoke-RestMethod 'http://127.0.0.1:8765/api/repositories/networklab/files?limit=10'
```

## Google AI Studio app prompt

The full master prompt for building a separate Google AI Studio full-stack control plane is in [`docs/GOOGLE_AI_STUDIO_CONTROL_PLANE_PROMPT.md`](docs/GOOGLE_AI_STUDIO_CONTROL_PLANE_PROMPT.md). Supply that prompt together with `runtime/repository_catalog.json`, `runtime/project_inventory.json`, `runtime/project_runtime_registry.json`, and `runtime/repository_architectures.json`. The architecture file is the source-backed reference for app layers, entrypoints and limitations; it must not be used as evidence of deployment or health.

## Development checks

```powershell
python -m unittest discover -s runtime -p "test_*.py" -v
npm --prefix .\webapp install
npm --prefix .\webapp run build
```

## Current boundaries

### Executive portfolio classification

Each repository is classified by `business_model`, `system_type`, `sector`, `market_category`, `target_market`, `market_segments`, `portfolio_role`, and `lifecycle_stage`. The local API merges this strategy metadata into each project returned by `GET /api/repositories`; the dashboard uses it to group and drill down across the portfolio. The public static console reads the mirrored `bonus-app/systems.json` catalog and provides the same four executive segmentation views without requiring the local runtime.

Business models and target markets are planning hypotheses inferred from repository evidence, not verified market research. Pricing, customers, revenue, commercial traction, TAM/SAM/SOM, and geographic reach are not claimed unless independently evidenced. Every catalog record explicitly carries a monetization status and market-validation status. Empty repositories and scaffolds remain classified as unvalidated. Keep the canonical runtime catalog and the static mirror synchronized when updating portfolio metadata.

The executive register is a decision-support view, not a financial forecast: portfolio counts are computed from catalog fields, and evidence-gap totals do not imply commercial performance. The project registry and source index remain foundations for cross-project discovery. Automated dependency mapping, project-level semantic search, agent orchestration, approval workflows, and executable lifecycle adapters remain subsequent capabilities. The registry describes the required adapter slots but does not execute unverified project launch commands. Keep credentials out of the repository and do not treat policy allowlisting as a complete OS sandbox.
