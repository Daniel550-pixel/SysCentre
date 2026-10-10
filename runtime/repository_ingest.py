"""Read-only GitHub repository ingestion for SysCentre's project registry.

Imports tracked repository metadata and readable source/documentation files into the local
SQLite index. Projects are indexed, not merged or executed. Sensitive-looking paths and
binary/oversized files are catalogued as skipped, never copied into the text index.
"""
from __future__ import annotations

import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if Path(getattr(sys.modules.get("__main__"), "__file__", "")).name == "server.py":
    import __main__ as server
else:
    import server

CATALOG_PATH = Path(__file__).with_name("repository_catalog.json")
API_ROOT = "https://api.github.com"
MAX_TEXT_BYTES = 900_000
MAX_FILES_PER_REPO = 10_000
SENSITIVE_PARTS = {
    ".env", ".env.local", ".env.production", "secrets", "secret", "credentials",
    "id_rsa", "id_ed25519", "private_key", "service-account",
}
SENSITIVE_SUFFIXES = (".pem", ".p12", ".pfx", ".key", ".keystore")
IGNORED_PARTS = {
    "node_modules", ".git", "dist", "build", ".next", ".venv", "venv",
    "__pycache__", "coverage", ".turbo",
}


def load_catalog() -> list[dict[str, Any]]:
    with CATALOG_PATH.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload.get("repositories", [])


def _repo_id(value: str) -> dict[str, Any]:
    for item in load_catalog():
        if item["id"] == value or item["name"].lower() == value.lower():
            return item
    raise ValueError("Repository is not in the SysCentre catalog.")


def _api_json(url: str) -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "SysCentre-Repository-Indexer/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 403:
            raise RuntimeError("GitHub rate limit or access restriction. Set GITHUB_TOKEN for higher limits.") from exc
        if exc.code == 404:
            raise RuntimeError("GitHub repository or tree was not found or is not accessible.") from exc
        raise RuntimeError(f"GitHub API returned HTTP {exc.code}.") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"Could not reach GitHub: {exc}") from exc


def _is_sensitive(path: str) -> bool:
    parts = [part.lower() for part in path.split("/")]
    filename = parts[-1] if parts else ""
    if filename.startswith(".env") or any(part in SENSITIVE_PARTS for part in parts):
        return True
    if filename.endswith(SENSITIVE_SUFFIXES):
        return True
    if filename in {".npmrc", ".pypirc", "credentials.json"}:
        return True
    return False


def _is_ignored(path: str) -> bool:
    return any(part.lower() in IGNORED_PARTS for part in path.split("/"))


