# Repository Application Architecture Audit

> **Inventory checked:** 2026-10-11 · **Repositories:** 28 · **Source of truth:** [`runtime/repository_architectures.json`](../runtime/repository_architectures.json)

This is a source-tree architecture audit, not a deployment report. It identifies observed application layers, entrypoints, technology declarations, state/data boundaries, integrations and known gaps from the tracked files at each recorded commit. A dependency or module name is not proof of live wiring. Deployment and runtime health remain explicitly unverified.

## Portfolio coverage

| Architecture status | Repositories | Meaning |
|---|---:|---|
| Source verified | 20 | Application or package implementation is present in tracked source; integration/runtime health still requires separate verification. |
| Source limited | 3 | Some domain/runtime code exists, but a runnable app, major layers, or source evidence is incomplete. |
| Documentation only | 3 | A concept or architecture README exists without a runnable implementation in the inspected tree. |
| Empty repository | 2 | GitHub reports no tracked Git tree or source files. |

## Repository hygiene findings

The source tree scan surfaced **4 path-level finding(s)** across 4 repositories. Sensitive files were not opened or copied into SysCentre; findings identify paths and remediation steps only.

- **HIGH — ai-trading-dashboard: Personal and recovered artifacts mixed into source.** Tracked paths include personal email/PDF/document exports, desktop shortcuts, ZIP archives and a recovered SQL dump alongside application source. This creates privacy, data-retention and accidental-disclosure risk. Evidence: [`Fw_ Bewijs van inschrijving.eml`](https://github.com/Daniel550-pixel/ai-trading-dashboard/blob/master/Fw_%20Bewijs%20van%20inschrijving.eml), [`OA_AP_D09C Bewijs van inschrijving (Briefpapier).pdf`](https://github.com/Daniel550-pixel/ai-trading-dashboard/blob/master/OA_AP_D09C%20Bewijs%20van%20inschrijving%20(Briefpapier).pdf), [`Recovered-feb-25-2025-0947.~vs3CF8.sql`](https://github.com/Daniel550-pixel/ai-trading-dashboard/blob/master/Recovered-feb-25-2025-0947.~vs3CF8.sql), [`ChatGPT gesprekken FinSight Global AI OS Platform.odt`](https://github.com/Daniel550-pixel/ai-trading-dashboard/blob/master/ChatGPT%20gesprekken%20FinSight%20Global%20AI%20OS%20Platform.odt) Recommended action: Review repository visibility and Git history; remove unrelated personal/recovered artifacts in a separate cleanup commit, add targeted ignore rules, and inspect the SQL/archive contents locally without copying them into SysCentre.
- **HIGH — FinSight-Global-AI-2: Legacy repository contains personal and recovery artifacts.** Tracked paths include personal email/PDF/document exports, desktop shortcuts, ZIP archives and a recovered SQL dump alongside legacy application source. Treat these as potentially sensitive; their contents were not read by SysCentre. Evidence: [`Fw_ Bewijs van inschrijving.eml`](https://github.com/Daniel550-pixel/FinSight-Global-AI-2/blob/main/Fw_%20Bewijs%20van%20inschrijving.eml), [`OA_AP_D09C Bewijs van inschrijving (Briefpapier).pdf`](https://github.com/Daniel550-pixel/FinSight-Global-AI-2/blob/main/OA_AP_D09C%20Bewijs%20van%20inschrijving%20(Briefpapier).pdf), [`Recovered-feb-25-2025-0947.~vs3CF8.sql`](https://github.com/Daniel550-pixel/FinSight-Global-AI-2/blob/main/Recovered-feb-25-2025-0947.~vs3CF8.sql), [`ChatGPT gesprekken FinSight Global AI OS Platform.odt`](https://github.com/Daniel550-pixel/FinSight-Global-AI-2/blob/main/ChatGPT%20gesprekken%20FinSight%20Global%20AI%20OS%20Platform.odt) Recommended action: Review repository visibility and Git history; remove unrelated artifacts in a separate cleanup commit, add ignore rules, and inspect any SQL/archive files locally for credentials or personal information before retaining them.
- **HIGH — FinSight_Global_AI_Dashboard: Tracked .env file.** The current tracked tree contains a .env file. Its contents were not read or copied into SysCentre. If it contains real credentials, they may be exposed to repository readers and Git history. Evidence: [`.env`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/.env) Recommended action: Review the file and repository access immediately; rotate any real credentials, remove the file from future commits, add it to .gitignore, and keep only a redacted .env.example. Historical commits may still contain prior values.
- **MEDIUM — Business-OS: Runtime security-event log is tracked.** The repository tree contains a runtime security event log under .business-os-data. Its contents were not inspected or copied; logs can contain operational identifiers or sensitive event details. Evidence: [`.business-os-data/security-events.jsonl`](https://github.com/Daniel550-pixel/Business-OS/blob/main/.business-os-data/security-events.jsonl) Recommended action: Confirm the file is a safe synthetic fixture; otherwise move runtime logs outside version control, ignore the directory, and retain only a sanitized sample or schema.

## Detailed architecture register

### FinSight-Global-AI

- **Status:** `source-verified`
- **Repository:** https://github.com/Daniel550-pixel/FinSight-Global-AI
- **Default branch:** `main`
- **Inspected commit:** [`db006841c3369938a126449e30f708052ec6d21d`](https://github.com/Daniel550-pixel/FinSight-Global-AI/commit/db006841c3369938a126449e30f708052ec6d21d)
- **Git tree SHA:** `cd71dc4e56f43544e9e0caa63d33ee1998b6bf06`
- **Commit date:** 2025-11-10T12:21:43Z
- **Inventory check date:** 2026-10-11

Python finance dashboard repository with a Streamlit UI entrypoint, additional app/dashboard modules, and data/ML dependencies. The checked-in Streamlit entrypoint itself is currently a minimal title/welcome screen; the dependency list alone does not prove model features are wired in.

**Technology stack**

- Python
- Streamlit
- FastAPI and Uvicorn dependencies (usage not confirmed in the inspected entrypoint)
- Pandas / NumPy / scikit-learn / TensorFlow / PyTorch dependencies
- Dockerfile present

**Application entrypoints**

- [`streamlit_app.py`](https://github.com/Daniel550-pixel/FinSight-Global-AI/blob/main/streamlit_app.py)
- [`app.py`](https://github.com/Daniel550-pixel/FinSight-Global-AI/blob/main/app.py)
- [`dashboard.py`](https://github.com/Daniel550-pixel/FinSight-Global-AI/blob/main/dashboard.py)

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| UI | Streamlit browser dashboard | streamlit_app.py | [`streamlit_app.py`](https://github.com/Daniel550-pixel/FinSight-Global-AI/blob/main/streamlit_app.py), [`requirements.txt`](https://github.com/Daniel550-pixel/FinSight-Global-AI/blob/main/requirements.txt) |
| Application modules | Python app and dashboard modules exist; deeper runtime linkage needs inspection | app.py, dashboard.py, src/my_module.py | [`app.py`](https://github.com/Daniel550-pixel/FinSight-Global-AI/blob/main/app.py), [`dashboard.py`](https://github.com/Daniel550-pixel/FinSight-Global-AI/blob/main/dashboard.py), [`src/my_module.py`](https://github.com/Daniel550-pixel/FinSight-Global-AI/blob/main/src/my_module.py) |
| Packaging | Container build scaffold | Docker image configuration | [`Dockerfile`](https://github.com/Daniel550-pixel/FinSight-Global-AI/blob/main/Dockerfile) |

**State and data**

- No persistent datastore configuration verified from inspected files.

**External integrations**

- Listed requirements include financial-data and ML libraries; actual live data/model behavior is not verified.

**Additional evidence files**

- [`README.md`](https://github.com/Daniel550-pixel/FinSight-Global-AI/blob/main/README.md)
- [`streamlit_app.py`](https://github.com/Daniel550-pixel/FinSight-Global-AI/blob/main/streamlit_app.py)
- [`app.py`](https://github.com/Daniel550-pixel/FinSight-Global-AI/blob/main/app.py)
- [`dashboard.py`](https://github.com/Daniel550-pixel/FinSight-Global-AI/blob/main/dashboard.py)
- [`src/my_module.py`](https://github.com/Daniel550-pixel/FinSight-Global-AI/blob/main/src/my_module.py)
- [`requirements.txt`](https://github.com/Daniel550-pixel/FinSight-Global-AI/blob/main/requirements.txt)
- [`Dockerfile`](https://github.com/Daniel550-pixel/FinSight-Global-AI/blob/main/Dockerfile)

**Gaps and caveats**

- Dependency breadth exceeds the currently visible entrypoint implementation; treat advertised analytics as unverified until traced through source.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### ai-trading-dashboard

- **Status:** `source-verified`
- **Repository:** https://github.com/Daniel550-pixel/ai-trading-dashboard
- **Default branch:** `master`
- **Inspected commit:** [`7f9f2055744719bbc28cca7de5de1c11ae838fa9`](https://github.com/Daniel550-pixel/ai-trading-dashboard/commit/7f9f2055744719bbc28cca7de5de1c11ae838fa9)
- **Git tree SHA:** `a3c1d7c12e75c60f4ebdbef286ef26bcc7f0fd35`
- **Commit date:** 2025-11-04T12:12:21Z
- **Inventory check date:** 2026-10-11

Python financial analysis project with a FastAPI service entrypoint and a separate dashboard script; pinned dependencies also include Streamlit and market-data/scikit-learn libraries.

**Technology stack**

- Python
- FastAPI
- Uvicorn
- Streamlit dependency
- Pandas / NumPy / scikit-learn / joblib / yfinance

**Application entrypoints**

- [`main.py`](https://github.com/Daniel550-pixel/ai-trading-dashboard/blob/master/main.py)
- [`dashboard.py`](https://github.com/Daniel550-pixel/ai-trading-dashboard/blob/master/dashboard.py)

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| API | FastAPI app exposes GET / and POST /run | Root endpoint and model trigger placeholder | [`main.py`](https://github.com/Daniel550-pixel/ai-trading-dashboard/blob/master/main.py) |
| Dashboard | Separate dashboard module; UI framework inferred from pinned Streamlit dependency, source not fully inspected here | dashboard.py | [`dashboard.py`](https://github.com/Daniel550-pixel/ai-trading-dashboard/blob/master/dashboard.py), [`requirements.txt`](https://github.com/Daniel550-pixel/ai-trading-dashboard/blob/master/requirements.txt) |
| Analytics | Python analysis/model modules in repository tree | Models / data processing | [`requirements.txt`](https://github.com/Daniel550-pixel/ai-trading-dashboard/blob/master/requirements.txt) |

**State and data**

- No durable datastore was verified from the inspected entrypoint.

**External integrations**

- yfinance dependency indicates market data access capability; live connectivity not tested.

**Repository hygiene findings**

- **HIGH — Personal and recovered artifacts mixed into source:** Tracked paths include personal email/PDF/document exports, desktop shortcuts, ZIP archives and a recovered SQL dump alongside application source. This creates privacy, data-retention and accidental-disclosure risk.
  - Evidence: [`Fw_ Bewijs van inschrijving.eml`](https://github.com/Daniel550-pixel/ai-trading-dashboard/blob/master/Fw_%20Bewijs%20van%20inschrijving.eml), [`OA_AP_D09C Bewijs van inschrijving (Briefpapier).pdf`](https://github.com/Daniel550-pixel/ai-trading-dashboard/blob/master/OA_AP_D09C%20Bewijs%20van%20inschrijving%20(Briefpapier).pdf), [`Recovered-feb-25-2025-0947.~vs3CF8.sql`](https://github.com/Daniel550-pixel/ai-trading-dashboard/blob/master/Recovered-feb-25-2025-0947.~vs3CF8.sql), [`ChatGPT gesprekken FinSight Global AI OS Platform.odt`](https://github.com/Daniel550-pixel/ai-trading-dashboard/blob/master/ChatGPT%20gesprekken%20FinSight%20Global%20AI%20OS%20Platform.odt)
  - Recommended action: Review repository visibility and Git history; remove unrelated personal/recovered artifacts in a separate cleanup commit, add targeted ignore rules, and inspect the SQL/archive contents locally without copying them into SysCentre.

**Additional evidence files**

- [`main.py`](https://github.com/Daniel550-pixel/ai-trading-dashboard/blob/master/main.py)
- [`dashboard.py`](https://github.com/Daniel550-pixel/ai-trading-dashboard/blob/master/dashboard.py)
- [`requirements.txt`](https://github.com/Daniel550-pixel/ai-trading-dashboard/blob/master/requirements.txt)

**Gaps and caveats**

- The /run endpoint currently returns a simple success result; do not treat it as proof a real model was executed.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### ai-trading-dashboard-2

- **Status:** `empty`
- **Repository:** https://github.com/Daniel550-pixel/ai-trading-dashboard-2
- **Default branch:** `main`
- **Inspected commit:** None — repository has no Git commit
- **Git tree SHA:** None — repository has no Git tree
- **Commit date:** No commit
- **Inventory check date:** 2026-10-11

GitHub reports an empty repository with no Git tree, source files, manifests, or entrypoint to analyze.

**Technology stack**

- No stack confirmed

**Application entrypoints**

- No runnable application entrypoint verified.

**Layers and components**

No application layers can be confirmed from the current source tree.

**State and data**

- No state/persistence layer verified.

**External integrations**

- No external integration verified.

**Gaps and caveats**

- Repository has no Git objects / source tree; architecture remains unassessed.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### ai-trading-dashboard-3

- **Status:** `documentation-only`
- **Repository:** https://github.com/Daniel550-pixel/ai-trading-dashboard-3
- **Default branch:** `main`
- **Inspected commit:** [`fc602daca1e43d10091244d595765c93bdda1a47`](https://github.com/Daniel550-pixel/ai-trading-dashboard-3/commit/fc602daca1e43d10091244d595765c93bdda1a47)
- **Git tree SHA:** `b58db45cf805f7f33666aa0fa341a71447c1e980`
- **Commit date:** 2025-11-04T12:04:27Z
- **Inventory check date:** 2026-10-11

README-only concept repository. No app code, dependency manifest, or runnable entrypoint is present in the scanned default-branch tree.

**Technology stack**

- No implementation stack confirmed

**Application entrypoints**

- [`README.md`](https://github.com/Daniel550-pixel/ai-trading-dashboard-3/blob/main/README.md)

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| Documentation | Concept description only | README | [`README.md`](https://github.com/Daniel550-pixel/ai-trading-dashboard-3/blob/main/README.md) |

**State and data**

- No application state layer implemented.

**External integrations**

- No external integration verified.

**Additional evidence files**

- [`README.md`](https://github.com/Daniel550-pixel/ai-trading-dashboard-3/blob/main/README.md)

**Gaps and caveats**

- Any intended architecture is a concept, not an implemented application.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### FinSight-Global-AI-2

- **Status:** `source-verified`
- **Repository:** https://github.com/Daniel550-pixel/FinSight-Global-AI-2
- **Default branch:** `main`
- **Inspected commit:** [`121a6ba2e90e7b173feefe438f84e793df742d0d`](https://github.com/Daniel550-pixel/FinSight-Global-AI-2/commit/121a6ba2e90e7b173feefe438f84e793df742d0d)
- **Git tree SHA:** `17bf6ed9e36015002d4d340c7a682d3e16b39a98`
- **Commit date:** 2025-11-04T14:32:02Z
- **Inventory check date:** 2026-10-11

Legacy Python finance workspace with FastAPI/Streamlit dependencies and two app entrypoints. Its current Streamlit page describes itself as a generated placeholder; deeper module behavior should not be inferred from the repo name.

**Technology stack**

- Python
- FastAPI / Uvicorn dependencies
- Streamlit
- Pandas / NumPy / scikit-learn / yfinance

**Application entrypoints**

- [`main.py`](https://github.com/Daniel550-pixel/FinSight-Global-AI-2/blob/main/main.py)
- [`streamlit_app.py`](https://github.com/Daniel550-pixel/FinSight-Global-AI-2/blob/main/streamlit_app.py)

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| API / core | Python service entrypoint present; route behavior should be inspected before operational use | main.py | [`main.py`](https://github.com/Daniel550-pixel/FinSight-Global-AI-2/blob/main/main.py), [`requirements.txt`](https://github.com/Daniel550-pixel/FinSight-Global-AI-2/blob/main/requirements.txt) |
| UI | Streamlit placeholder dashboard | Default generated dashboard message | [`streamlit_app.py`](https://github.com/Daniel550-pixel/FinSight-Global-AI-2/blob/main/streamlit_app.py) |
| Analytics modules | Python source tree contains multiple modules | Legacy model / finance modules | [`requirements.txt`](https://github.com/Daniel550-pixel/FinSight-Global-AI-2/blob/main/requirements.txt) |

**State and data**

- No persistence implementation confirmed in inspected manifest/entrypoint.

**External integrations**

- Market-data dependency is declared; live upstream integrations unverified.

**Repository hygiene findings**

- **HIGH — Legacy repository contains personal and recovery artifacts:** Tracked paths include personal email/PDF/document exports, desktop shortcuts, ZIP archives and a recovered SQL dump alongside legacy application source. Treat these as potentially sensitive; their contents were not read by SysCentre.
  - Evidence: [`Fw_ Bewijs van inschrijving.eml`](https://github.com/Daniel550-pixel/FinSight-Global-AI-2/blob/main/Fw_%20Bewijs%20van%20inschrijving.eml), [`OA_AP_D09C Bewijs van inschrijving (Briefpapier).pdf`](https://github.com/Daniel550-pixel/FinSight-Global-AI-2/blob/main/OA_AP_D09C%20Bewijs%20van%20inschrijving%20(Briefpapier).pdf), [`Recovered-feb-25-2025-0947.~vs3CF8.sql`](https://github.com/Daniel550-pixel/FinSight-Global-AI-2/blob/main/Recovered-feb-25-2025-0947.~vs3CF8.sql), [`ChatGPT gesprekken FinSight Global AI OS Platform.odt`](https://github.com/Daniel550-pixel/FinSight-Global-AI-2/blob/main/ChatGPT%20gesprekken%20FinSight%20Global%20AI%20OS%20Platform.odt)
  - Recommended action: Review repository visibility and Git history; remove unrelated artifacts in a separate cleanup commit, add ignore rules, and inspect any SQL/archive files locally for credentials or personal information before retaining them.

**Additional evidence files**

- [`main.py`](https://github.com/Daniel550-pixel/FinSight-Global-AI-2/blob/main/main.py)
- [`streamlit_app.py`](https://github.com/Daniel550-pixel/FinSight-Global-AI-2/blob/main/streamlit_app.py)
- [`requirements.txt`](https://github.com/Daniel550-pixel/FinSight-Global-AI-2/blob/main/requirements.txt)

**Gaps and caveats**

- Legacy lineage versus other FinSight repositories is not confirmed.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### FinSight-Global-AI-4

- **Status:** `source-verified`
- **Repository:** https://github.com/Daniel550-pixel/FinSight-Global-AI-4
- **Default branch:** `main`
- **Inspected commit:** [`a081dd0fa4a33efa6c20cea6416e65a28f7a57cc`](https://github.com/Daniel550-pixel/FinSight-Global-AI-4/commit/a081dd0fa4a33efa6c20cea6416e65a28f7a57cc)
- **Git tree SHA:** `6c60d34de60ad029bdbb36001f4491d3954b83c0`
- **Commit date:** 2025-11-05T08:44:17Z
- **Inventory check date:** 2026-10-11

Minimal Python Streamlit app variant with only two tracked files in the recursive tree: requirements and Streamlit entrypoint.

**Technology stack**

- Python
- Streamlit
- Financial data dependencies declared in requirements

**Application entrypoints**

- [`streamlit_app.py`](https://github.com/Daniel550-pixel/FinSight-Global-AI-4/blob/main/streamlit_app.py)

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| UI / application | Streamlit entrypoint | Single-page dashboard scaffold | [`streamlit_app.py`](https://github.com/Daniel550-pixel/FinSight-Global-AI-4/blob/main/streamlit_app.py) |

**State and data**

- No persistence layer or backend API found in the scanned two-file tree.

**External integrations**

- No external integration verified.

**Additional evidence files**

- [`streamlit_app.py`](https://github.com/Daniel550-pixel/FinSight-Global-AI-4/blob/main/streamlit_app.py)
- [`requirements.txt`](https://github.com/Daniel550-pixel/FinSight-Global-AI-4/blob/main/requirements.txt)

**Gaps and caveats**

- The repo tree is very small and has no README; product purpose beyond the entrypoint is not established.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### FinSight_Global_AI_Dashboard

- **Status:** `source-verified`
- **Repository:** https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard
- **Default branch:** `master`
- **Inspected commit:** [`f1a8aed0429cb9a96be62bfa25fbfd6b700e0c17`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/commit/f1a8aed0429cb9a96be62bfa25fbfd6b700e0c17)
- **Git tree SHA:** `dff0bb48e04396a73180d441e8eb5dcd26332c9d`
- **Commit date:** 2026-09-18T08:06:50Z
- **Inventory check date:** 2026-10-11

Python Streamlit financial workstation. finSight_master.py is a thin import wrapper for finsight_terminal_ui.py, which configures the Streamlit page and dashboard interface; additional tracked modules cover market analysis, sentiment, backtesting, simulation, hedging, broker/auth/alert helpers and operations scripts.

**Technology stack**

- Python
- Streamlit
- Pandas
- NumPy
- Plotly (declared in requirements)
- yfinance (declared in requirements)

**Application entrypoints**

- [`finSight_master.py`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/finSight_master.py)
- [`finsight_terminal_ui.py`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/finsight_terminal_ui.py)

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| Presentation | Streamlit UI configures the FinSight Global page and composes dashboard content. | finSight_master.py delegates to finsight_terminal_ui.py | [`finSight_master.py`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/finSight_master.py), [`finsight_terminal_ui.py`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/finsight_terminal_ui.py), [`requirements.txt`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/requirements.txt) |
| Market and portfolio analytics | Separate modules exist for market engines, sentiment, Monte Carlo, backtesting, hedging, valuation and deep reinforcement learning; exact production wiring is not claimed. | market_engine.py, sentiment_analysis.py, monte_carlo.py, backtest.py, portfolio_hedging.py, deep_rl_agent.py | [`market_engine.py`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/market_engine.py), [`sentiment_analysis.py`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/sentiment_analysis.py), [`monte_carlo.py`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/monte_carlo.py), [`backtest.py`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/backtest.py), [`portfolio_hedging.py`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/portfolio_hedging.py), [`deep_rl_agent.py`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/deep_rl_agent.py) |
| API / user support modules | Broker API, authentication, alert and utility modules are present; external connection and authorization behavior require independent review. | broker_api.py, auth.py, alerts.py, utils.py | [`broker_api.py`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/broker_api.py), [`auth.py`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/auth.py), [`alerts.py`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/alerts.py), [`utils.py`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/utils.py) |
| Operations and packaging | Container/devcontainer configuration and multiple shell upgrade/restore scripts are tracked. | Dockerfile, .devcontainer configuration and maintenance scripts | [`Dockerfile`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/Dockerfile), [`.devcontainer/devcontainer.json`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/.devcontainer/devcontainer.json), [`finsight_full_upgrade.sh`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/finsight_full_upgrade.sh), [`finsight_safe_restore_upgrade.sh`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/finsight_safe_restore_upgrade.sh) |

**State and data**

- No persistent database configuration was confirmed from the inspected manifests and source tree.
- A tracked .env file is present. Its contents were intentionally not read or copied; treat it as a credential-exposure risk until reviewed.

**External integrations**

- requirements.txt declares yfinance; live market-data calls were not tested.
- broker_api.py and auth.py exist, but configured broker/provider endpoints and live connectivity are not verified.

**Repository hygiene findings**

- **HIGH — Tracked .env file:** The current tracked tree contains a .env file. Its contents were not read or copied into SysCentre. If it contains real credentials, they may be exposed to repository readers and Git history.
  - Evidence: [`.env`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/.env)
  - Recommended action: Review the file and repository access immediately; rotate any real credentials, remove the file from future commits, add it to .gitignore, and keep only a redacted .env.example. Historical commits may still contain prior values.

**Additional evidence files**

- [`finSight_master.py`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/finSight_master.py)
- [`finsight_terminal_ui.py`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/finsight_terminal_ui.py)
- [`requirements.txt`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/requirements.txt)
- [`market_engine.py`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/market_engine.py)
- [`backtest.py`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/backtest.py)
- [`broker_api.py`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/broker_api.py)
- [`auth.py`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/auth.py)
- [`Dockerfile`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/Dockerfile)
- [`.env`](https://github.com/Daniel550-pixel/FinSight_Global_AI_Dashboard/blob/master/.env)

**Gaps and caveats**

- The presence of analytics modules does not prove all modules are wired into the Streamlit page.
- requirements.txt uses broad, unpinned dependency declarations.
- The tracked .env path is a high-priority repository hygiene concern; do not display or index its contents.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### AI-mainframe

- **Status:** `source-verified`
- **Repository:** https://github.com/Daniel550-pixel/AI-mainframe
- **Default branch:** `main`
- **Inspected commit:** [`f27ba860005a32ebd5d45c49c6e2aa8b82483252`](https://github.com/Daniel550-pixel/AI-mainframe/commit/f27ba860005a32ebd5d45c49c6e2aa8b82483252)
- **Git tree SHA:** `7485b330520df53c2dce23d29c9bd37329d1518b`
- **Commit date:** 2026-08-25T09:47:26Z
- **Inventory check date:** 2026-10-11

Dependency-free Python capability-registry package; it describes capabilities and delegates all consequential execution/governance to ArchOS rather than acting as a second autonomous runtime.

**Technology stack**

- Python standard library
- Dependency-free package

**Application entrypoints**

- [`src/ai_mainframe/runtime.py`](https://github.com/Daniel550-pixel/AI-mainframe/blob/main/src/ai_mainframe/runtime.py)

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| Capability registry | Dataclass-based catalog of governed capabilities | MainframeRuntime / MainframeCapability | [`src/ai_mainframe/runtime.py`](https://github.com/Daniel550-pixel/AI-mainframe/blob/main/src/ai_mainframe/runtime.py) |
| Integration boundary | ArchOS owns policy, identity, event fabric, world state, and external side effects | Capability description / governed handoff | [`README.md`](https://github.com/Daniel550-pixel/AI-mainframe/blob/main/README.md), [`src/ai_mainframe/runtime.py`](https://github.com/Daniel550-pixel/AI-mainframe/blob/main/src/ai_mainframe/runtime.py) |

**State and data**

- In-memory static capability tuple; no database or side-effect execution implemented.

**External integrations**

- Designed for ArchOS integration; README references ArchOS-Repo integration path.

**Additional evidence files**

- [`README.md`](https://github.com/Daniel550-pixel/AI-mainframe/blob/main/README.md)
- [`src/ai_mainframe/runtime.py`](https://github.com/Daniel550-pixel/AI-mainframe/blob/main/src/ai_mainframe/runtime.py)
- [`src/ai_mainframe/__init__.py`](https://github.com/Daniel550-pixel/AI-mainframe/blob/main/src/ai_mainframe/__init__.py)

**Gaps and caveats**

- Not a standalone web application; no UI or network server is intended.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### AI-OS-Global-Super-App

- **Status:** `documentation-only`
- **Repository:** https://github.com/Daniel550-pixel/AI-OS-Global-Super-App
- **Default branch:** `main`
- **Inspected commit:** [`04a19fa52cb1f5589baa4eaa81dd8c28a4d41802`](https://github.com/Daniel550-pixel/AI-OS-Global-Super-App/commit/04a19fa52cb1f5589baa4eaa81dd8c28a4d41802)
- **Git tree SHA:** `4677376151061a9acd64bcc09df381c5c9248f5a`
- **Commit date:** 2025-12-11T13:27:00Z
- **Inventory check date:** 2026-10-11

README-only AI operating-system / super-app concept with no frontend, backend, dependency manifest, or executable entrypoint in the scanned tree.

**Technology stack**

- No implementation stack confirmed

**Application entrypoints**

- [`README.md`](https://github.com/Daniel550-pixel/AI-OS-Global-Super-App/blob/main/README.md)

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| Documentation | Title/concept README only | Product intent | [`README.md`](https://github.com/Daniel550-pixel/AI-OS-Global-Super-App/blob/main/README.md) |

**State and data**

- No implemented state store.

**External integrations**

- No external integration verified.

**Additional evidence files**

- [`README.md`](https://github.com/Daniel550-pixel/AI-OS-Global-Super-App/blob/main/README.md)

**Gaps and caveats**

- Feature architecture and runtime behavior cannot be verified yet.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### AI-OS-Global-Wealth-Engine

- **Status:** `empty`
- **Repository:** https://github.com/Daniel550-pixel/AI-OS-Global-Wealth-Engine
- **Default branch:** `main`
- **Inspected commit:** None — repository has no Git commit
- **Git tree SHA:** None — repository has no Git tree
- **Commit date:** No commit
- **Inventory check date:** 2026-10-11

GitHub reports an empty repository; there are no tracked sources or manifests from which to derive an application architecture.

**Technology stack**

- No stack confirmed

**Application entrypoints**

- No runnable application entrypoint verified.

**Layers and components**

No application layers can be confirmed from the current source tree.

**State and data**

- No state/persistence layer verified.

**External integrations**

- No external integration verified.

**Gaps and caveats**

- Empty Git repository; no architecture can be claimed.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### AIOS-System

- **Status:** `documentation-only`
- **Repository:** https://github.com/Daniel550-pixel/AIOS-System
- **Default branch:** `main`
- **Inspected commit:** [`135156f9d7bee89002bb0748ee38ac5c37168678`](https://github.com/Daniel550-pixel/AIOS-System/commit/135156f9d7bee89002bb0748ee38ac5c37168678)
- **Git tree SHA:** `def6579b1d895d59731484f2df5313789ea7c49b`
- **Commit date:** 2025-12-30T14:04:04Z
- **Inventory check date:** 2026-10-11

README-only AIOS system concept; no executable product code or dependency manifest exists in the default branch tree.

**Technology stack**

- No implementation stack confirmed

**Application entrypoints**

- [`README.md`](https://github.com/Daniel550-pixel/AIOS-System/blob/main/README.md)

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| Documentation | Concept README | Intended system direction | [`README.md`](https://github.com/Daniel550-pixel/AIOS-System/blob/main/README.md) |

**State and data**

- No implemented persistence layer.

**External integrations**

- No external integration verified.

**Additional evidence files**

- [`README.md`](https://github.com/Daniel550-pixel/AIOS-System/blob/main/README.md)

**Gaps and caveats**

- This is not yet an app architecture backed by runnable source.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### AIOS-Core-Architect.

- **Status:** `source-limited`
- **Repository:** https://github.com/Daniel550-pixel/AIOS-Core-Architect.
- **Default branch:** `main`
- **Inspected commit:** [`4ca3b69e27dca5d1b46f8ed52abce8b411f6eafe`](https://github.com/Daniel550-pixel/AIOS-Core-Architect./commit/4ca3b69e27dca5d1b46f8ed52abce8b411f6eafe)
- **Git tree SHA:** `4fee0b4ffd599bcce511bf1ca5d4ef22c18ab66c`
- **Commit date:** 2026-01-20T14:03:59Z
- **Inventory check date:** 2026-10-11

Small Python/Gradio application that reads JSON configuration, simulates module revenue in a daemon thread, and renders recent logs in a Gradio Blocks UI. The source references configs files that were not present in the scanned tree, and requirements.txt appears to mix dependency lines with non-requirements content.

**Technology stack**

- Python
- Gradio
- JSON configuration
- Threading / datetime standard library

**Application entrypoints**

- [`app.py`](https://github.com/Daniel550-pixel/AIOS-Core-Architect./blob/main/app.py)

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| Configuration | Loads system_config.json and modules.json from configs/ | Config-driven module list | [`app.py`](https://github.com/Daniel550-pixel/AIOS-Core-Architect./blob/main/app.py), [`requirements.txt`](https://github.com/Daniel550-pixel/AIOS-Core-Architect./blob/main/requirements.txt) |
| Simulation loop | In-memory Module objects mutate simulated revenue and append logs | Daemon thread and periodic updates | [`app.py`](https://github.com/Daniel550-pixel/AIOS-Core-Architect./blob/main/app.py) |
| UI | Gradio Blocks textbox/button refreshes logs on request | Manual refresh UI | [`app.py`](https://github.com/Daniel550-pixel/AIOS-Core-Architect./blob/main/app.py) |

**State and data**

- State exists in process memory; no database found.

**External integrations**

- No real revenue system is verified; app's own code is a simulation.

**Additional evidence files**

- [`app.py`](https://github.com/Daniel550-pixel/AIOS-Core-Architect./blob/main/app.py)
- [`requirements.txt`](https://github.com/Daniel550-pixel/AIOS-Core-Architect./blob/main/requirements.txt)

**Gaps and caveats**

- configs/system_config.json and configs/modules.json are referenced by app.py but were not in the scanned tree. Validate dependencies/config before startup.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### Obsidian-AI

- **Status:** `source-verified`
- **Repository:** https://github.com/Daniel550-pixel/Obsidian-AI
- **Default branch:** `main`
- **Inspected commit:** [`2de5c83490209ae441a91ed4aa270a58b3d57bf8`](https://github.com/Daniel550-pixel/Obsidian-AI/commit/2de5c83490209ae441a91ed4aa270a58b3d57bf8)
- **Git tree SHA:** `a58d44e05e98f9372455dce7b7cdf88b2d4e1d3f`
- **Commit date:** 2026-03-25T15:10:50Z
- **Inventory check date:** 2026-10-11

React/TypeScript + Vite AI interface using Firebase Authentication/Firestore for user-scoped chat messages and a Gemini service for generation, grounding, and speech-related features.

**Technology stack**

- React 19
- TypeScript
- Vite
- Firebase Auth / Firestore
- Google GenAI SDK
- Motion / Lucide

**Application entrypoints**

- [`src/main.tsx`](https://github.com/Daniel550-pixel/Obsidian-AI/blob/main/src/main.tsx)
- [`src/App.tsx`](https://github.com/Daniel550-pixel/Obsidian-AI/blob/main/src/App.tsx)
- [`src/services/geminiService.ts`](https://github.com/Daniel550-pixel/Obsidian-AI/blob/main/src/services/geminiService.ts)

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| Client UI | React App with command/chat UI, visuals and business model components | App and feature components | [`src/App.tsx`](https://github.com/Daniel550-pixel/Obsidian-AI/blob/main/src/App.tsx), [`src/components/ICCVisualizer.tsx`](https://github.com/Daniel550-pixel/Obsidian-AI/blob/main/src/components/ICCVisualizer.tsx), [`src/components/BusinessModelCanvas.tsx`](https://github.com/Daniel550-pixel/Obsidian-AI/blob/main/src/components/BusinessModelCanvas.tsx) |
| Identity / user state | Firebase popup sign-in and auth-state handling | Firebase Auth | [`src/firebase.ts`](https://github.com/Daniel550-pixel/Obsidian-AI/blob/main/src/firebase.ts), [`src/App.tsx`](https://github.com/Daniel550-pixel/Obsidian-AI/blob/main/src/App.tsx) |
| Conversation persistence | Firestore collection under a per-user conversation path | Message write and onSnapshot read | [`src/App.tsx`](https://github.com/Daniel550-pixel/Obsidian-AI/blob/main/src/App.tsx), [`src/firebase.ts`](https://github.com/Daniel550-pixel/Obsidian-AI/blob/main/src/firebase.ts) |
| AI service | Gemini generation / grounding / thinking and TTS helpers | Gemini service module | [`src/services/geminiService.ts`](https://github.com/Daniel550-pixel/Obsidian-AI/blob/main/src/services/geminiService.ts) |

**State and data**

- Firestore stores conversation messages using server timestamps; Firebase configuration resides in src/firebase.ts.

**External integrations**

- Firebase Auth, Cloud Firestore, Google GenAI.

**Additional evidence files**

- [`package.json`](https://github.com/Daniel550-pixel/Obsidian-AI/blob/main/package.json)
- [`src/main.tsx`](https://github.com/Daniel550-pixel/Obsidian-AI/blob/main/src/main.tsx)
- [`src/App.tsx`](https://github.com/Daniel550-pixel/Obsidian-AI/blob/main/src/App.tsx)
- [`src/firebase.ts`](https://github.com/Daniel550-pixel/Obsidian-AI/blob/main/src/firebase.ts)
- [`src/services/geminiService.ts`](https://github.com/Daniel550-pixel/Obsidian-AI/blob/main/src/services/geminiService.ts)
- [`src/components/ICCVisualizer.tsx`](https://github.com/Daniel550-pixel/Obsidian-AI/blob/main/src/components/ICCVisualizer.tsx)

**Gaps and caveats**

- The repository's server dependency is declared, but no server.ts was found in the scanned tree; backend hosting model is not confirmed.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### FGSE

- **Status:** `source-verified`
- **Repository:** https://github.com/Daniel550-pixel/FGSE
- **Default branch:** `main`
- **Inspected commit:** [`8abadadb9efaa7a7fe9237d1e37713613447701a`](https://github.com/Daniel550-pixel/FGSE/commit/8abadadb9efaa7a7fe9237d1e37713613447701a)
- **Git tree SHA:** `97ed438ae7f00a1d0dfb35953666d4e1787e5b50`
- **Commit date:** 2026-04-22T17:31:31Z
- **Inventory check date:** 2026-10-11

Full-stack TypeScript finance/trading app: React/Vite frontend, Express server, SQLite-backed trade access, strategy/trader modules, market-data requests and Gemini service logic.

**Technology stack**

- React 19
- TypeScript
- Vite
- Express
- better-sqlite3
- Google GenAI SDK
- Axios

**Application entrypoints**

- [`server.ts`](https://github.com/Daniel550-pixel/FGSE/blob/main/server.ts)
- [`src/main.tsx`](https://github.com/Daniel550-pixel/FGSE/blob/main/src/main.tsx)
- [`src/App.tsx`](https://github.com/Daniel550-pixel/FGSE/blob/main/src/App.tsx)

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| Frontend | React dashboard and visualizations | src tree and main entry | [`src/main.tsx`](https://github.com/Daniel550-pixel/FGSE/blob/main/src/main.tsx), [`src/App.tsx`](https://github.com/Daniel550-pixel/FGSE/blob/main/src/App.tsx) |
| HTTP backend | Express routes for health, GAOS scan, recursive spawn, finance and trading workflows | Server starts Vite and mounts API routes | [`server.ts`](https://github.com/Daniel550-pixel/FGSE/blob/main/server.ts) |
| Strategy / trading domain | Signal generation, trade execution helpers, and portfolio access | Strategy + trader modules | [`server/strategy.ts`](https://github.com/Daniel550-pixel/FGSE/blob/main/server/strategy.ts), [`server/trader.ts`](https://github.com/Daniel550-pixel/FGSE/blob/main/server/trader.ts) |
| Persistence | SQLite initialization and trade reads/writes | DB helper | [`server/db.ts`](https://github.com/Daniel550-pixel/FGSE/blob/main/server/db.ts) |

**State and data**

- SQLite via better-sqlite3 (per dependency and server imports).

**External integrations**

- Google GenAI, Binance market-data endpoint via Axios; actual accounts/real trade execution not independently verified.

**Additional evidence files**

- [`package.json`](https://github.com/Daniel550-pixel/FGSE/blob/main/package.json)
- [`server.ts`](https://github.com/Daniel550-pixel/FGSE/blob/main/server.ts)
- [`server/db.ts`](https://github.com/Daniel550-pixel/FGSE/blob/main/server/db.ts)
- [`server/strategy.ts`](https://github.com/Daniel550-pixel/FGSE/blob/main/server/strategy.ts)
- [`server/trader.ts`](https://github.com/Daniel550-pixel/FGSE/blob/main/server/trader.ts)
- [`src/App.tsx`](https://github.com/Daniel550-pixel/FGSE/blob/main/src/App.tsx)

**Gaps and caveats**

- Source includes demo/mock labels and illustrative thresholds; do not treat labels such as 'deployed' as verified infrastructure state.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### ArchOS-Repo

- **Status:** `source-verified`
- **Repository:** https://github.com/Daniel550-pixel/ArchOS-Repo
- **Default branch:** `main`
- **Inspected commit:** [`eb935d3a1337b469f8c29b8ec01c9200cd8ebd8e`](https://github.com/Daniel550-pixel/ArchOS-Repo/commit/eb935d3a1337b469f8c29b8ec01c9200cd8ebd8e)
- **Git tree SHA:** `21a47d0942f96f85b0d8fe9d78bcc1730db1fba4`
- **Commit date:** 2026-08-28T12:33:39Z
- **Inventory check date:** 2026-10-11

Large multi-layer ArchOS codebase with FastAPI backend, agent orchestration and policy/action gates, world model and simulation APIs, identity/auth, worker scheduling, event fabric, operational services, and React/TypeScript spatial experience UI.

**Technology stack**

- Python
- FastAPI / Pydantic
- React / TypeScript
- Three.js / React Three Fiber (documented)
- MediaPipe gesture/vision integration (documented)
- Docker / GitHub Actions

**Application entrypoints**

- [`backend/app/main.py`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/backend/app/main.py)
- [`frontend entrypoint not fully enumerated in this compact scan`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/frontend%20entrypoint%20not%20fully%20enumerated%20in%20this%20compact%20scan)
- [`src/components/ArchOSSystemUI.tsx (catalog reference)`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/src/components/ArchOSSystemUI.tsx%20(catalog%20reference))

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| API host | FastAPI application with routers for agents, world model, simulation, scenarios, causal graph, integrations, and Claude provider routes | App lifecycle wires workers and service runtimes | [`backend/app/main.py`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/backend/app/main.py), [`backend/app/api/agents.py`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/backend/app/api/agents.py), [`backend/app/api/world_model.py`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/backend/app/api/world_model.py), [`backend/app/api/simulation.py`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/backend/app/api/simulation.py) |
| Agent and governance runtime | JARVIS orchestrator, specialist/swarm runtime, action gate, evidence chains, verification | Agent fabric and policy controls | [`backend/agents/jarvis_orchestrator.py`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/backend/agents/jarvis_orchestrator.py), [`backend/agents/action_gate.py`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/backend/agents/action_gate.py), [`backend/agents/swarm.py`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/backend/agents/swarm.py), [`backend/agents/evidence_chain.py`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/backend/agents/evidence_chain.py) |
| World state / intelligence | World-model, scenario, causal graph, normalization, search and simulation services | Domain services | [`backend/app/services/scenario_orchestrator.py`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/backend/app/services/scenario_orchestrator.py), [`backend/app/services/scenario_verifier.py`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/backend/app/services/scenario_verifier.py), [`backend/app/services/causal_graph.py`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/backend/app/services/causal_graph.py) |
| Identity / operations | Identity middleware, key/session/WebAuthn components, metrics, FinOps, event fabric, schedulers | Middleware and service lifetime | [`backend/app/middleware/identity.py`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/backend/app/middleware/identity.py), [`backend/app/services/event_fabric.py`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/backend/app/services/event_fabric.py), [`backend/app/services/finops_service.py`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/backend/app/services/finops_service.py) |
| Experience layer | React/TypeScript interactive spatial UI; README documents 3D and multimodal inputs | Frontend layer described by project README/catalog | [`README.md`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/README.md), [`src/components/ArchOSSystemUI.tsx`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/src/components/ArchOSSystemUI.tsx) |

**State and data**

- Database abstraction/model files are present; configured persistence depends on environment/settings.

**External integrations**

- Model/provider integrations including Claude and Google AI appear in repository modules/docs; production credentials and operation are not verified.

**Additional evidence files**

- [`README.md`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/README.md)
- [`backend/app/main.py`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/backend/app/main.py)
- [`backend/agents/action_gate.py`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/backend/agents/action_gate.py)
- [`backend/agents/jarvis_orchestrator.py`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/backend/agents/jarvis_orchestrator.py)
- [`backend/agents/swarm.py`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/backend/agents/swarm.py)
- [`backend/app/services/event_fabric.py`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/backend/app/services/event_fabric.py)
- [`backend/app/services/causal_graph.py`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/backend/app/services/causal_graph.py)
- [`src/components/ArchOSSystemUI.tsx`](https://github.com/Daniel550-pixel/ArchOS-Repo/blob/main/src/components/ArchOSSystemUI.tsx)

**Gaps and caveats**

- Architecture combines present modules and documented direction; no claim that every integration or production security control is live.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### archos-3

- **Status:** `source-verified`
- **Repository:** https://github.com/Daniel550-pixel/archos-3
- **Default branch:** `main`
- **Inspected commit:** [`0616406be6678231b29f8c9fc7f2e5f7e7e37fe3`](https://github.com/Daniel550-pixel/archos-3/commit/0616406be6678231b29f8c9fc7f2e5f7e7e37fe3)
- **Git tree SHA:** `82450dd54de067e963d17dc80606332fe455296f`
- **Commit date:** 2026-08-21T14:49:51Z
- **Inventory check date:** 2026-10-11

Separate ARCHOS 3.0 full-stack prototype: FastAPI control plane with REST/WebSocket endpoints and in-memory world entities/events, plus a React/TypeScript client organized around dashboard, map, auth, and component modules.

**Technology stack**

- Python
- FastAPI
- Pydantic
- WebSockets
- Prometheus text metrics
- React / TypeScript client source
- Docker backend

**Application entrypoints**

- [`backend/main.py`](https://github.com/Daniel550-pixel/archos-3/blob/main/backend/main.py)
- [`client/src/App.tsx`](https://github.com/Daniel550-pixel/archos-3/blob/main/client/src/App.tsx)

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| API / control plane | FastAPI endpoints for health, readiness, metrics and control-plane data; WebSocket broadcast manager | HTTP and realtime API | [`backend/main.py`](https://github.com/Daniel550-pixel/archos-3/blob/main/backend/main.py), [`backend/requirements.txt`](https://github.com/Daniel550-pixel/archos-3/blob/main/backend/requirements.txt) |
| World model / event layer | Entity models with provenance tags and in-memory maps/event log | Observed/inferred/predicted/simulated records | [`backend/main.py`](https://github.com/Daniel550-pixel/archos-3/blob/main/backend/main.py), [`client/src/ARCHITECTURE.md`](https://github.com/Daniel550-pixel/archos-3/blob/main/client/src/ARCHITECTURE.md) |
| Client | React app, router, DashboardLayout, map and reusable UI components | Browser experience | [`client/src/App.tsx`](https://github.com/Daniel550-pixel/archos-3/blob/main/client/src/App.tsx), [`client/src/app/router.tsx`](https://github.com/Daniel550-pixel/archos-3/blob/main/client/src/app/router.tsx), [`client/src/components/DashboardLayout.tsx`](https://github.com/Daniel550-pixel/archos-3/blob/main/client/src/components/DashboardLayout.tsx) |

**State and data**

- World entities and event log are explicitly initialized in process memory in backend/main.py; durable database not evidenced by this file.

**External integrations**

- WebSocket clients; source strings refer to upstream telemetry providers (BMS/Open-Meteo) but connected live adapters are not verified.

**Additional evidence files**

- [`backend/main.py`](https://github.com/Daniel550-pixel/archos-3/blob/main/backend/main.py)
- [`backend/requirements.txt`](https://github.com/Daniel550-pixel/archos-3/blob/main/backend/requirements.txt)
- [`client/src/App.tsx`](https://github.com/Daniel550-pixel/archos-3/blob/main/client/src/App.tsx)
- [`client/src/ARCHITECTURE.md`](https://github.com/Daniel550-pixel/archos-3/blob/main/client/src/ARCHITECTURE.md)
- [`client/src/components/DashboardLayout.tsx`](https://github.com/Daniel550-pixel/archos-3/blob/main/client/src/components/DashboardLayout.tsx)

**Gaps and caveats**

- Recursive tree did not show client/package.json at the expected path; client build/package wiring needs a separate check.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### BitMiner-AI

- **Status:** `source-verified`
- **Repository:** https://github.com/Daniel550-pixel/BitMiner-AI
- **Default branch:** `main`
- **Inspected commit:** [`5616d8c8f7a6d32dabed426b1eafdb3c18b83146`](https://github.com/Daniel550-pixel/BitMiner-AI/commit/5616d8c8f7a6d32dabed426b1eafdb3c18b83146)
- **Git tree SHA:** `8900792a8df62e5041fccdf30c57f95b4a05642d`
- **Commit date:** 2026-08-31T17:36:49Z
- **Inventory check date:** 2026-10-11

React/Vite operations UI with an Express TypeScript server and a large domain layer for agentic mining decisions, consensus, memory, temporal/canonical ledgers, economic gates, forecasting, replay, verification and fleet proposals.

**Technology stack**

- React 19
- TypeScript
- Vite
- Express
- Google GenAI SDK (optional via GEMINI_API_KEY)
- esbuild build pipeline

**Application entrypoints**

- [`server.ts`](https://github.com/Daniel550-pixel/BitMiner-AI/blob/main/server.ts)
- [`src/main.tsx`](https://github.com/Daniel550-pixel/BitMiner-AI/blob/main/src/main.tsx)
- [`src/App.tsx`](https://github.com/Daniel550-pixel/BitMiner-AI/blob/main/src/App.tsx)

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| Presentation | Dashboard and feature views for fleets, agent memory, provenance, simulation, verification, white-label reports | React component layer | [`src/App.tsx`](https://github.com/Daniel550-pixel/BitMiner-AI/blob/main/src/App.tsx), [`src/components/DashboardView.tsx`](https://github.com/Daniel550-pixel/BitMiner-AI/blob/main/src/components/DashboardView.tsx), [`src/components/FleetControllerView.tsx`](https://github.com/Daniel550-pixel/BitMiner-AI/blob/main/src/components/FleetControllerView.tsx) |
| HTTP / provider | Express server, request bounds, optional Gemini client, API handlers | Node runtime | [`server.ts`](https://github.com/Daniel550-pixel/BitMiner-AI/blob/main/server.ts) |
| Agent and decision engine | Agent cycles, arbitration, economic gate, execution proposals | Domain services | [`src/server/agenticMiningEngine.ts`](https://github.com/Daniel550-pixel/BitMiner-AI/blob/main/src/server/agenticMiningEngine.ts), [`src/server/agentConsensus.ts`](https://github.com/Daniel550-pixel/BitMiner-AI/blob/main/src/server/agentConsensus.ts), [`src/server/economicDecisionGate.ts`](https://github.com/Daniel550-pixel/BitMiner-AI/blob/main/src/server/economicDecisionGate.ts), [`src/server/executionEngine.ts`](https://github.com/Daniel550-pixel/BitMiner-AI/blob/main/src/server/executionEngine.ts) |
| State integrity | Canonical event store, temporal ledger/state, deterministic replay, provenance and verification certificates | Audit/replay mechanisms | [`src/server/canonicalEventStore.ts`](https://github.com/Daniel550-pixel/BitMiner-AI/blob/main/src/server/canonicalEventStore.ts), [`src/server/temporalLedger.ts`](https://github.com/Daniel550-pixel/BitMiner-AI/blob/main/src/server/temporalLedger.ts), [`src/server/deterministicReplay.ts`](https://github.com/Daniel550-pixel/BitMiner-AI/blob/main/src/server/deterministicReplay.ts), [`src/server/verificationCertificateChain.ts`](https://github.com/Daniel550-pixel/BitMiner-AI/blob/main/src/server/verificationCertificateChain.ts) |

**State and data**

- Canonical and temporal stores are implemented as TypeScript modules; exact persistence backing/config should be verified against each store implementation.

**External integrations**

- Google GenAI; web fetching guarded by scraper allowlist and consensus helpers.

**Additional evidence files**

- [`package.json`](https://github.com/Daniel550-pixel/BitMiner-AI/blob/main/package.json)
- [`server.ts`](https://github.com/Daniel550-pixel/BitMiner-AI/blob/main/server.ts)
- [`src/App.tsx`](https://github.com/Daniel550-pixel/BitMiner-AI/blob/main/src/App.tsx)
- [`src/server/agenticMiningEngine.ts`](https://github.com/Daniel550-pixel/BitMiner-AI/blob/main/src/server/agenticMiningEngine.ts)
- [`src/server/canonicalEventStore.ts`](https://github.com/Daniel550-pixel/BitMiner-AI/blob/main/src/server/canonicalEventStore.ts)
- [`src/server/executionEngine.ts`](https://github.com/Daniel550-pixel/BitMiner-AI/blob/main/src/server/executionEngine.ts)
- [`src/server/verificationHarness.ts`](https://github.com/Daniel550-pixel/BitMiner-AI/blob/main/src/server/verificationHarness.ts)

**Gaps and caveats**

- Module names evidence intended controls; do not assume the complete mining, economic, or fleet pipeline is live in production.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### NetworkLab

- **Status:** `source-verified`
- **Repository:** https://github.com/Daniel550-pixel/NetworkLab
- **Default branch:** `main`
- **Inspected commit:** [`8f0bf60bd63b52bbbe397b5f0fbeb8ebd192284a`](https://github.com/Daniel550-pixel/NetworkLab/commit/8f0bf60bd63b52bbbe397b5f0fbeb8ebd192284a)
- **Git tree SHA:** `4af1b7bc817894f0edd0f4c947749193b2a96bd7`
- **Commit date:** 2026-10-09T08:59:45Z
- **Inventory check date:** 2026-10-11

Local-only infrastructure lab: Python standard-library HTTP server serves HTML/CSS/JavaScript UI and JSON API backed by service modules for network, VM, storage, health, evidence and PowerShell command orchestration.

**Technology stack**

- Python standard library
- HTML / CSS / JavaScript
- PowerShell
- JSON
- VirtualBox host tooling

**Application entrypoints**

- [`app/server.py`](https://github.com/Daniel550-pixel/NetworkLab/blob/main/app/server.py)
- [`web/index.html`](https://github.com/Daniel550-pixel/NetworkLab/blob/main/web/index.html)
- [`web/app.js`](https://github.com/Daniel550-pixel/NetworkLab/blob/main/web/app.js)

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| Web host/API | ThreadingHTTPServer bound by default to 127.0.0.1:8501 and serves static files / JSON routes | No Streamlit dependency required | [`app/server.py`](https://github.com/Daniel550-pixel/NetworkLab/blob/main/app/server.py), [`web/index.html`](https://github.com/Daniel550-pixel/NetworkLab/blob/main/web/index.html), [`web/app.js`](https://github.com/Daniel550-pixel/NetworkLab/blob/main/web/app.js) |
| Services | Network and virtual network, VM topology/runtime, storage/ISO, health/evidence | Service modules | [`app/services/network_service.py`](https://github.com/Daniel550-pixel/NetworkLab/blob/main/app/services/network_service.py), [`app/services/virtualization_service.py`](https://github.com/Daniel550-pixel/NetworkLab/blob/main/app/services/virtualization_service.py), [`app/services/vm_service.py`](https://github.com/Daniel550-pixel/NetworkLab/blob/main/app/services/vm_service.py), [`app/services/storage_service.py`](https://github.com/Daniel550-pixel/NetworkLab/blob/main/app/services/storage_service.py) |
| Host integration | PowerShell subprocess/host inspection layer | Windows host operations and safety checks | [`app/core/powershell.py`](https://github.com/Daniel550-pixel/NetworkLab/blob/main/app/core/powershell.py), [`app/core/config.py`](https://github.com/Daniel550-pixel/NetworkLab/blob/main/app/core/config.py) |

**State and data**

- Configuration and lab state use structured JSON / host and VirtualBox observations; no database requirement in requirements.txt.

**External integrations**

- VirtualBox via host commands and PowerShell; app is intended for localhost only.

**Additional evidence files**

- [`README.md`](https://github.com/Daniel550-pixel/NetworkLab/blob/main/README.md)
- [`app/server.py`](https://github.com/Daniel550-pixel/NetworkLab/blob/main/app/server.py)
- [`app/services/health_service.py`](https://github.com/Daniel550-pixel/NetworkLab/blob/main/app/services/health_service.py)
- [`app/services/network_service.py`](https://github.com/Daniel550-pixel/NetworkLab/blob/main/app/services/network_service.py)
- [`app/services/vm_service.py`](https://github.com/Daniel550-pixel/NetworkLab/blob/main/app/services/vm_service.py)
- [`app/services/storage_service.py`](https://github.com/Daniel550-pixel/NetworkLab/blob/main/app/services/storage_service.py)
- [`web/index.html`](https://github.com/Daniel550-pixel/NetworkLab/blob/main/web/index.html)
- [`web/app.js`](https://github.com/Daniel550-pixel/NetworkLab/blob/main/web/app.js)
- [`requirements.txt`](https://github.com/Daniel550-pixel/NetworkLab/blob/main/requirements.txt)

**Gaps and caveats**

- Documented target topology values are not the same as a live VM/network health check.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### SecureOS

- **Status:** `source-verified`
- **Repository:** https://github.com/Daniel550-pixel/SecureOS
- **Default branch:** `main`
- **Inspected commit:** [`b3afc717d0ba45445e9c0f730a6dda4ec96ffb87`](https://github.com/Daniel550-pixel/SecureOS/commit/b3afc717d0ba45445e9c0f730a6dda4ec96ffb87)
- **Git tree SHA:** `0d5cff5b9938074fd252f0a874a6882447f4979a`
- **Commit date:** 2026-09-04T09:09:06Z
- **Inventory check date:** 2026-10-11

React/Vite security-integrity workstation with an Express backend, deterministic baseline comparison and trust-scoring modules, scenario simulation, telemetry normalization and an event ledger; Gemini is an optional analysis provider.

**Technology stack**

- React 19
- TypeScript
- Vite
- Express
- Google GenAI SDK
- Motion / Lucide
- esbuild server bundling

**Application entrypoints**

- [`server.ts`](https://github.com/Daniel550-pixel/SecureOS/blob/main/server.ts)
- [`src/main.tsx`](https://github.com/Daniel550-pixel/SecureOS/blob/main/src/main.tsx)
- [`src/App.tsx`](https://github.com/Daniel550-pixel/SecureOS/blob/main/src/App.tsx)

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| UI | Security workstation, trust dashboards, telemetry, scenario simulator and topology panels | React components | [`src/App.tsx`](https://github.com/Daniel550-pixel/SecureOS/blob/main/src/App.tsx), [`src/components/IntelligenceWorkstation.tsx`](https://github.com/Daniel550-pixel/SecureOS/blob/main/src/components/IntelligenceWorkstation.tsx), [`src/components/SecurityTopology.tsx`](https://github.com/Daniel550-pixel/SecureOS/blob/main/src/components/SecurityTopology.tsx) |
| API / telemetry | Express parses telemetry and manages scenario state | Server entry | [`server.ts`](https://github.com/Daniel550-pixel/SecureOS/blob/main/server.ts) |
| Deterministic integrity engine | Baseline comparison, normalized telemetry, trust scoring and scenario model | Engine modules | [`src/engine/baseline.ts`](https://github.com/Daniel550-pixel/SecureOS/blob/main/src/engine/baseline.ts), [`src/engine/telemetryNormalizer.ts`](https://github.com/Daniel550-pixel/SecureOS/blob/main/src/engine/telemetryNormalizer.ts), [`src/engine/trustEngine.ts`](https://github.com/Daniel550-pixel/SecureOS/blob/main/src/engine/trustEngine.ts), [`src/engine/scenarios.ts`](https://github.com/Daniel550-pixel/SecureOS/blob/main/src/engine/scenarios.ts) |
| Audit trail | Event ledger appends telemetry/trust/lifecycle records and exposes verification helpers | Ledger module | [`src/engine/eventLedger.ts`](https://github.com/Daniel550-pixel/SecureOS/blob/main/src/engine/eventLedger.ts) |

**State and data**

- Active scenario/system state is currently initialized in process memory; event-ledger persistence characteristics require implementation-level verification.

**External integrations**

- Google GenAI via server-side key when configured.

**Additional evidence files**

- [`package.json`](https://github.com/Daniel550-pixel/SecureOS/blob/main/package.json)
- [`server.ts`](https://github.com/Daniel550-pixel/SecureOS/blob/main/server.ts)
- [`src/App.tsx`](https://github.com/Daniel550-pixel/SecureOS/blob/main/src/App.tsx)
- [`src/engine/baseline.ts`](https://github.com/Daniel550-pixel/SecureOS/blob/main/src/engine/baseline.ts)
- [`src/engine/eventLedger.ts`](https://github.com/Daniel550-pixel/SecureOS/blob/main/src/engine/eventLedger.ts)
- [`src/engine/trustEngine.ts`](https://github.com/Daniel550-pixel/SecureOS/blob/main/src/engine/trustEngine.ts)
- [`src/engine/telemetryNormalizer.ts`](https://github.com/Daniel550-pixel/SecureOS/blob/main/src/engine/telemetryNormalizer.ts)

**Gaps and caveats**

- This architecture records code boundaries; runtime protection of an actual host is not established by this scan.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### AI-Venture-Radar

- **Status:** `source-limited`
- **Repository:** https://github.com/Daniel550-pixel/AI-Venture-Radar
- **Default branch:** `main`
- **Inspected commit:** [`9519620d74164ae2a610bd3f6a75dbb4364f4672`](https://github.com/Daniel550-pixel/AI-Venture-Radar/commit/9519620d74164ae2a610bd3f6a75dbb4364f4672)
- **Git tree SHA:** `721d4fe91a12b37e7717bb81e51bb91d864f89e0`
- **Commit date:** 2026-09-04T13:16:08Z
- **Inventory check date:** 2026-10-11

Python domain-core prototype for AI Venture Radar. Tracked code currently implements dataclass domain models for evidence/signals/opportunities, deterministic weighted opportunity scoring, and deterministic adversarial validation; the README's broader data-ingestion, agents, opportunity graph, API and dashboard are planned rather than present in the current tree.

**Technology stack**

- Python
- Python standard library (dataclasses, datetime, enum, uuid, typing)

**Application entrypoints**

- No runnable application entrypoint verified.

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| Domain model | Typed in-memory records for evidence, signals and opportunities, including polarity/status/confidence metadata. | Evidence, Signal, Opportunity and status enums | [`core/models.py`](https://github.com/Daniel550-pixel/AI-Venture-Radar/blob/main/core/models.py) |
| Scoring | Deterministic weighted opportunity score and evidence-derived confidence calculation. | DEFAULT_WEIGHTS and score_opportunity() | [`core/scoring.py`](https://github.com/Daniel550-pixel/AI-Venture-Radar/blob/main/core/scoring.py), [`core/models.py`](https://github.com/Daniel550-pixel/AI-Venture-Radar/blob/main/core/models.py) |
| Adversarial validation | Deterministic checks for supporting evidence, counter-evidence and required problem/gap descriptions. | validate_opportunity() | [`core/adversarial.py`](https://github.com/Daniel550-pixel/AI-Venture-Radar/blob/main/core/adversarial.py), [`core/models.py`](https://github.com/Daniel550-pixel/AI-Venture-Radar/blob/main/core/models.py) |
| Architecture specification | Documents the intended signal-to-opportunity pipeline, but the described ingestion, agents, graph, storage, API and dashboard are not present in the current tree. | README architecture and proposed repository structure | [`README.md`](https://github.com/Daniel550-pixel/AI-Venture-Radar/blob/main/README.md) |

**State and data**

- Evidence, Signal and Opportunity are in-memory Python dataclasses; no persistence layer is present in the tracked tree.
- No ingestion scheduler, source connector or API endpoint is present in the current tracked tree.

**External integrations**

- No external integration verified.

**Additional evidence files**

- [`README.md`](https://github.com/Daniel550-pixel/AI-Venture-Radar/blob/main/README.md)
- [`core/__init__.py`](https://github.com/Daniel550-pixel/AI-Venture-Radar/blob/main/core/__init__.py)
- [`core/models.py`](https://github.com/Daniel550-pixel/AI-Venture-Radar/blob/main/core/models.py)
- [`core/scoring.py`](https://github.com/Daniel550-pixel/AI-Venture-Radar/blob/main/core/scoring.py)
- [`core/adversarial.py`](https://github.com/Daniel550-pixel/AI-Venture-Radar/blob/main/core/adversarial.py)

**Gaps and caveats**

- README explicitly identifies the repository as Phase 0 / architecture initialized.
- No runnable service, web UI, external data adapters, persistence layer or tests were found in the current tracked tree.
- Opportunity scores and validation are deterministic domain primitives, not evidence that market data has been collected or a venture has been validated.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### The-Factory

- **Status:** `source-verified`
- **Repository:** https://github.com/Daniel550-pixel/The-Factory
- **Default branch:** `main`
- **Inspected commit:** [`4420c7c9853d1621ccb3c66abaeeffb6ba39e4b5`](https://github.com/Daniel550-pixel/The-Factory/commit/4420c7c9853d1621ccb3c66abaeeffb6ba39e4b5)
- **Git tree SHA:** `85e1de414844ae213a4c0490111982a96cb8fe87`
- **Commit date:** 2026-09-05T06:27:49Z
- **Inventory check date:** 2026-10-11

Python 3.11+ alpha package implementing reusable system primitives for governed proposals and execution, agent/provider abstractions, events and provenance, context/memory, recovery, scheduling, simulation, observability, tenancy and storage. It is an importable/package-level runtime, not a verified deployed HTTP application; the README still describes kernel extraction and architecture lock as in progress.

**Technology stack**

- Python >=3.11
- setuptools package
- pytest
- Ruff / mypy configuration

**Application entrypoints**

- [`factory/__main__.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/__main__.py)
- [`factory/api.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/api.py)

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| Public package and operation dispatch | Package entry surface and in-process operation handler registry; factory/api.py is not an HTTP server. | factory/__init__.py, factory/__main__.py, APIRequest / APIResponse / FactoryAPI | [`factory/__init__.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/__init__.py), [`factory/__main__.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/__main__.py), [`factory/api.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/api.py) |
| Governance and execution kernel | Explicit proposal/decision boundary; a proposal is only executed when the supplied policy decision is ALLOW. | PolicyDecision, Proposal, PolicyGate, ExecutionBoundary and security adapters | [`factory/kernel/policy.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/kernel/policy.py), [`factory/kernel/execution.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/kernel/execution.py), [`factory/kernel/security.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/kernel/security.py), [`factory/kernel/adapters.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/kernel/adapters.py) |
| State, evidence and recovery primitives | In-memory hash-chained reference event ledger plus provenance, context/memory and recovery abstractions; durability depends on selected adapters. | Events, context, memory, provenance, recovery and observability modules | [`factory/kernel/events.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/kernel/events.py), [`factory/kernel/context.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/kernel/context.py), [`factory/kernel/memory.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/kernel/memory.py), [`factory/kernel/provenance.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/kernel/provenance.py), [`factory/kernel/recovery.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/kernel/recovery.py), [`factory/kernel/observability.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/kernel/observability.py) |
| Agent/runtime and coordination | Agent/provider contracts, scheduling, simulation, queue and worker modules provide reusable runtime components. | Agents, providers, scheduler, simulation, queue, workers | [`factory/kernel/agents.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/kernel/agents.py), [`factory/kernel/providers.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/kernel/providers.py), [`factory/kernel/scheduler.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/kernel/scheduler.py), [`factory/kernel/simulation.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/kernel/simulation.py), [`factory/queue.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/queue.py), [`factory/workers.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/workers.py) |
| Storage, tenancy and product boundaries | Supporting storage/PostgreSQL/tenancy modules and thin product packages separate common primitives from domain projects. | Storage and product package boundaries | [`factory/storage.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/storage.py), [`factory/postgres.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/postgres.py), [`factory/tenancy.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/tenancy.py), [`products/README.md`](https://github.com/Daniel550-pixel/The-Factory/blob/main/products/README.md), [`products/archos/__init__.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/products/archos/__init__.py), [`products/bitminer/__init__.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/products/bitminer/__init__.py), [`products/secureos/__init__.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/products/secureos/__init__.py), [`products/venture_radar/__init__.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/products/venture_radar/__init__.py) |
| Quality controls | Tests and static tooling are configured for the package and integration contracts. | pytest tests; Ruff and mypy project configuration | [`tests/test_kernel.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/tests/test_kernel.py), [`tests/test_integrations.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/tests/test_integrations.py), [`pyproject.toml`](https://github.com/Daniel550-pixel/The-Factory/blob/main/pyproject.toml) |

**State and data**

- factory/kernel/events.py documents EventLedger as an in-memory reference implementation; events are hash-chained within the process and are not durable by themselves.
- PostgreSQL/storage modules exist, but an active database connection or production storage configuration is not verified by tree inspection.
- Tenancy and product module boundaries are implemented as source packages; no deployment topology is configured in the repository itself.

**External integrations**

- PostgreSQL integration module exists; live database connectivity was not tested.
- Product packages reference ArchOS, BitMiner, SecureOS and Venture Radar domains; no cross-repository runtime coupling is assumed.

**Additional evidence files**

- [`README.md`](https://github.com/Daniel550-pixel/The-Factory/blob/main/README.md)
- [`pyproject.toml`](https://github.com/Daniel550-pixel/The-Factory/blob/main/pyproject.toml)
- [`factory/__main__.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/__main__.py)
- [`factory/api.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/api.py)
- [`factory/kernel/policy.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/kernel/policy.py)
- [`factory/kernel/execution.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/kernel/execution.py)
- [`factory/kernel/events.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/kernel/events.py)
- [`factory/kernel/agents.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/kernel/agents.py)
- [`factory/storage.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/storage.py)
- [`factory/postgres.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/postgres.py)
- [`factory/tenancy.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/factory/tenancy.py)
- [`tests/test_kernel.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/tests/test_kernel.py)
- [`tests/test_integrations.py`](https://github.com/Daniel550-pixel/The-Factory/blob/main/tests/test_integrations.py)

**Gaps and caveats**

- README labels the architecture audit/extraction and kernel architecture lock as in progress.
- This package contains implemented primitives, but this inventory does not claim their integration into a production orchestrator or successful runtime test execution.
- The default event ledger is in-memory; do not treat it as durable audit storage.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### The-Factory-2.0

- **Status:** `source-verified`
- **Repository:** https://github.com/Daniel550-pixel/The-Factory-2.0
- **Default branch:** `main`
- **Inspected commit:** [`087f09265c2581e3910f5cb6f3d04e4c15c8d2a0`](https://github.com/Daniel550-pixel/The-Factory-2.0/commit/087f09265c2581e3910f5cb6f3d04e4c15c8d2a0)
- **Git tree SHA:** `47bafd30ddc060d945d5fd61de959a20f451d677`
- **Commit date:** 2026-09-11T08:58:18Z
- **Inventory check date:** 2026-10-11

React/Vite control plane with TypeScript/Express server and explicit kernel modules for policy/security, agent runtime, execution brokerage/lifecycle, durable event ledger, evidence/provenance, replay/recovery, memory and knowledge adapters.

**Technology stack**

- React 19
- TypeScript
- Vite
- Express
- Google GenAI SDK
- Vitest
- Docker

**Application entrypoints**

- [`server-entry.ts`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/server-entry.ts)
- [`server.ts`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/server.ts)
- [`src/main.tsx`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/src/main.tsx)
- [`src/App.tsx`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/src/App.tsx)

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| UI / control plane | Operational views for agents, approvals, arbitration, execution, ledger, provenance, memory, policy, replay, security and settings | React view/component layer | [`src/App.tsx`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/src/App.tsx), [`src/views/ApprovalsView.tsx`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/src/views/ApprovalsView.tsx), [`src/views/EventLedgerView.tsx`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/src/views/EventLedgerView.tsx), [`src/views/PolicyGateView.tsx`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/src/views/PolicyGateView.tsx) |
| HTTP / API | Express server with knowledge, Ox Alpha and runtime routes | Node entrypoints | [`server.ts`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/server.ts), [`server-entry.ts`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/server-entry.ts) |
| Kernel / execution | Policy/security logic, agent runtime, execution broker and lifecycle / receipts | Governed command path | [`server/kernel.ts`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/server/kernel.ts), [`server/security.ts`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/server/security.ts), [`server/execution-broker.ts`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/server/execution-broker.ts), [`server/execution-lifecycle.test.ts`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/server/execution-lifecycle.test.ts) |
| Evidence / durable state | Durable ledger, execution replay store, event/provenance and knowledge adapters | Persistence and recovery modules | [`server/durable-ledger.ts`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/server/durable-ledger.ts), [`server/execution-replay-store.ts`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/server/execution-replay-store.ts), [`server/execution-receipt.ts`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/server/execution-receipt.ts), [`server/knowledge-adapters.ts`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/server/knowledge-adapters.ts) |

**State and data**

- Durable ledger/replay adapters are present; their operational guarantees depend on backing implementation/config.

**External integrations**

- Google GenAI optional provider; knowledge adapters have own route and transaction modules.

**Additional evidence files**

- [`README.md`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/README.md)
- [`package.json`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/package.json)
- [`server-entry.ts`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/server-entry.ts)
- [`server.ts`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/server.ts)
- [`server/kernel.ts`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/server/kernel.ts)
- [`server/security.ts`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/server/security.ts)
- [`server/execution-broker.ts`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/server/execution-broker.ts)
- [`server/durable-ledger.ts`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/server/durable-ledger.ts)
- [`server/execution-replay-store.ts`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/server/execution-replay-store.ts)
- [`src/App.tsx`](https://github.com/Daniel550-pixel/The-Factory-2.0/blob/main/src/App.tsx)

**Gaps and caveats**

- Repository README explicitly cautions that production security boundaries are not yet complete.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### The-House-Of-Coding

- **Status:** `source-verified`
- **Repository:** https://github.com/Daniel550-pixel/The-House-Of-Coding
- **Default branch:** `main`
- **Inspected commit:** [`7d3bc97168ceba585c51f61f78b72ccc2166c962`](https://github.com/Daniel550-pixel/The-House-Of-Coding/commit/7d3bc97168ceba585c51f61f78b72ccc2166c962)
- **Git tree SHA:** `208399f204975791bb79530754f7459f07ce1795`
- **Commit date:** 2026-09-12T21:29:14Z
- **Inventory check date:** 2026-10-11

npm-workspaces monorepo: Next.js/React web application and a separate Express 5 TypeScript API, with routes for code, execution, review, language discovery, search, sessions and agents; OpenAI-backed API is declared.

**Technology stack**

- Node.js / TypeScript
- npm workspaces
- Next.js 16 / React 19
- Express 5
- OpenAI SDK
- Zod

**Application entrypoints**

- [`apps/web/src/app/page.tsx`](https://github.com/Daniel550-pixel/The-House-Of-Coding/blob/main/apps/web/src/app/page.tsx)
- [`apps/api/src/server.ts`](https://github.com/Daniel550-pixel/The-House-Of-Coding/blob/main/apps/api/src/server.ts)

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| Web experience | Next.js App Router pages/components, agent workspace and route handlers | Browser app | [`apps/web/package.json`](https://github.com/Daniel550-pixel/The-House-Of-Coding/blob/main/apps/web/package.json), [`apps/web/src/app/page.tsx`](https://github.com/Daniel550-pixel/The-House-Of-Coding/blob/main/apps/web/src/app/page.tsx), [`apps/web/src/app/agent-workspace/page.tsx`](https://github.com/Daniel550-pixel/The-House-Of-Coding/blob/main/apps/web/src/app/agent-workspace/page.tsx) |
| API service | Express server with modular route and service files | Code, execute, review, search, session and agent routes | [`apps/api/src/server.ts`](https://github.com/Daniel550-pixel/The-House-Of-Coding/blob/main/apps/api/src/server.ts), [`apps/api/src/routes/code.ts`](https://github.com/Daniel550-pixel/The-House-Of-Coding/blob/main/apps/api/src/routes/code.ts), [`apps/api/src/routes/execute.ts`](https://github.com/Daniel550-pixel/The-House-Of-Coding/blob/main/apps/api/src/routes/execute.ts), [`apps/api/src/routes/review.ts`](https://github.com/Daniel550-pixel/The-House-Of-Coding/blob/main/apps/api/src/routes/review.ts) |
| Agent/session services | Session manager and house services with schema validation | Backend domain services | [`apps/api/src/services/agent-sessions.ts`](https://github.com/Daniel550-pixel/The-House-Of-Coding/blob/main/apps/api/src/services/agent-sessions.ts), [`apps/api/src/services/house.ts`](https://github.com/Daniel550-pixel/The-House-Of-Coding/blob/main/apps/api/src/services/house.ts) |

**State and data**

- No datastore confirmed from checked package manifests; source-level storage behavior should be verified.

**External integrations**

- OpenAI SDK declared in API dependencies; live provider credentials/runtime unverified.

**Additional evidence files**

- [`package.json`](https://github.com/Daniel550-pixel/The-House-Of-Coding/blob/main/package.json)
- [`apps/web/package.json`](https://github.com/Daniel550-pixel/The-House-Of-Coding/blob/main/apps/web/package.json)
- [`apps/api/package.json`](https://github.com/Daniel550-pixel/The-House-Of-Coding/blob/main/apps/api/package.json)
- [`apps/api/src/server.ts`](https://github.com/Daniel550-pixel/The-House-Of-Coding/blob/main/apps/api/src/server.ts)
- [`apps/api/src/routes/execute.ts`](https://github.com/Daniel550-pixel/The-House-Of-Coding/blob/main/apps/api/src/routes/execute.ts)
- [`apps/api/src/services/agent-sessions.ts`](https://github.com/Daniel550-pixel/The-House-Of-Coding/blob/main/apps/api/src/services/agent-sessions.ts)

**Gaps and caveats**

- Build/deployment success is not verified from tree inspection alone.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### Localhost-webapp

- **Status:** `source-limited`
- **Repository:** https://github.com/Daniel550-pixel/Localhost-webapp
- **Default branch:** `main`
- **Inspected commit:** [`24aa5206d971ccfc5e1ce6b84459d16ac74ecf0e`](https://github.com/Daniel550-pixel/Localhost-webapp/commit/24aa5206d971ccfc5e1ce6b84459d16ac74ecf0e)
- **Git tree SHA:** `9442b5ad12ef8b61b35a2066b4488b372967d3c9`
- **Commit date:** 2026-09-20T10:03:12Z
- **Inventory check date:** 2026-10-11

Next.js App Router scaffold. The inspected page is the stock Next starter template; no actual product workflow or backend API was visible in the scanned source.

**Technology stack**

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS

**Application entrypoints**

- [`src/app/page.tsx`](https://github.com/Daniel550-pixel/Localhost-webapp/blob/main/src/app/page.tsx)
- [`src/app/layout.tsx`](https://github.com/Daniel550-pixel/Localhost-webapp/blob/main/src/app/layout.tsx)

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| Web shell | Next.js App Router page/layout and static assets | Starter page | [`src/app/page.tsx`](https://github.com/Daniel550-pixel/Localhost-webapp/blob/main/src/app/page.tsx), [`src/app/layout.tsx`](https://github.com/Daniel550-pixel/Localhost-webapp/blob/main/src/app/layout.tsx), [`package.json`](https://github.com/Daniel550-pixel/Localhost-webapp/blob/main/package.json) |

**State and data**

- No persistence/API layer found in the scanned entrypoint and tracked key paths.

**External integrations**

- No external integration verified.

**Additional evidence files**

- [`package.json`](https://github.com/Daniel550-pixel/Localhost-webapp/blob/main/package.json)
- [`src/app/page.tsx`](https://github.com/Daniel550-pixel/Localhost-webapp/blob/main/src/app/page.tsx)
- [`src/app/layout.tsx`](https://github.com/Daniel550-pixel/Localhost-webapp/blob/main/src/app/layout.tsx)

**Gaps and caveats**

- Currently a starter scaffold rather than a verified functional product.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### Business-OS

- **Status:** `source-verified`
- **Repository:** https://github.com/Daniel550-pixel/Business-OS
- **Default branch:** `main`
- **Inspected commit:** [`f2e32c34f743080f1b905cad424d6900b83ddbbc`](https://github.com/Daniel550-pixel/Business-OS/commit/f2e32c34f743080f1b905cad424d6900b83ddbbc)
- **Git tree SHA:** `d1e587f1f5e7d9e94b86961367e03677b4433d79`
- **Commit date:** 2026-09-29T18:47:50Z
- **Inventory check date:** 2026-10-11

Rich React/Vite workspace with Express bootstrap/server, Gemini-driven prompt/runtime services, action execution boundary and multiple business/security/visualization panels including Three.js-based world and flow views.

**Technology stack**

- React 19
- TypeScript
- Vite
- Express
- Google GenAI SDK
- Three.js
- Motion

**Application entrypoints**

- [`server/bootstrap.ts`](https://github.com/Daniel550-pixel/Business-OS/blob/main/server/bootstrap.ts)
- [`server.ts`](https://github.com/Daniel550-pixel/Business-OS/blob/main/server.ts)
- [`src/main.tsx`](https://github.com/Daniel550-pixel/Business-OS/blob/main/src/main.tsx)
- [`src/App.tsx`](https://github.com/Daniel550-pixel/Business-OS/blob/main/src/App.tsx)

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| Web experience | Executive cockpit, finance, sales, operations, agents, missions and spatial world views | React component modules | [`src/App.tsx`](https://github.com/Daniel550-pixel/Business-OS/blob/main/src/App.tsx), [`src/components/ExecutiveCockpit.tsx`](https://github.com/Daniel550-pixel/Business-OS/blob/main/src/components/ExecutiveCockpit.tsx), [`src/components/BusinessWorld.tsx`](https://github.com/Daniel550-pixel/Business-OS/blob/main/src/components/BusinessWorld.tsx), [`src/components/LivingSystemFlow3D.tsx`](https://github.com/Daniel550-pixel/Business-OS/blob/main/src/components/LivingSystemFlow3D.tsx) |
| Request and prompt runtime | Bootstrap increases Express JSON body limit before importing server; server prompt/response runtimes process requests | Server boundary | [`server/bootstrap.ts`](https://github.com/Daniel550-pixel/Business-OS/blob/main/server/bootstrap.ts), [`server/promptRuntime.ts`](https://github.com/Daniel550-pixel/Business-OS/blob/main/server/promptRuntime.ts), [`server/responseRuntime.ts`](https://github.com/Daniel550-pixel/Business-OS/blob/main/server/responseRuntime.ts) |
| Action and security layer | Action runtime, security kernel, security incidents/events/provenance | Gated server operations | [`server/actionRuntime.ts`](https://github.com/Daniel550-pixel/Business-OS/blob/main/server/actionRuntime.ts), [`server/security/securityKernel.ts`](https://github.com/Daniel550-pixel/Business-OS/blob/main/server/security/securityKernel.ts), [`server/security/securityEvents.ts`](https://github.com/Daniel550-pixel/Business-OS/blob/main/server/security/securityEvents.ts), [`server/security/provenance.ts`](https://github.com/Daniel550-pixel/Business-OS/blob/main/server/security/provenance.ts) |

**State and data**

- Persistent store not confirmed from checked manifest/files.

**External integrations**

- Google GenAI; optional provider behavior depends on local server environment/config.

**Repository hygiene findings**

- **MEDIUM — Runtime security-event log is tracked:** The repository tree contains a runtime security event log under .business-os-data. Its contents were not inspected or copied; logs can contain operational identifiers or sensitive event details.
  - Evidence: [`.business-os-data/security-events.jsonl`](https://github.com/Daniel550-pixel/Business-OS/blob/main/.business-os-data/security-events.jsonl)
  - Recommended action: Confirm the file is a safe synthetic fixture; otherwise move runtime logs outside version control, ignore the directory, and retain only a sanitized sample or schema.

**Additional evidence files**

- [`package.json`](https://github.com/Daniel550-pixel/Business-OS/blob/main/package.json)
- [`server/bootstrap.ts`](https://github.com/Daniel550-pixel/Business-OS/blob/main/server/bootstrap.ts)
- [`server.ts`](https://github.com/Daniel550-pixel/Business-OS/blob/main/server.ts)
- [`server/promptRuntime.ts`](https://github.com/Daniel550-pixel/Business-OS/blob/main/server/promptRuntime.ts)
- [`server/actionRuntime.ts`](https://github.com/Daniel550-pixel/Business-OS/blob/main/server/actionRuntime.ts)
- [`server/security/securityKernel.ts`](https://github.com/Daniel550-pixel/Business-OS/blob/main/server/security/securityKernel.ts)
- [`src/App.tsx`](https://github.com/Daniel550-pixel/Business-OS/blob/main/src/App.tsx)

**Gaps and caveats**

- A rich UI is not evidence that backend actions are deployed or safe in a production environment.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### OneDrive-Cleanup-Controller

- **Status:** `source-verified`
- **Repository:** https://github.com/Daniel550-pixel/OneDrive-Cleanup-Controller
- **Default branch:** `main`
- **Inspected commit:** [`fed42c719b8fe42e7dca5f687720bd3ed52bcdbd`](https://github.com/Daniel550-pixel/OneDrive-Cleanup-Controller/commit/fed42c719b8fe42e7dca5f687720bd3ed52bcdbd)
- **Git tree SHA:** `cca1198329886280158c4826b3d1dc63b814abd7`
- **Commit date:** 2026-09-20T12:48:57Z
- **Inventory check date:** 2026-10-11

PowerShell CLI/controller for inspecting OneDrive storage, freeing local disk space, safely quarantining/deleting synced files, restoring quarantined files and writing local audit logs. It has no web UI.

**Technology stack**

- Windows PowerShell
- PowerShell scripts
- JSON configuration

**Application entrypoints**

- [`scripts/Initialize.ps1`](https://github.com/Daniel550-pixel/OneDrive-Cleanup-Controller/blob/main/scripts/Initialize.ps1)
- [`scripts/Status.ps1`](https://github.com/Daniel550-pixel/OneDrive-Cleanup-Controller/blob/main/scripts/Status.ps1)
- [`scripts/Scan.ps1`](https://github.com/Daniel550-pixel/OneDrive-Cleanup-Controller/blob/main/scripts/Scan.ps1)
- [`scripts/FreeUpSpace.ps1`](https://github.com/Daniel550-pixel/OneDrive-Cleanup-Controller/blob/main/scripts/FreeUpSpace.ps1)
- [`scripts/Cleanup.ps1`](https://github.com/Daniel550-pixel/OneDrive-Cleanup-Controller/blob/main/scripts/Cleanup.ps1)
- [`scripts/Restore.ps1 (README names)`](https://github.com/Daniel550-pixel/OneDrive-Cleanup-Controller/blob/main/scripts/Restore.ps1%20(README%20names))

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| Command-line operations | Task-specific PowerShell scripts call shared safety/util functions | Initialize/status/scan/free-space/cleanup/restore | [`README.md`](https://github.com/Daniel550-pixel/OneDrive-Cleanup-Controller/blob/main/README.md) |
| Safety / policy | OneDrive-root confinement, quarantine-by-default, explicit permanent deletion flag | Safety rules documented in README | [`README.md`](https://github.com/Daniel550-pixel/OneDrive-Cleanup-Controller/blob/main/README.md) |
| Configuration and audit | Config template and local ignored configuration; local audit logging | Local-only runtime data | [`README.md`](https://github.com/Daniel550-pixel/OneDrive-Cleanup-Controller/blob/main/README.md) |

**State and data**

- Local config file and audit log; personal OneDrive file contents intentionally excluded from the repository.

**External integrations**

- Windows OneDrive client / local filesystem; destructive sync deletion can propagate to cloud and devices.

**Additional evidence files**

- [`README.md`](https://github.com/Daniel550-pixel/OneDrive-Cleanup-Controller/blob/main/README.md)

**Gaps and caveats**

- Architecture is inferred primarily from README; source scripts should be inspected to verify exact enforcement.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### ExperienceEngine

- **Status:** `source-verified`
- **Repository:** https://github.com/Daniel550-pixel/ExperienceEngine
- **Default branch:** `main`
- **Inspected commit:** [`b89acf7c56b6d3ccc2427c99959fef545f056f9a`](https://github.com/Daniel550-pixel/ExperienceEngine/commit/b89acf7c56b6d3ccc2427c99959fef545f056f9a)
- **Git tree SHA:** `f43ae217a29ac82bc1a92734c30dd765f1f99226`
- **Commit date:** 2026-10-01T19:18:42Z
- **Inventory check date:** 2026-10-11

React/Vite split-screen creation/code workspace served through an Express TypeScript process; code generation uses Google GenAI, a shared language library, prompt normalization/chunking and a code cache.

**Technology stack**

- React 19
- TypeScript
- Vite
- Express
- Google GenAI SDK
- Motion

**Application entrypoints**

- [`server.ts`](https://github.com/Daniel550-pixel/ExperienceEngine/blob/main/server.ts)
- [`src/main.tsx`](https://github.com/Daniel550-pixel/ExperienceEngine/blob/main/src/main.tsx)
- [`src/App.tsx`](https://github.com/Daniel550-pixel/ExperienceEngine/blob/main/src/App.tsx)

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| Web editor | Intention and creation panels, status bar, language presets and simulations | React UI | [`src/App.tsx`](https://github.com/Daniel550-pixel/ExperienceEngine/blob/main/src/App.tsx), [`src/components/IntentionPanel.tsx`](https://github.com/Daniel550-pixel/ExperienceEngine/blob/main/src/components/IntentionPanel.tsx), [`src/components/CreationPanel.tsx`](https://github.com/Daniel550-pixel/ExperienceEngine/blob/main/src/components/CreationPanel.tsx), [`src/utils/projectGenerator.ts`](https://github.com/Daniel550-pixel/ExperienceEngine/blob/main/src/utils/projectGenerator.ts) |
| AI generation service | Server-side Gemini client, prompt validation/normalization, large prompt chunking and code cache | Express server | [`server.ts`](https://github.com/Daniel550-pixel/ExperienceEngine/blob/main/server.ts), [`src/data/codeLanguageLibrary.ts`](https://github.com/Daniel550-pixel/ExperienceEngine/blob/main/src/data/codeLanguageLibrary.ts) |
| Client state / presets | Preset projects, code language definitions and local storage helpers | Browser state utilities | [`src/data/presetProjects.ts`](https://github.com/Daniel550-pixel/ExperienceEngine/blob/main/src/data/presetProjects.ts), [`src/utils/storage.ts`](https://github.com/Daniel550-pixel/ExperienceEngine/blob/main/src/utils/storage.ts) |

**State and data**

- Browser local storage helper exists; server code cache is in-memory. Durable server-side project storage was not confirmed.

**External integrations**

- Google GenAI API key is read from server environment; external generation requires a valid key.

**Additional evidence files**

- [`package.json`](https://github.com/Daniel550-pixel/ExperienceEngine/blob/main/package.json)
- [`server.ts`](https://github.com/Daniel550-pixel/ExperienceEngine/blob/main/server.ts)
- [`src/App.tsx`](https://github.com/Daniel550-pixel/ExperienceEngine/blob/main/src/App.tsx)
- [`src/components/CreationPanel.tsx`](https://github.com/Daniel550-pixel/ExperienceEngine/blob/main/src/components/CreationPanel.tsx)
- [`src/utils/projectGenerator.ts`](https://github.com/Daniel550-pixel/ExperienceEngine/blob/main/src/utils/projectGenerator.ts)
- [`src/utils/storage.ts`](https://github.com/Daniel550-pixel/ExperienceEngine/blob/main/src/utils/storage.ts)

**Gaps and caveats**

- Build is declared as Vite bundle and lint/type check; runtime and provider quotas not tested by this architecture scan.

- **Deployment verified:** No
- **Runtime health verified:** No

---

### SysCentre

- **Status:** `source-verified`
- **Repository:** https://github.com/Daniel550-pixel/SysCentre
- **Default branch:** `main`
- **Inspected commit:** [`af949623bb731151414ac07c28ccc3b990a9111c`](https://github.com/Daniel550-pixel/SysCentre/commit/af949623bb731151414ac07c28ccc3b990a9111c)
- **Git tree SHA:** `082e4c915ed5abf14e1bcb1da2fa045d881a33bb`
- **Commit date:** 2026-10-11T13:29:50Z
- **Inventory check date:** 2026-10-11

Local-first React/Vite control plane backed by a Python standard-library HTTP runtime. It keeps project catalog/intake/runtime-adapter records, indexes GitHub trees and text into SQLite, exposes read-only search and records policy-gated commands/audit events.

**Technology stack**

- Python 3.11+ standard library
- React 18
- TypeScript
- Vite
- SQLite
- GitHub REST API

**Application entrypoints**

- [`runtime/server.py`](https://github.com/Daniel550-pixel/SysCentre/blob/main/runtime/server.py)
- [`webapp/src/main.tsx`](https://github.com/Daniel550-pixel/SysCentre/blob/main/webapp/src/main.tsx)
- [`webapp/src/App.tsx`](https://github.com/Daniel550-pixel/SysCentre/blob/main/webapp/src/App.tsx)
- [`bonus-app/index.html`](https://github.com/Daniel550-pixel/SysCentre/blob/main/bonus-app/index.html)

**Layers and components**

| Layer | Observed responsibility | Components | Evidence |
|---|---|---|---|
| Web control plane | React UI for portfolio, project registry, intake, runtime adapters, command console, policy and event ledger | Vite browser bundle | [`webapp/src/main.tsx`](https://github.com/Daniel550-pixel/SysCentre/blob/main/webapp/src/main.tsx), [`webapp/src/App.tsx`](https://github.com/Daniel550-pixel/SysCentre/blob/main/webapp/src/App.tsx), [`webapp/src/styles.css`](https://github.com/Daniel550-pixel/SysCentre/blob/main/webapp/src/styles.css) |
| Local runtime API | ThreadingHTTPServer on 127.0.0.1:8765 with health/status/events/policy/project/search/ingestion routes | Read-only metadata endpoints and bounded actions | [`runtime/server.py`](https://github.com/Daniel550-pixel/SysCentre/blob/main/runtime/server.py), [`runtime/policy.py`](https://github.com/Daniel550-pixel/SysCentre/blob/main/runtime/policy.py) |
| Repository ingestion | GitHub tree/contents import, path filters, checkpoints and full-text source search | External read-only repository scanning | [`runtime/repository_ingest.py`](https://github.com/Daniel550-pixel/SysCentre/blob/main/runtime/repository_ingest.py) |
| State and audit | SQLite event ledger/index and JSON catalogs/registries | Local persistent state + configuration | [`runtime/server.py`](https://github.com/Daniel550-pixel/SysCentre/blob/main/runtime/server.py), [`runtime/repository_catalog.json`](https://github.com/Daniel550-pixel/SysCentre/blob/main/runtime/repository_catalog.json), [`runtime/project_inventory.json`](https://github.com/Daniel550-pixel/SysCentre/blob/main/runtime/project_inventory.json), [`runtime/project_runtime_registry.json`](https://github.com/Daniel550-pixel/SysCentre/blob/main/runtime/project_runtime_registry.json) |
| Architecture inventory | New JSON snapshot and GET API expose evidence-backed layers per project; no source is executed | This feature | [`runtime/repository_architectures.json`](https://github.com/Daniel550-pixel/SysCentre/blob/main/runtime/repository_architectures.json), [`runtime/server.py`](https://github.com/Daniel550-pixel/SysCentre/blob/main/runtime/server.py) |

**State and data**

- SQLite at ~/.syscentre/syscentre.db; catalogs/registry remain JSON files in the repository.

**External integrations**

- GitHub API reads; no repository code is run. Runtime adapters default to unconfigured pending explicit verification.

**Additional evidence files**

- [`README.md`](https://github.com/Daniel550-pixel/SysCentre/blob/main/README.md)
- [`runtime/server.py`](https://github.com/Daniel550-pixel/SysCentre/blob/main/runtime/server.py)
- [`runtime/repository_ingest.py`](https://github.com/Daniel550-pixel/SysCentre/blob/main/runtime/repository_ingest.py)
- [`runtime/policy.py`](https://github.com/Daniel550-pixel/SysCentre/blob/main/runtime/policy.py)
- [`webapp/src/App.tsx`](https://github.com/Daniel550-pixel/SysCentre/blob/main/webapp/src/App.tsx)
- [`webapp/package.json`](https://github.com/Daniel550-pixel/SysCentre/blob/main/webapp/package.json)
- [`runtime/repository_catalog.json`](https://github.com/Daniel550-pixel/SysCentre/blob/main/runtime/repository_catalog.json)
- [`runtime/project_runtime_registry.json`](https://github.com/Daniel550-pixel/SysCentre/blob/main/runtime/project_runtime_registry.json)

**Gaps and caveats**

- This architecture inventory is a static source-tree snapshot; it does not verify build/deploy/live health for the linked repositories.

- **Deployment verified:** No
- **Runtime health verified:** No

---

## Interpretation rules

- A `source-verified` label means source structure has been inspected; it does not imply complete feature wiring, passing tests, deployment or production readiness.
- A README architecture diagram is treated as a plan unless tracked implementation files support it.
- Empty and documentation-only repositories are not assigned invented stacks, entrypoints or launch commands.
- All records preserve the exact inspected commit/tree identity. Re-scan architecture when a linked repository advances materially.
- Do not paste `.env`, SQL dump, operational log or personal document contents into this register or AI context. Resolve hygiene findings in the source repository and review Git history where exposure is possible.
