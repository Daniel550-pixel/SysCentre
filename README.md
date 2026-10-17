# SysCentre

SysCentre is a standalone local-first systems control plane. It catalogs existing projects, indexes repository metadata and readable source files into a local SQLite database, and preserves each project's independent repository and runtime boundary.

## Current delivery target

The active two-day hub sprint is tracked in [`docs/SYSCENTRE_HUB_SPRINT.md`](docs/SYSCENTRE_HUB_SPRINT.md). The goal is to make every known project reachable from SysCentre, expose a verified interface or source/setup path, and show truthful run-readiness. A repository is not marked runnable until its project-specific launch adapter and health check have been verified. Empty or unfinished projects remain accessible but are not presented as working applications.

## Core architecture

- **WebApp:** React + TypeScript + Vite dashboard with a project registry and indexing controls.
- **Runtime:** Python standard-library HTTP API on `127.0.0.1:8765`.
- **Policy engine:** deterministic explicit allowlist; unknown commands are denied and recorded.
- **Event ledger:** SQLite database at `~/.syscentre/syscentre.db`, with up to 5,000 recent audit events.
- **Project registry:** `runtime/repository_catalog.json` records the 28 projects known to SysCentre, including executive portfolio metadata. `bonus-app/systems.json` mirrors this catalog for the static GitHub Pages application. `runtime/project_inventory.json` tracks historical/new project identities that still need exact repository reconciliation.
- **Executive control plane:** portfolio-wide grouping by business-model hypothesis, system type, sector, and market category, with an executive register that combines all four filters, searches target markets and portfolio roles, and surfaces market-validation, lifecycle, and monetization-evidence gaps. Each repository remains individually inspectable with source links and classification basis.
- **Repository indexer:** `runtime/repository_ingest.py` imports repository metadata, commit/tree identity, file paths, blob hashes, file sizes, and readable UTF-8 source/documentation content.
- **Runtime adapter registry:** `runtime/project_runtime_registry.json` has an explicit, initially unconfigured adapter profile for every one of the 28 repositories. The dashboard shows readiness and does not pretend unconfigured projects are runnable. `GET /api/runtime-projects` exposes this read-only registry.
- **Application architecture inventory:** `runtime/repository_architectures.json` maps the observed stack, entrypoints, implemented layers, state/data boundaries, declared integrations, evidence paths, source commit SHA, Git tree SHA, commit date, and inventory check date for all 28 repositories. `GET /api/repository-architectures` serves the searchable **Application architectures** explorer. It separately records repository hygiene findings using path metadata only (never secret contents), and distinguishes source-verified apps from partial prototypes, documentation-only projects and empty repositories. None of these snapshots assert deployment or runtime health. The human-readable [architecture audit](docs/REPOSITORY_ARCHITECTURE_AUDIT.md) mirrors this inventory. The cross-repository [duplication, architecture and risk audit](docs/CODEBASE_DUPLICATION_AUDIT.md) records confirmed duplicate blobs, overlapping product lineages, high-priority hygiene risks and the recommended remediation order.
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

## Start and synchronize on Windows

**Recommended: one-command activation.** From a clean clone of the repository, open PowerShell in the repository root and run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\Activate-SysCentre.ps1
```

The activation script checks Git, Python 3.11+, Node.js 20+, the expected `origin`, and the `main` branch; refuses to pull over uncommitted local changes; refreshes `main` with `git pull --rebase`; installs the locked webapp dependencies with `npm ci`; runs the production build; starts the runtime and Vite webapp; checks their local HTTP endpoints; and opens a separate PowerShell window for the Git sync watcher. It never force-pushes. Dependency or build failures stop activation before service startup.

- Dashboard: **http://127.0.0.1:5173**
- Runtime API: **http://127.0.0.1:8765**
- Health check: **http://127.0.0.1:8765/api/health**

The watcher checks every 60 seconds by default. It pulls with rebase before pushing and retries bounded non-fast-forward races. Auto-commit is **off by default**: uncommitted local changes pause sync to protect work. To explicitly allow the watcher to commit and push all local changes, run activation with `-AutoCommitSync` only after reviewing that behavior. You can adjust the watcher interval with `-SyncIntervalSeconds 120`, skip opening the watcher with `-NoGitWatcher`, or skip opening the browser with `-NoBrowser`.

For manual service startup without the activation checks, `.`scripts\Start-SysCentre.ps1` remains available. To run the watcher alone from the repository root:

