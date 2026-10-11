# Cross-Repository Architecture, Duplication and Risk Audit

> **Inventory date:** 2026-10-11  
> **Account:** Daniel550-pixel  
> **Coverage:** 28 repositories; based on the checked-in architecture register and targeted GitHub blob comparisons.  
> **Scope:** Static source and metadata review. No project was started, built, or tested as part of this report.

## Executive result

The portfolio contains **28 repositories, 20 source-verified, 3 source-limited, 3 documentation-only and 2 empty**. “Source-verified” means source entrypoints/layers were found; it does not mean features work, tests pass, or deployments are healthy.

The measured inventory is 1,274 source files and 215,563 lines across the audit's selected source/configuration/documentation extensions. These totals include possible repeated and non-executable text and must not be described as unique executable code.

### Highest-priority findings

1. **HIGH — Credentials risk:** `FinSight_Global_AI_Dashboard/.env` is tracked in Git. Its contents were intentionally not opened. Review repository access and history; rotate any real credentials; remove it from future commits; keep a redacted `.env.example`. Deleting a file in a new commit does not erase prior Git history.
2. **HIGH — Personal/recovery artifacts in two repositories:** `ai-trading-dashboard` and `FinSight-Global-AI-2` track personal email/PDF/document exports, archives/shortcuts and a recovered SQL dump alongside source. Treat them as potentially sensitive. Review repository visibility and history, then remove unrelated artifacts and add ignore rules. Do not copy their contents into the portfolio index.
3. **HIGH — Confirmed duplicate starter files:** GitHub blob SHA comparisons confirm three identical file-content pairs across `FinSight-Global-AI-2` and `ai-trading-dashboard`: `main.py` in both; `FinSight-Global-AI-2/streamlit_app.py` and `ai-trading-dashboard/dashboard.py`; and `requirements.txt` in both. The FastAPI `POST /run` handler returns a success string but does not execute a model. The Streamlit page is a generated placeholder. This is duplicated scaffold, not proof of duplicated working trading functionality.
4. **HIGH — Possible Python entrypoint contamination:** `FinSight-Global-AI/streamlit_app.py` is approximately 78 KB and contains shell-session transcript text after the visible Streamlit welcome lines. This appears inconsistent with a clean Python entrypoint and may prevent parsing. Verify with a local syntax check before trying to run it; do not assume the declared ML dependencies are wired into a functioning app.
5. **MEDIUM — Runtime log tracked:** `Business-OS/.business-os-data/security-events.jsonl` is committed. Confirm it contains only sanitized synthetic data; move runtime logs outside version control and ignore the data directory if it contains real operational events.
6. **MEDIUM — Two competing ARCHOS implementations:** `ArchOS-Repo` and `archos-3` are different codebases, not exact copies. They overlap in product identity but differ in implementation and scope. Select a canonical product repository and define the other as a prototype/archive or a clearly bounded subproject.
7. **MEDIUM — Factory lineage needs an explicit contract:** `The-Factory` is a Python alpha package of reusable primitives; `The-Factory-2.0` is a React/TypeScript/Express operational control plane. They are not a simple version-to-version copy. Define whether the Python package is a reference/prototype, a separate kernel package, or to be retired; do not merge blindly across languages.
8. **MEDIUM — Empty/concept repos can be mistaken for products:** `AI-OS-Global-Wealth-Engine` and `ai-trading-dashboard-2` are empty; `AIOS-System`, `AI-OS-Global-Super-App`, and `ai-trading-dashboard-3` are documentation-only. `AIOS-Core-Architect.` is source-limited and references missing config files. Keep these statuses visible in the portfolio.
9. **MEDIUM — Production controls are not verified:** The Factory 2.0 README itself says authentication, deterministic authorization, independent evidence verification, durable integrity and execution isolation need further hardening. Treat it as development/controlled-demo software until tests establish the security boundaries.
10. **MEDIUM — Data/runtime assumptions:** `archos-3` initializes world entities and events in process memory; no durable store is evidenced in the scanned backend entrypoint. This is a prototype limitation if state must survive restarts.

