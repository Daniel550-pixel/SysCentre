"""Read-only, evidence-backed architecture analysis of already-indexed source files.

This module parses source text and manifests only. It never imports, evaluates, starts, or
executes code from a catalogued project.
"""
from __future__ import annotations

import ast
import json
import re
from collections import Counter
from pathlib import PurePosixPath
from typing import Any
from urllib.parse import urlsplit

import server


MAX_ANALYZED_FILES = 10_000
MAX_ANALYZED_BYTES = 25_000_000
TEXT_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".json", ".toml", ".yaml", ".yml", ".ini", ".cfg", ".md", ".sql", ".html", ".css", ".sh", ".ps1", ".go", ".rs", ".java", ".cs", ".php", ".rb"}


def _unique(values: list[str], limit: int = 100) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))[:limit]


def _matches(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE | re.MULTILINE) for pattern in patterns)


def analyze_indexed_repository(project_id: str) -> dict[str, Any]:
    """Analyze indexed source without executing it; outputs are tied to the indexed commit."""
    from repository_ingest import _db_executescript
    _db_executescript()
    with server._DB_LOCK:
        with server._database() as connection:
            project = connection.execute(
                "SELECT project_id, name, repository_url, default_branch, latest_commit, indexed_at, status FROM projects WHERE project_id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Repository has not been indexed yet. Index it first, then run source analysis.")
            rows = connection.execute(
                "SELECT path, blob_sha, size_bytes, file_kind, content, skip_reason FROM repository_files WHERE project_id = ? ORDER BY path LIMIT ?",
                (project_id, MAX_ANALYZED_FILES + 1),
            ).fetchall()

    if len(rows) > MAX_ANALYZED_FILES:
        raise RuntimeError(f"Indexed source exceeds the analysis limit of {MAX_ANALYZED_FILES} files.")
    files = [dict(row) for row in rows if row["file_kind"] == "text" and row["content"] is not None]
    total_bytes = sum(int(row["size_bytes"] or 0) for row in files)
    if total_bytes > MAX_ANALYZED_BYTES:
        raise RuntimeError(f"Indexed source exceeds the analysis limit of {MAX_ANALYZED_BYTES} bytes.")
    if not files:
        raise ValueError("No indexed text files are available for analysis.")

    paths = {row["path"] for row in files}
    paths_by_stem: dict[str, list[str]] = {}
    for path in sorted(paths):
        candidate = PurePosixPath(path)
        paths_by_stem.setdefault(candidate.stem, []).append(path)

    imports: list[dict[str, str]] = []
    routes: list[dict[str, str]] = []
    outbound_api_calls: list[dict[str, str]] = []
    storage: list[dict[str, str]] = []
    entrypoints: list[dict[str, str]] = []
    manifest_findings: list[dict[str, str]] = []
    modules: list[dict[str, Any]] = []
    framework_counts: Counter[str] = Counter()
    edge_set: set[tuple[str, str]] = set()
    code_files = 0
    total_lines = 0
    total_functions = 0
    total_classes = 0
    total_imports = 0
    parse_failures: list[str] = []

    for row in files:
        path = row["path"]
        text = row["content"] or ""
        suffix = PurePosixPath(path).suffix.lower()
        lines = text.splitlines()
        total_lines += len(lines)
        module_imports: list[str] = []
        if suffix in {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".go", ".rs", ".java", ".cs", ".php", ".rb"}:
            code_files += 1
        if suffix == ".py":
            try:
                tree = ast.parse(text, filename=path)
                functions = [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
                classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                total_functions += len(functions)
                total_classes += len(classes)
                for node in ast.walk(tree):
                    module = None
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            module = alias.name
                            module_imports.append(module)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        module = node.module
                        module_imports.append(module)
                    if module:
                        imports.append({"source": path, "module": module, "kind": "python-import"})
                        top = module.split(".")[0]
                        if top in {"fastapi", "flask", "django", "streamlit", "gradio", "nicegui"}:
                            framework_counts[top] += 1
                if PurePosixPath(path).name in {"main.py", "app.py", "server.py", "manage.py", "__main__.py", "streamlit_app.py"}:
                    entrypoints.append({"path": path, "reason": "Conventional Python application entrypoint filename"})
            except (SyntaxError, ValueError) as exc:
                parse_failures.append(path)
            for match in re.finditer(r"@(?:app|router|api|bp)\.(get|post|put|patch|delete|options|route)\s*\(\s*['\"]([^'\"]+)", text, re.I):
                routes.append({"method": match.group(1).upper(), "path": match.group(2), "source": path})
            for match in re.finditer(r"\b(?:include_router|register_blueprint)\s*\(\s*([A-Za-z_][\w.]*)", text):
                routes.append({"method": "MOUNT", "path": match.group(1), "source": path})
        if suffix in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
            for match in re.finditer(r"\bimport\s+(?:[^;\n]*?\s+from\s+)?['\"]([^'\"]+)['\"]|\brequire\s*\(\s*['\"]([^'\"]+)['\"]\s*\)", text):
                module = match.group(1) or match.group(2)
                imports.append({"source": path, "module": module, "kind": "javascript-import"})
                module_imports.append(module)
                if module in {"react", "react-dom"}:
                    framework_counts["react"] += 1
                elif module in {"express", "fastify", "koa", "hono", "next"}:
                    framework_counts[module] += 1
            for match in re.finditer(r"\b(?:app|router|server)\.(get|post|put|patch|delete|all|use)\s*\(\s*['\"]([^'\"]+)", text, re.I):
                routes.append({"method": match.group(1).upper(), "path": match.group(2), "source": path})
            if PurePosixPath(path).name in {"main.ts", "main.tsx", "index.ts", "index.tsx", "index.js", "index.jsx", "App.tsx", "App.jsx"}:
                entrypoints.append({"path": path, "reason": "Conventional frontend/application entrypoint filename"})

        outbound_pattern = r"""\b(fetch|axios\.(?:get|post|put|patch|delete)|requests\.(?:get|post|put|patch|delete)|httpx\.(?:get|post|put|patch|delete)|urlopen)\s*\(\s*[fFrRuUbB]*['"]([^'"]+)['"]"""
        for match in re.finditer(outbound_pattern, text, re.I):
            outbound_api_calls.append({
                "client": match.group(1),
                "target": match.group(2),
                "source": path,
                "evidence": "Static HTTP-client call target; runtime request is not verified",
            })
        base_url_pattern = r"""\b(?:API_BASE_URL|BASE_URL|API_URL)\s*[:=]\s*['"]([^'"]+)['"]"""
        for match in re.finditer(base_url_pattern, text, re.I):
            outbound_api_calls.append({
                "client": "base-url configuration",
                "target": match.group(1),
                "source": path,
                "evidence": "Static API base URL configuration; runtime request is not verified",
            })

        if PurePosixPath(path).name in {"package.json", "requirements.txt", "pyproject.toml", "Pipfile", "Cargo.toml", "go.mod", "pom.xml", "Gemfile", "composer.json"}:
            manifest_findings.append({"path": path, "kind": PurePosixPath(path).name, "evidence": "Dependency or build manifest is present"})
            lower = text.lower()
            for framework in ("react", "vite", "next", "express", "fastapi", "flask", "django", "streamlit", "sqlalchemy", "prisma", "drizzle", "pydantic", "pytest", "vitest"):
                if re.search(r"\b" + re.escape(framework) + r"\b", lower):
                    framework_counts[framework] += 1
        if _matches(path, (r"(^|/)(\.env|config|settings)", r"database", r"schema\.sql$")) or _matches(text, (r"sqlite3?\.", r"create_engine\s*\(", r"MongoClient", r"mongoose\.", r"PrismaClient", r"localStorage", r"sessionStorage", r"indexedDB", r"redis\.", r"CREATE TABLE", r"\bDATABASE_URL\b")):
            signals = []
            for label, patterns in (
                ("SQLite", (r"sqlite3?\.", r"sqlite://")),
                ("SQLAlchemy / SQL database", (r"create_engine\s*\(", r"SQLAlchemy", r"postgresql://", r"mysql://", r"\bDATABASE_URL\b")),
                ("MongoDB", (r"MongoClient", r"mongoose\.")),
                ("Prisma", (r"PrismaClient", r"prisma/schema\.prisma")),
                ("Browser storage", (r"localStorage", r"sessionStorage", r"indexedDB")),
                ("Redis", (r"redis\.", r"Redis\(")),
                ("SQL schema", (r"CREATE TABLE", r"schema\.sql$")),
            ):
                if _matches(path + "\n" + text, patterns):
                    signals.append(label)
            for signal in signals:
                storage.append({"name": signal, "source": path, "evidence": "Pattern match in indexed source; runtime connectivity is not verified"})
        for module in module_imports:
            candidate = _resolve_local_import(path, module, paths, paths_by_stem)
            if candidate and candidate != path:
                edge_set.add((path, candidate))

        if suffix in {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"} and (module_imports or len(lines) > 0):
            modules.append({
                "path": path, "language": suffix.lstrip("."),
                "lines": len(lines), "imports": len(module_imports),
                "functions_or_classes": len([1 for _ in re.finditer(r"\b(?:def|class|function)\s+[A-Za-z_$][\w$]*|\b(?:const|let)\s+[A-Za-z_$][\w$]*\s*=\s*(?:async\s*)?\([^)]*\)\s*=>", text)]),
                "role": _role_for_path(path, text),
            })
        total_imports += len(module_imports)

    for row in files:
        path = row["path"]
        text = row["content"] or ""
        if PurePosixPath(path).name in {"package.json", "pyproject.toml"}:
            try:
                if path.endswith("package.json"):
                    manifest = json.loads(text)
                    for section in ("dependencies", "devDependencies", "peerDependencies"):
                        for name, version in (manifest.get(section, {}) or {}).items():
                            manifest_findings.append({"path": path, "kind": "dependency", "evidence": f"{name}@{version} ({section})"})
                elif path.endswith("pyproject.toml"):
                    for line in text.splitlines():
                        if re.match(r"\s*[A-Za-z0-9_.-]+\s*=\s*['\"][^'\"]+['\"]", line):
                            manifest_findings.append({"path": path, "kind": "pyproject-setting", "evidence": line.strip()[:180]})
            except (ValueError, TypeError):
                parse_failures.append(path)

    route_keys = set()
    unique_routes = []
    for item in routes:
        key = (item["method"], item["path"], item["source"])
        if key not in route_keys:
            route_keys.add(key)
            unique_routes.append(item)
    route_count = len(unique_routes)
    findings = []
    if not entrypoints:
        findings.append({"severity": "medium", "title": "No conventional entrypoint identified", "detail": "No common Python or JavaScript entrypoint filename was identified; this does not prove the application has no entrypoint."})
    if not routes:
        findings.append({"severity": "info", "title": "No route declarations detected", "detail": "No supported Python/JavaScript route decorator or call pattern was found."})
    if parse_failures:
        findings.append({"severity": "low", "title": "Some source files could not be parsed", "detail": f"{len(set(parse_failures))} files had syntax/manifest parsing errors; other pattern-based findings may still be available."})
    if not storage:
        findings.append({"severity": "info", "title": "No data-store patterns detected", "detail": "No supported database or browser-storage pattern was detected in indexed source."})

    modules.sort(key=lambda item: (-item["lines"], item["path"]))
    local_edges = [{"from": source, "to": target, "kind": "local-import"} for source, target in sorted(edge_set)]
    frameworks = [{"name": name, "evidence_count": count} for name, count in framework_counts.most_common(30)]
    indexed_at = project["indexed_at"] or ""
    return {
        "ok": True,
        "project": {"project_id": project["project_id"], "name": project["name"], "repository_url": project["repository_url"], "default_branch": project["default_branch"], "indexed_commit": project["latest_commit"], "indexed_at": indexed_at, "index_status": project["status"]},
        "analysis": {
            "mode": "static-source-analysis",
            "generated_at": server.datetime.now(server.timezone.utc).isoformat(),
            "source_files_analyzed": len(files),
            "source_bytes_analyzed": total_bytes,
            "code_files": code_files,
            "lines_of_source": total_lines,
            "imports_detected": total_imports,
            "local_dependency_edges": len(local_edges),
            "functions_detected": total_functions,
            "classes_detected": total_classes,
            "routes_detected": route_count,
            "entrypoints": _unique([item["path"] for item in entrypoints]),
            "entrypoint_evidence": entrypoints[:100],
            "framework_signals": frameworks,
            "dependency_manifest_evidence": manifest_findings[:200],
            "api_routes": unique_routes[:250],
            "outbound_api_calls": _dedupe_api_calls(outbound_api_calls)[:250],
            "data_store_signals": _dedupe_records(storage)[:100],
            "modules": modules[:300],
            "dependency_edges": local_edges[:500],
            "findings": findings,
            "limitations": [
                "Analysis runs against the latest locally indexed commit, not necessarily the current remote HEAD.",
                "Pattern and AST analysis is static; imports, routes, database access, external integrations, and launchability are not runtime-verified.",
                "Unindexed files, excluded sensitive paths, generated/dependency folders, binary files, and files over the indexing limit are not analyzed.",
                "Local dependency edges are heuristic and may omit aliases, dynamic imports, namespace packages, and generated code.",
            ],
        },
    }




def build_api_relationship_map() -> dict[str, Any]:
    """Build conservative, evidence-backed API relationship candidates across indexed repositories."""
    from repository_ingest import _db_executescript
    _db_executescript()
    with server._DB_LOCK:
        with server._database() as connection:
            projects = connection.execute(
                "SELECT project_id, name, repository_url, latest_commit, status FROM projects ORDER BY name"
            ).fetchall()

    analyzed: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    for project in projects:
        try:
            result = analyze_indexed_repository(project["project_id"])
        except (ValueError, RuntimeError) as exc:
            skipped.append({"project_id": project["project_id"], "name": project["name"], "reason": str(exc)})
            continue
        analysis = result["analysis"]
        analyzed.append({
            "project": result["project"],
            "routes": analysis["api_routes"],
            "calls": analysis["outbound_api_calls"],
        })

    providers: list[dict[str, Any]] = []
    for item in analyzed:
        for base in item["calls"]:
            if base["client"] != "base-url configuration":
                continue
            parsed = urlsplit(base["target"])
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                continue
            providers.append({
                "project": item["project"],
                "base": base,
                "origin": f"{parsed.scheme.lower()}://{parsed.netloc.lower()}",
                "base_path": parsed.path.rstrip("/"),
                "routes": item["routes"],
            })

    relationships: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for caller in analyzed:
        for call in caller["calls"]:
            if call["client"] == "base-url configuration":
                continue
            parsed = urlsplit(call["target"])
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                continue
            target_path = parsed.path or "/"
            for provider in providers:
                if provider["project"]["project_id"] == caller["project"]["project_id"]:
                    continue
                if f"{parsed.scheme.lower()}://{parsed.netloc.lower()}" != provider["origin"]:
                    continue
                base_path = provider["base_path"]
                if base_path and not (target_path == base_path or target_path.startswith(base_path + "/")):
                    continue
                relative_path = target_path[len(base_path):] if base_path else target_path
                relative_path = "/" + relative_path.lstrip("/")
                matched_routes = [
                    route for route in provider["routes"]
                    if route["method"] != "MOUNT" and route["path"].rstrip("/") == relative_path.rstrip("/")
                ]
                for route in matched_routes:
                    key = (caller["project"]["project_id"], provider["project"]["project_id"], call["source"], route["source"])
                    if key in seen:
                        continue
                    seen.add(key)
                    relationships.append({
                        "caller": {
                            "project_id": caller["project"]["project_id"],
                            "name": caller["project"]["name"],
                            "repository_url": caller["project"]["repository_url"],
                            "indexed_commit": caller["project"]["indexed_commit"],
                        },
                        "provider": {
                            "project_id": provider["project"]["project_id"],
                            "name": provider["project"]["name"],
                            "repository_url": provider["project"]["repository_url"],
                            "indexed_commit": provider["project"]["indexed_commit"],
                        },
                        "target": call["target"],
                        "method": route["method"],
                        "route": route["path"],
                        "caller_evidence": call["source"],
                        "provider_evidence": route["source"],
                        "confidence": "static-exact-host-and-route-match",
                        "evidence": "Static URL target matches another indexed repository's configured API base URL and declared route; runtime traffic is not verified.",
                    })

    return {
        "ok": True,
        "mode": "static-cross-repository-api-map",
        "repositories_analyzed": len(analyzed),
        "repositories_skipped": skipped,
        "relationships": relationships[:500],
        "limitations": [
            "Only already-indexed repositories are considered; this endpoint does not fetch or execute repository code.",
            "A relationship is reported only when a static outbound URL matches another indexed repository's configured API base URL and an exactly matching declared route.",
            "Dynamic URLs, environment-expanded URLs, proxies, API gateways, aliases, and route parameters may be missed.",
            "A static match is a candidate integration, not proof of deployment, reachability, authentication, or live network traffic.",
        ],
    }


def _resolve_local_import(
    source_path: str,
    module: str,
    known_paths: set[str],
    paths_by_stem: dict[str, list[str]],
) -> str | None:
    """Resolve common Python and JS/TS local imports against indexed paths only."""
    source = PurePosixPath(source_path)
    suffix = source.suffix.lower()
    candidates: list[str] = []

    if module.startswith(".") and suffix in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
        base = source.parent.joinpath(module).as_posix()
        candidates.extend([base, base + ".ts", base + ".tsx", base + ".js", base + ".jsx", base + ".mjs", base + ".cjs", base + ".json"])
        candidates.extend(f"{base}/index{ext}" for ext in (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".json"))
    else:
        module_path = module.lstrip(".").replace(".", "/")
        if module_path:
            candidates.extend((module_path + ".py", module_path + "/__init__.py"))
            if module.startswith("."):
                base = source.parent
                candidates.extend((base.joinpath(module_path + ".py").as_posix(),
                                   base.joinpath(module_path, "__init__.py").as_posix()))
        leaf = module.split(".")[-1]
        candidates.extend(paths_by_stem.get(leaf, []))
        candidates.extend(paths_by_stem.get(module.split(".")[0], []))

    for candidate in candidates:
        normalized = PurePosixPath(candidate).as_posix()
        if normalized in known_paths:
            return normalized
    # Only fall back to a stem when it is unique; duplicate names are ambiguous.
    stem = module.rstrip("/").split("/")[-1].split(".")[-1]
    matches = paths_by_stem.get(stem, [])
    return matches[0] if len(matches) == 1 else None

def _role_for_path(path: str, text: str) -> str:
    lower = path.lower()
    if "test" in lower or re.search(r"\b(?:describe|it|test)\s*\(", text):
        return "Tests / verification"
    if "api" in lower or "route" in lower or re.search(r"@(?:app|router)\.(?:get|post|put|patch|delete)", text):
        return "API / routing"
    if any(part in lower for part in ("model", "schema", "database", "repository", "store")):
        return "Data / persistence"
    if any(part in lower for part in ("component", "page", "view", "app.tsx", "app.jsx", "frontend", "webapp/src")):
        return "User interface"
    if any(part in lower for part in ("agent", "llm", "model", "prompt", "ai/")):
        return "AI / domain logic"
    if any(part in lower for part in ("config", "setting", "policy", "auth", "security")):
        return "Configuration / security"
    if PurePosixPath(path).name in {"main.py", "app.py", "server.py", "index.ts", "index.js", "main.ts", "main.tsx", "streamlit_app.py"}:
        return "Application entrypoint"
    return "Application / supporting module"



def _dedupe_api_calls(records: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[tuple[str, str, str]] = set()
    result = []
    for record in records:
        key = (record["client"], record["target"], record["source"])
        if key not in seen:
            seen.add(key)
            result.append(record)
    return result


def _dedupe_records(records: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[tuple[str, str]] = set()
    result = []
    for record in records:
        key = (record["name"], record["source"])
        if key not in seen:
            seen.add(key)
            result.append(record)
    return result