```powershell
.\scripts\SysCentre-GitSync.ps1 -Watch -IntervalSeconds 60
```

The local services and watcher run only while the host computer is powered on and the relevant PowerShell processes remain open. This workflow does not turn on a sleeping or powered-off computer.

## Runtime API

- `GET /api/health` — liveness check
- `GET /api/status` — runtime state and environment
- `GET /api/events` — persisted audit events
- `GET /api/policy` — current allowlisted command catalog
- `GET /api/repositories` — catalog plus indexing status
- `GET /api/ingest-status?project_id=syscentre` — persisted per-project ingestion progress, including interrupted runs and checkpoint counts
- `GET /api/runtime-projects` — runtime adapter configuration/readiness for all registered repository records
- `GET /api/repository-architectures` — 28 evidence-backed architecture records with stack, entrypoints, layers, data/state, integrations, snapshot SHAs and limitations
- `GET /api/repositories/{project_id}/architecture-analysis` — static analysis of locally indexed source: imports, heuristic local dependency edges, framework signals, conventional entrypoints, inbound route patterns (including Python router aliases, Django URL patterns, JavaScript router aliases, Spring Java annotations, common Go router declarations, ASP.NET attributes, Laravel routes, and Ruby route declarations), outbound HTTP-client targets across Python/JavaScript plus common Go, .NET, Java, PHP, Ruby, Rust and PowerShell patterns, data-store signals, module inventory and limitations; outbound targets and route patterns are source evidence only, not verified network traffic or live endpoints; route declarations, outbound HTTP targets, and imports include source line references when detected, and project code is never executed
- `GET /api/architecture/api-map` — conservative cross-repository API relationship candidates when an outbound static URL matches another indexed repository’s configured API base URL and an exact declared route with a compatible detected HTTP method, plus an inventory of unmatched outbound HTTP targets; malformed URLs are ignored, no network calls are made, and candidates are not proof of live integrations
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

The full master prompt for building a separate Google AI Studio full-stack control plane is in [`docs/GOOGLE_AI_STUDIO_CONTROL_PLANE_PROMPT.md`](docs/GOOGLE_AI_STUDIO_CONTROL_PLANE_PROMPT.md). Supply that prompt together with `runtime/repository_catalog.json`, `runtime/project_inventory.json`, `runtime/project_runtime_registry.json`, and `runtime/repository_architectures.json`. The architecture file is the source-backed reference for app layers, entrypoints, inspected commit/tree identity, hygiene findings and limitations; it must not be used as evidence of deployment or health. The hygiene panel intentionally records only filenames and recommendations, never contents from `.env`, database dumps, logs or personal documents.

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

The executive register is a decision-support view, not a financial forecast: portfolio counts are computed from catalog fields, and evidence-gap totals do not imply commercial performance. The project registry and source index remain foundations for cross-project discovery. Automated dependency mapping, project-level semantic search, agent orchestration, approval workflows, and executable lifecycle adapters remain subsequent capabilities. The registry describes the required adapter slots but does not execute unverified project launch commands. The static source architecture analyzer operates only on source text already indexed in the local SQLite store. It reports heuristic evidence tied to the indexed commit; it does not establish runtime behavior, dependency resolution, deployment status or production health. Index a repository first, then use **Analyze indexed source** in its architecture card. Keep credentials out of the repository and do not treat policy allowlisting as a complete OS sandbox.