## Confirmed exact duplication

The following Git blob hashes matched exactly at the audited default-branch snapshots:

| Repository A / path | Repository B / path | Result |
|---|---|---|
| `FinSight-Global-AI-2/main.py` | `ai-trading-dashboard/main.py` | Exact same blob |
| `FinSight-Global-AI-2/streamlit_app.py` | `ai-trading-dashboard/dashboard.py` | Exact same blob |
| `FinSight-Global-AI-2/requirements.txt` | `ai-trading-dashboard/requirements.txt` | Exact same blob |

This establishes shared scaffold files only. The repositories' full tree SHAs differ, so do not call the complete repositories identical.

## Overlap clusters and recommended boundaries

### 1. ARCHOS: `ArchOS-Repo` and `archos-3`

- **ArchOS-Repo:** larger, multi-layer system with FastAPI backend, React/TypeScript spatial experience, policy/action gates, world-model/simulation routes, identity/auth and orchestration modules.
- **archos-3:** separate FastAPI/WebSocket prototype and React/TypeScript client; the inspected backend uses in-memory world entities/events and has unresolved client package/build wiring in the scanned tree.
- **Decision:** keep `ArchOS-Repo` as the default canonical candidate for the main ARCHOS product because it is the broader implementation, subject to a feature/test comparison. Mark `archos-3` as prototype/legacy unless a unique capability is explicitly migrated. Do not delete or merge until the feature and history comparison is complete.

### 2. FinSight and trading analytics

Repositories: `FinSight-Global-AI`, `FinSight-Global-AI-2`, `FinSight-Global-AI-4`, `FinSight_Global_AI_Dashboard`, `ai-trading-dashboard`, `ai-trading-dashboard-2`, `ai-trading-dashboard-3`, and `FGSE`.

- `FinSight-Global-AI-2` and `ai-trading-dashboard` share the three exact starter blobs above and both contain personal/recovery artifacts. The main API route is a placeholder, not a model execution pipeline.
- `FinSight-Global-AI` declares a broad ML/data stack, but its visible Streamlit entrypoint includes apparent shell transcript contamination. Audit and repair the entrypoint before assessing its actual analytics.
- `FinSight_Global_AI_Dashboard` has the most substantial dedicated Streamlit workstation described in the architecture register, but a tracked `.env` is a credential-risk finding and its module wiring still needs runtime verification.
- `FinSight-Global-AI-4` is a two-file minimal app variant; `ai-trading-dashboard-2` is empty; `ai-trading-dashboard-3` is README-only.
- `FGSE` is a distinct React/Express/SQLite application, not merely another Streamlit clone.
- **Decision:** designate one canonical financial dashboard, one separate trading/portfolio analytics product if its functionality is truly distinct, and label remaining repositories as archive/prototype/empty. Compare features, tests, data adapters and deployment before choosing the canonical FinSight repo. Never combine credentials or real trading capabilities as part of a consolidation.

### 3. The Factory: Python primitives and TypeScript control plane

- `The-Factory` provides Python package-level primitives; its default event ledger is an in-memory reference implementation, so it is not durable audit storage by itself.
- `The-Factory-2.0` provides the current React/TypeScript/Express UI and runtime modules, with npm scripts for lint/test/build. Its own security policy warns that production boundaries are incomplete.
- **Decision:** document a contract between shared kernel semantics and the UI/runtime implementation. Preserve `AI DECIDES ≠ AI EXECUTES`, deterministic policy decisions, independent evidence verification, explicit authorization, durable event storage, replay/idempotency and fail-closed behavior as acceptance tests. Do not claim the two repositories are integrated unless an explicit tested interface exists.

### 4. AIOS / assistant-system identity

