"""SysCentre local runtime: persistent audit ledger and policy-gated command API."""
from __future__ import annotations

import json
import os
import platform
import sqlite3
import time
from urllib.parse import parse_qs, unquote, urlsplit
from datetime import datetime, timezone
from contextlib import contextmanager
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock
from typing import Any

from policy import evaluate_command, policy_catalog

HOST = os.environ.get("SYSCENTRE_HOST", "127.0.0.1")
PORT = int(os.environ.get("SYSCENTRE_PORT", "8765"))
STARTED_AT = time.time()
DB_PATH = Path(os.environ.get("SYSCENTRE_DB_PATH", str(Path.home() / ".syscentre" / "syscentre.db")))
_DB_LOCK = Lock()
MAX_BODY_BYTES = 8_192

# Cross-origin browser access is limited to the published fallback and local dev UI.
# Never use "*" here: the runtime exposes local machine state and indexed source text.
DEFAULT_ALLOWED_ORIGINS = (
    "https://daniel550-pixel.github.io",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
)
_configured_origins = os.environ.get("SYSCENTRE_ALLOWED_ORIGINS")
ALLOWED_ORIGINS = frozenset(
    value.strip().rstrip("/")
    for value in (_configured_origins.split(",") if _configured_origins is not None else DEFAULT_ALLOWED_ORIGINS)
    if value.strip() and value.strip() != "*"
)


