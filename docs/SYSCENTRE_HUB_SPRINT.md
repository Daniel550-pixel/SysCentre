# SysCentre Hub Sprint — 17–18 October 2026

## Outcome

Turn SysCentre from a portfolio inventory into the single entry point for every known project: discover it, understand it, open its real interface or source, follow its setup/runbook, and see whether it is actually runnable and healthy. Preserve each project's own repository, dependencies, data, secrets, and lifecycle.

**Definition of usable:** every project identity is represented in the hub and has an explicit, evidence-backed access state. Where a working interface or deployment exists, the hub links to it. Where a project is local-only, it has a verified project-specific launch profile and isolated runtime adapter before launch controls are enabled. Where the repository is empty, documentation-only, or an unfinished scaffold, the hub says so and provides the next implementation step instead of pretending it runs.

## Day 1 — Saturday 17 October: inventory and hub foundation

1. Reconcile the 28 canonical repositories against the live GitHub account and preserve exact repository URLs/default branches.
2. Reconcile historical project identities separately; never guess that two names are the same project.
3. For each repository, record:
   - implementation maturity (working app, partial prototype, documentation-only, empty/scaffold);
   - interface type and verified interface URL, if any;
   - local entrypoint and dependency/install requirements when evidenced by source;
   - required environment/configuration, with secret *names* only—never values;
   - runtime adapter type, health-check method, allowed actions, and approval needs;
   - what is verified versus unknown, with source evidence and check date.
4. Make the hub the default navigation: portfolio overview, project launchpad, architecture/source explorer, integrations, runtime health, and audit history.
5. Add an explicit usability/readiness summary so an unconfigured project cannot be mistaken for a runnable one.

**Day 1 acceptance checks**
- All canonical repositories appear exactly once.
- Every record links to its exact GitHub repository and architecture evidence.
- Every project has an honest access/readiness state and a concrete next step.
- Unknown deployment URLs and launch commands remain unset until verified.
- Existing tests and production build pass.

## Day 2 — Sunday 18 October: project access and controlled execution

1. Group projects by real launch mechanism (existing web deployment, static web app, local web app/API, desktop/CLI, or not runnable yet).
2. Implement and test reusable adapters for the verified launch mechanisms; do not create 28 bespoke shells where a safe shared adapter suffices.
3. Add project detail / launchpad actions: open verified UI, open source, view setup instructions, index source, inspect architecture, and run health checks where supported.
4. Enable start/stop/restart only for projects with reviewed, allowlisted adapter profiles. Keep each process isolated, with timeouts, health checks, explicit environment configuration, audit events, and approval for mutating/high-risk actions.
5. Add smoke tests and a final readiness report for all 28 projects plus unresolved historical identities.

**Day 2 acceptance checks**
- Every project can be reached from SysCentre and has a usable next action.
- Verified deployed interfaces open directly from the hub.
- Verified local projects can be launched and health-checked through a typed adapter.
- Unconfigured, empty, and incomplete projects are visibly marked and are not offered fake launch buttons.
- No arbitrary shell execution, no inferred commands, no shared secrets, no cross-project data mixing, and no force-push.
- CI tests and webapp production build pass.

## Delivery order

1. **Project access and truthful readiness** — foundation for every other integration.
2. **Highest-confidence existing interfaces** — surface verified deployed/local apps first.
3. **Reusable local launch adapters** — only after inspecting entrypoints and dependency files.
4. **Health, logs, audit, and approvals** — required before lifecycle controls.
5. **Unfinished projects** — accessible through their source, architecture, and a clear implementation backlog; they cannot honestly be called runnable until code exists.

## Non-negotiable boundaries

- SysCentre orchestrates independent projects; it does not merge them into one codebase.
- Static indexing and architecture inference never execute project code.
- A README, entrypoint filename, or deployment field is not proof that an app starts successfully.
- A project is **Runnable** only after its adapter and launch target are verified and its health check succeeds.
- Financial, trading, security, and infrastructure projects require extra caution around credentials, external side effects, and live operations.
- Historical names are not mapped to a repository without exact evidence and explicit reconciliation.

## Status

- [x] Canonical 28-project catalog and architecture inventory exist.
- [x] Per-project runtime adapter slots and readiness UI exist.
- [x] Source indexing, architecture analysis, cross-repository search, and audit events exist.
- [x] Initial unified project hub launchpad with repository/source/index/architecture access (live deployments and runnable adapters remain unverified).
- [x] Policy-gated lifecycle API: session inventory plus start/stop/restart routes, allowlisted executable names, isolated workspaces, shell disabled, and per-project logs.
- [x] Hub UI lifecycle controls, process/health state, and Open app link.
- [x] First source-backed launch profile for Localhost-webapp, with a dedicated PowerShell workspace provisioning script and locked dependency installation opt-in.
- [x] Second source-backed launch profile for NetworkLab: isolated workspace, Python standard-library server, loopback-only health check, and explicit boundary excluding automatic VirtualBox/network changes.
- [ ] Run NetworkLab through SysCentre on the user's machine and confirm startup, health, stop, and restart behavior.
- [x] Loopback-only HTTP health probes and tests for unsafe health URLs and healthy-session reporting.
- [ ] Run Localhost-webapp on a user's machine and confirm end-to-end startup, health, stop, and restart behavior.
- [ ] Process recovery/adoption after SysCentre restarts.
- [ ] Source-backed launch profiles and setup checklists for remaining implemented projects.
- [ ] Full 28-project readiness report and final smoke-test results.