- `AI-mainframe`: small dependency-free Python capability registry, designed to delegate consequential execution/governance to ARCHOS.
- `AIOS-Core-Architect.`: tiny Gradio simulation that references missing config files; revenue behavior is simulated, not a verified revenue integration.
- `AIOS-System` and `AI-OS-Global-Super-App`: documentation-only.
- `AI-OS-Global-Wealth-Engine`: empty.
- **Decision:** preserve these as separate repository records, but do not present all of them as runnable AIOS products. Confirm intended identity and source-of-truth mapping before implementing or renaming.

### 5. Overlapping developer/business interfaces

- `Business-OS`: React/Vite/Express/Gemini business workspace with rich panels.
- `ExperienceEngine`: React/Vite/Express code-generation workspace with Gemini integration.
- `The-House-Of-Coding`: Next.js web app plus Express API and OpenAI SDK.
- `Localhost-webapp`: stock Next.js starter scaffold, not a verified product.
- **Decision:** compare actual user workflows and service contracts. Reuse design-system components or service packages only after boundaries are identified; do not merge products just because they share React/Express/LLM dependencies.

### 6. Security/integrity primitives across products

`SecureOS`, `BitMiner-AI`, `ArchOS-Repo`, `The-Factory` and `The-Factory-2.0` contain overlapping security, policy, event, verification, replay or agent-governance concepts. The overlap is architectural rather than confirmed file duplication.

**Decision:** define shared contracts and conformance tests before extracting a common library. Keep product-specific threat models and authorization decisions isolated. A module name or README claim is not evidence of an enforced control.

## Repository architecture inventory

| Repository | Status | Observed implementation / primary gap |
|---|---|---|
| `ArchOS-Repo` | Source verified | Python/FastAPI + React/TypeScript; broad ARCHOS platform. Runtime/deployment not verified. |
| `archos-3` | Source verified | FastAPI/WebSocket + React/TypeScript; in-memory world/event state; client package wiring needs checking. |
| `The-Factory` | Source verified | Python alpha primitives; event ledger default is in-memory. |
| `The-Factory-2.0` | Source verified | React/TypeScript + Express control plane; production security boundaries incomplete by its own policy. |
| `SysCentre` | Source verified | Python/SQLite + React/Vite portfolio/index control plane; adapters intentionally unconfigured. |
| `FinSight-Global-AI` | Source verified | Python/Streamlit plus broad ML dependencies; entrypoint appears contaminated by shell transcript. |
| `FinSight-Global-AI-2` | Source verified | Python/FastAPI + Streamlit generated placeholder; exact scaffold overlaps `ai-trading-dashboard`. |
| `FinSight-Global-AI-4` | Source verified | Minimal Python/Streamlit, two-file variant. |
| `FinSight_Global_AI_Dashboard` | Source verified | Python/Streamlit finance workstation; tracked `.env` risk. |
| `ai-trading-dashboard` | Source verified | Python/FastAPI + dashboard scaffold; no real model run proven; personal/recovery artifacts tracked. |
| `ai-trading-dashboard-2` | Empty | No source tree. |
| `ai-trading-dashboard-3` | Documentation only | README-only concept. |
| `FGSE` | Source verified | React/Vite + Express + SQLite finance/trading app; live account/trade behavior unverified. |
| `AI-mainframe` | Source verified | Small Python capability registry; not a standalone web app. |
| `AIOS-Core-Architect.` | Source limited | Python/Gradio simulation; missing referenced configs and questionable requirements file. |
| `AIOS-System` | Documentation only | README-only concept. |
| `AI-OS-Global-Super-App` | Documentation only | README-only concept. |
| `AI-OS-Global-Wealth-Engine` | Empty | No source tree. |
| `SecureOS` | Source verified | React/Vite + Express security/integrity workstation; actual host protection unverified. |
| `BitMiner-AI` | Source verified | React/Vite + Express domain modules for mining/ledger/verification; production wiring unverified. |
| `AI-Venture-Radar` | Source limited | Python domain models/scoring only; no service, ingestion, persistence or UI. |
| `Obsidian-AI` | Source verified | React/TypeScript + Firebase Auth/Firestore + Gemini; server hosting boundary unclear. |
| `NetworkLab` | Source verified | Python stdlib localhost API + HTML/CSS/JS + PowerShell/VirtualBox; live lab state must be observed separately. |
| `Business-OS` | Source verified | React/Vite + Express + Gemini; tracked runtime security-event log. |
| `ExperienceEngine` | Source verified | React/Vite + Express + Gemini; server code cache is in-memory. |
| `The-House-Of-Coding` | Source verified | Next.js + Express + OpenAI SDK; build/runtime not verified. |
| `Localhost-webapp` | Source limited | Next.js starter template, no actual product workflow found. |
| `OneDrive-Cleanup-Controller` | Source verified | PowerShell file-management controller; destructive synced deletion requires careful testing. |