def _origin_is_allowed(origin: str | None) -> bool:
    """Return True only for an explicitly configured browser origin."""
    return bool(origin and origin.rstrip("/") in ALLOWED_ORIGINS)


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=5)
    connection.row_factory = sqlite3.Row
    connection.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            type TEXT NOT NULL,
            message TEXT NOT NULL,
            details_json TEXT NOT NULL
        )
    """)
    connection.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)")
    return connection


@contextmanager
def _database():
    connection = _connect()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def record_event(event_type: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    event = {
        "id": f"evt-{time.time_ns()}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": event_type,
        "message": message,
        "details": details or {},
    }
    with _DB_LOCK:
        with _database() as connection:
            connection.execute(
                "INSERT INTO events (id, timestamp, type, message, details_json) VALUES (?, ?, ?, ?, ?)",
                (event["id"], event["timestamp"], event["type"], event["message"], json.dumps(event["details"], ensure_ascii=False)),
            )
            connection.execute("""
                DELETE FROM events WHERE id IN (
                    SELECT id FROM events ORDER BY timestamp DESC LIMIT -1 OFFSET 5000
                )
            """)
    return event


def recent_events(limit: int = 50) -> list[dict[str, Any]]:
    bounded_limit = max(1, min(int(limit), 100))
    with _DB_LOCK:
        with _database() as connection:
            rows = connection.execute(
                "SELECT id, timestamp, type, message, details_json FROM events ORDER BY timestamp DESC LIMIT ?",
                (bounded_limit,),
            ).fetchall()
    return [
        {"id": row["id"], "timestamp": row["timestamp"], "type": row["type"],
         "message": row["message"], "details": json.loads(row["details_json"])}
        for row in rows
    ]


def runtime_status() -> dict[str, Any]:
    return {
        "name": "SysCentre Runtime",
        "state": "online",
        "host": HOST,
        "port": PORT,
        "uptime_seconds": round(time.time() - STARTED_AT, 1),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "policy_gate": "enabled",
        "event_ledger": "sqlite",
        "event_ledger_path": str(DB_PATH),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def execute_command(command: str) -> dict[str, Any]:
    """Execute only explicit runtime commands; user input is never sent to a shell."""
    decision = evaluate_command(command)
    if not decision.allowed:
        record_event("policy.denied", "Command rejected by policy gate", {
            "command": decision.action, "risk": decision.risk, "reason": decision.reason,
        })
        raise ValueError(f"Command not allowed: {decision.reason}. Use status, help, or diagnostics.")
    normalized = decision.action
    if normalized == "status":
        result: Any = runtime_status()
    elif normalized == "help":
        result = {
            "available_commands": [item["command"] for item in policy_catalog()],
            "note": "Only explicitly allowlisted runtime commands are accepted; arbitrary shell execution is disabled.",
        }
    else:
        result = {"checks": [
            {"name": "runtime", "state": "pass", "detail": "HTTP server process is responding"},
            {"name": "policy_gate", "state": "pass", "detail": "Deterministic command policy is active"},
            {"name": "event_ledger", "state": "pass", "detail": "SQLite event ledger is available"},
        ]}
    record_event("command.accepted", f"Runtime command executed: {normalized}", {
        "command": normalized, "risk": decision.risk, "policy_reason": decision.reason,
    })
    return {"ok": True, "command": normalized, "result": result}


class Handler(BaseHTTPRequestHandler):
    server_version = "SysCentreRuntime/0.2"

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        origin = self.headers.get("Origin")
        if _origin_is_allowed(origin):
            self.send_header("Access-Control-Allow-Origin", origin.rstrip("/"))
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            if self.headers.get("Access-Control-Request-Private-Network", "").lower() == "true":
                self.send_header("Access-Control-Allow-Private-Network", "true")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self._send_json(200, {"ok": True})

    def do_GET(self) -> None:
        parsed = urlsplit(self.path)
        path = parsed.path
        if path == "/api/health":
            self._send_json(200, {"ok": True, "service": "syscentre-runtime"})
        elif path == "/api/status":
            self._send_json(200, runtime_status())
        elif path == "/api/events":
            events = recent_events(50)
            self._send_json(200, {"events": events, "count": len(events), "storage": "sqlite"})
        elif path == "/api/policy":
            self._send_json(200, {"enabled": True, "mode": "allowlist", "commands": policy_catalog()})
        elif path == "/api/repositories":
            from repository_ingest import list_projects
            projects = list_projects()
            self._send_json(200, {"projects": projects, "count": len(projects)})
        elif path == "/api/ingest-status":
            from repository_ingest import ingest_status
            params = parse_qs(parsed.query)
            project_id = params.get("project_id", [""])[0].strip()
            try:
                self._send_json(200, ingest_status(project_id or None))
            except ValueError as exc:
                self._send_json(400, {"ok": False, "error": str(exc)})
        elif path == "/api/project-inventory":
            inventory_path = Path(__file__).with_name("project_inventory.json")
            with inventory_path.open("r", encoding="utf-8") as handle:
                inventory = json.load(handle)
            projects = inventory.get("projects", [])
            self._send_json(200, {"projects": projects, "count": len(projects), "status": "repository_match_required"})
        elif path == "/api/search":
            from repository_ingest import search_index
            params = parse_qs(parsed.query)
            query = params.get("q", [""])[0]
            try:
                self._send_json(200, search_index(query, limit=int(params.get("limit", ["50"])[0])))
            except (ValueError, TypeError) as exc:
                self._send_json(400, {"ok": False, "error": str(exc)})
        elif path.startswith("/api/repositories/") and path.endswith("/files"):
            from repository_ingest import project_files
            project_id = unquote(path[len("/api/repositories/"):-len("/files")].strip("/"))
            params = parse_qs(parsed.query)
            query = params.get("path", [""])[0]
            try:
                self._send_json(200, project_files(project_id, query=query, limit=int(params.get("limit", ["100"])[0])))
            except (ValueError, TypeError) as exc:
                self._send_json(400, {"ok": False, "error": str(exc)})
        else:
            self._send_json(404, {"ok": False, "error": "Route not found"})

    def do_POST(self) -> None:
        parsed = urlsplit(self.path)
        if parsed.path not in {"/api/command", "/api/repositories/ingest"}:
            self._send_json(404, {"ok": False, "error": "Route not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY_BYTES:
                raise ValueError("Request body must be between 1 and 8192 bytes.")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("Request body must be a JSON object.")
            if parsed.path == "/api/command":
                if not isinstance(payload.get("command"), str):
                    raise ValueError("JSON body must contain a string 'command'.")
                self._send_json(200, execute_command(payload["command"]))
            else:
                project_id = payload.get("project_id")
                if not isinstance(project_id, str) or not project_id.strip():
                    raise ValueError("JSON body must contain a string 'project_id'.")
                from repository_ingest import ingest_repository
                self._send_json(200, ingest_repository(project_id))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            self._send_json(400, {"ok": False, "error": str(exc)})
        except RuntimeError as exc:
            record_event("repository.ingest_failed", "Repository ingestion failed", {"error": str(exc)})
            self._send_json(502, {"ok": False, "error": str(exc)})

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[SysCentre] {self.log_date_time_string()} {fmt % args}")


def main() -> None:
    record_event("runtime.started", "SysCentre local runtime started", {"host": HOST, "port": PORT})
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"SysCentre Runtime listening on http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSysCentre Runtime stopping...")
    finally:
        server.server_close()
        record_event("runtime.stopped", "SysCentre local runtime stopped")


if __name__ == "__main__":
    main()