def _db_executescript() -> None:
    with server._DB_LOCK:
        with server._database() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    repository_url TEXT NOT NULL,
                    default_branch TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    latest_commit TEXT NOT NULL DEFAULT '',
                    indexed_at TEXT NOT NULL,
                    file_count INTEGER NOT NULL DEFAULT 0,
                    text_file_count INTEGER NOT NULL DEFAULT 0,
                    skipped_file_count INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'registered',
                    metadata_json TEXT NOT NULL DEFAULT '{}'
                );
                CREATE TABLE IF NOT EXISTS repository_files (
                    project_id TEXT NOT NULL,
                    path TEXT NOT NULL,
                    blob_sha TEXT NOT NULL DEFAULT '',
                    size_bytes INTEGER NOT NULL DEFAULT 0,
                    file_kind TEXT NOT NULL,
                    content TEXT,
                    skip_reason TEXT NOT NULL DEFAULT '',
                    PRIMARY KEY (project_id, path)
                );
                CREATE INDEX IF NOT EXISTS idx_repository_files_project ON repository_files(project_id);
                CREATE TABLE IF NOT EXISTS ingest_runs (
                    run_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    finished_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    files_seen INTEGER NOT NULL DEFAULT 0,
                    files_indexed INTEGER NOT NULL DEFAULT 0,
                    files_skipped INTEGER NOT NULL DEFAULT 0,
                    error TEXT NOT NULL DEFAULT ''
                );
            """)


def list_projects() -> list[dict[str, Any]]:
    _db_executescript()
    with server._DB_LOCK:
        with server._database() as connection:
            rows = connection.execute(
                "SELECT project_id, name, repository_url, default_branch, description, latest_commit, indexed_at, file_count, text_file_count, skipped_file_count, status FROM projects ORDER BY name"
            ).fetchall()
    indexed = {row["project_id"]: dict(row) for row in rows}
    result = []
    for item in load_catalog():
        result.append(indexed.get(item["id"], {
            "project_id": item["id"], "name": item["name"], "repository_url": item["url"],
            "default_branch": item["default_branch"], "description": "", "latest_commit": "",
            "indexed_at": "", "file_count": 0, "text_file_count": 0, "skipped_file_count": 0,
            "status": "registered",
        }))
    return result


def ingest_repository(project_key: str) -> dict[str, Any]:
    item = _repo_id(project_key)
    _db_executescript()
    started = datetime.now(timezone.utc).isoformat()
    run_id = f"ingest-{time.time_ns()}"
    owner_repo = urllib.parse.urlparse(item["url"]).path.strip("/")
    repo_data = _api_json(f"{API_ROOT}/repos/{owner_repo}")
    branch = repo_data.get("default_branch") or item["default_branch"]
    commit = _api_json(f"{API_ROOT}/repos/{owner_repo}/commits/{urllib.parse.quote(branch, safe='')}")
    commit_sha = commit.get("sha", "")
    tree = _api_json(f"{API_ROOT}/repos/{owner_repo}/git/trees/{commit_sha}?recursive=1")
    if tree.get("truncated"):
        raise RuntimeError("GitHub returned a truncated repository tree; complete indexing cannot be claimed.")
    entries = [node for node in tree.get("tree", []) if node.get("type") == "blob"]
    if len(entries) > MAX_FILES_PER_REPO:
        raise RuntimeError(f"Repository has {len(entries)} files; safety limit is {MAX_FILES_PER_REPO} per ingestion run.")

    files_indexed = 0
    files_skipped = 0
    rows: list[tuple[Any, ...]] = []
    for node in entries:
        path = node.get("path", "")
        size = int(node.get("size", 0) or 0)
        sha = node.get("sha", "")
        if _is_sensitive(path):
            rows.append((item["id"], path, sha, size, "excluded", None, "sensitive-looking path"))
            files_skipped += 1
            continue
        if _is_ignored(path):
            rows.append((item["id"], path, sha, size, "excluded", None, "generated/dependency directory"))
            files_skipped += 1
            continue
        if size > MAX_TEXT_BYTES:
            rows.append((item["id"], path, sha, size, "excluded", None, "file exceeds text indexing limit"))
            files_skipped += 1
            continue
        try:
            blob = _api_json(f"{API_ROOT}/repos/{owner_repo}/git/blobs/{sha}")
            raw = base64.b64decode(blob.get("content", ""))
            text_content = raw.decode("utf-8")
            if "\x00" in text_content:
                raise UnicodeDecodeError("utf-8", raw, 0, 1, "binary content")
            rows.append((item["id"], path, sha, size, "text", text_content, ""))
            files_indexed += 1
        except (UnicodeDecodeError, ValueError):
            rows.append((item["id"], path, sha, size, "binary", None, "not UTF-8 text"))
            files_skipped += 1
        except RuntimeError as exc:
            # Keep ingestion failure explicit instead of silently claiming completeness.
            raise RuntimeError(f"Failed indexing {path}: {exc}") from exc

    finished = datetime.now(timezone.utc).isoformat()
    description = repo_data.get("description") or ""
    status = "indexed_with_exclusions" if files_skipped else "indexed"
    with server._DB_LOCK:
        with server._database() as connection:
            connection.execute("DELETE FROM repository_files WHERE project_id = ?", (item["id"],))
            connection.executemany(
                "INSERT INTO repository_files (project_id, path, blob_sha, size_bytes, file_kind, content, skip_reason) VALUES (?, ?, ?, ?, ?, ?, ?)",
                rows,
            )
            connection.execute("""
                INSERT INTO projects (project_id, name, repository_url, default_branch, description, latest_commit, indexed_at, file_count, text_file_count, skipped_file_count, status, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    name=excluded.name, repository_url=excluded.repository_url, default_branch=excluded.default_branch,
                    description=excluded.description, latest_commit=excluded.latest_commit, indexed_at=excluded.indexed_at,
                    file_count=excluded.file_count, text_file_count=excluded.text_file_count,
                    skipped_file_count=excluded.skipped_file_count, status=excluded.status, metadata_json=excluded.metadata_json
            """, (item["id"], item["name"], item["url"], branch, description, commit_sha, finished, len(entries), files_indexed, files_skipped, status, json.dumps({
                "private": repo_data.get("private", False),
                "language": repo_data.get("language"),
                "topics": repo_data.get("topics", []),
                "stars": repo_data.get("stargazers_count", 0),
                "updated_at": repo_data.get("updated_at"),
                "tree_sha": tree.get("sha", ""),
            })))
            connection.execute(
                "INSERT INTO ingest_runs (run_id, project_id, started_at, finished_at, status, files_seen, files_indexed, files_skipped) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (run_id, item["id"], started, finished, status, len(entries), files_indexed, files_skipped),
            )
    server.record_event("repository.indexed", f"Indexed repository {item['name']}", {
        "project_id": item["id"], "commit": commit_sha, "files_seen": len(entries),
        "files_indexed": files_indexed, "files_skipped": files_skipped, "status": status,
    })
    return {
        "ok": True, "project_id": item["id"], "name": item["name"], "repository_url": item["url"],
        "commit": commit_sha, "branch": branch, "files_seen": len(entries),
        "files_indexed": files_indexed, "files_skipped": files_skipped, "status": status,
        "note": "Source files were indexed locally. Sensitive-looking paths, generated/dependency directories, binary files, and oversized files are recorded as exclusions.",
    }


def search_index(query: str, limit: int = 50) -> dict[str, Any]:
    term = query.strip()
    if len(term) < 2:
        raise ValueError("Search query must contain at least two characters.")
    if len(term) > 200:
        raise ValueError("Search query must be 200 characters or fewer.")
    bounded = max(1, min(int(limit), 100))
    _db_executescript()
    with server._DB_LOCK:
        with server._database() as connection:
            rows = connection.execute(
                """SELECT p.project_id, p.name, p.repository_url, f.path, f.blob_sha, f.size_bytes, f.content
                   FROM repository_files f JOIN projects p ON p.project_id = f.project_id
                   WHERE f.file_kind = 'text' AND f.content LIKE ?
                   ORDER BY p.name, f.path LIMIT ?""",
                ("%" + term + "%", bounded),
            ).fetchall()
    results = []
    for row in rows:
        content = row["content"] or ""
        position = content.lower().find(term.lower())
        start = max(0, position - 140)
        end = min(len(content), position + len(term) + 220)
        excerpt = content[start:end].replace("\n", " ").replace("\r", " ")
        results.append({
            "project_id": row["project_id"], "project_name": row["name"],
            "repository_url": row["repository_url"], "path": row["path"],
            "blob_sha": row["blob_sha"], "size_bytes": row["size_bytes"], "excerpt": excerpt,
        })
    return {"query": term, "results": results, "count": len(results), "limit": bounded}

def project_files(project_key: str, query: str = "", limit: int = 100) -> dict[str, Any]:
    item = _repo_id(project_key)
    _db_executescript()
    bounded = max(1, min(int(limit), 200))
    with server._DB_LOCK:
        with server._database() as connection:
            if query:
                rows = connection.execute(
                    "SELECT path, blob_sha, size_bytes, file_kind, content, skip_reason FROM repository_files WHERE project_id = ? AND path LIKE ? ORDER BY path LIMIT ?",
                    (item["id"], f"%{query}%", bounded),
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT path, blob_sha, size_bytes, file_kind, content, skip_reason FROM repository_files WHERE project_id = ? ORDER BY path LIMIT ?",
                    (item["id"], bounded),
                ).fetchall()
    return {"project_id": item["id"], "files": [dict(row) for row in rows], "count": len(rows)}