## Recommended execution plan

### P0 — Contain exposure and remove repository contamination

1. Review `FinSight_Global_AI_Dashboard/.env` access and Git history. Rotate any real credentials. Remove from future commits and retain a redacted example.
2. Review repository visibility/history and remove unrelated personal/recovery artifacts from `ai-trading-dashboard` and `FinSight-Global-AI-2`. Inspect SQL/archive files locally only; do not import their contents into SysCentre.
3. Verify whether `FinSight-Global-AI/streamlit_app.py` parses as Python. Replace accidental shell transcript content with a clean entrypoint only after preserving intended code safely.
4. Confirm whether the Business-OS JSONL file is synthetic. Remove real runtime logs from source control.

### P1 — Establish canonical products

5. Run feature/test/entrypoint comparison for `ArchOS-Repo` versus `archos-3`; select one canonical ARCHOS source of truth.
6. Choose the canonical FinSight dashboard and distinguish it from any separate trading analytics product. Archive or label empty/generated variants.
7. Define the intended relationship between Python `The-Factory` and TypeScript `The-Factory-2.0`; record contracts and acceptance tests.

### P2 — Validate behavior, not names

8. Run each repository's declared lint/test/build checks in its own environment; record exact command, commit SHA, exit code and logs. Do not run projects as part of static indexing.
9. Validate that advertised integrations are actually wired: model calls, market-data feeds, databases, authentication, broker connectivity and external action execution.
10. Add per-repository status fields in SysCentre: source status, build status, test status, deployment status, secret hygiene, canonical/legacy designation and last verified commit. Keep unknown states as unknown.
11. Only after the above, perform file-level deduplication beyond the three exact blob pairs and extract shared security/runtime primitives behind explicit interfaces.

## Verification limitations

- This report uses SysCentre's architecture snapshots plus targeted GitHub blob SHA comparisons. It is not a full AST-level clone detector.
- No build, unit test, integration test, runtime launch, network call or deployment health check was executed for the 28 projects during this report.
- A dependency manifest can list unused packages; an entrypoint can be a placeholder even when the repository contains many modules.
- No secret, personal document, recovered SQL dump, or operational log contents were opened or reproduced for this report.
- ArchOS-Repo was previously measured from Git objects because a tracked Windows-invalid path prevents a normal full checkout; its measured tree is still represented in the architecture snapshot.

## Source references

- [SysCentre architecture audit](REPOSITORY_ARCHITECTURE_AUDIT.md)
- [SysCentre repository architecture register](../runtime/repository_architectures.json)
- [SysCentre repository catalog](../runtime/repository_catalog.json)
- [The Factory](https://github.com/Daniel550-pixel/The-Factory)
- [The Factory 2.0](https://github.com/Daniel550-pixel/The-Factory-2.0)
- [ArchOS-Repo](https://github.com/Daniel550-pixel/ArchOS-Repo)
- [archos-3](https://github.com/Daniel550-pixel/archos-3)
- [FinSight-Global-AI-2](https://github.com/Daniel550-pixel/FinSight-Global-AI-2)
- [ai-trading-dashboard](https://github.com/Daniel550-pixel/ai-trading-dashboard)
- [FinSight_Global_AI_Dashboard](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard)
