"""SysCentre local runtime: standard-library HTTP API with an allowlisted command surface."""
from __future__ import annotations

import json
import os
import platform
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock
from typing import Any

HOST = os.environ.get("SYSCENTRE_HOST", "127.0.0.1")
PORT = int(os.environ.get("SYSCENTRE_PORT", "8765"))
STARTED_AT = time.time()
_LEDGER: list[dict[str, Any]] = []
_LEDGER_LOCK = Lock()
MAX_BODY_BYTES = 8_192


def record_event(event_type: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    event = {
        "id": f"evt-{time.time_ns()}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": event_type,
        "message": message,
        "details": details or {},
    }
    with _LEDGER_LOCK:
        _LEDGER.append(event)
        del _LEDGER[:-200]
    return event


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
        "event_ledger": "in-memory",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def execute_command(command: str) -> dict[str, Any]:
    """Execute a known runtime command. Never forwards input to a shell."""
    normalized = command.strip().lower()
    allowed = {
        "status": lambda: runtime_status(),
        "help": lambda: {
            "available_commands": ["status", "help", "diagnostics"],
            "note": "Only explicitly allowlisted runtime commands are accepted.",
        },
        "diagnostics": lambda: {
            "checks": [
                {"name": "runtime", "state": "pass", "detail": "HTTP server is responding"},
                {"name": "policy_gate", "state": "pass", "detail": "Command allowlist is active"},
                {"name": "event_ledger", "state": "pass", "detail": "In-memory event ledger is available"},
            ],
        },
    }
    if normalized not in allowed:
        record_event("policy.denied", "Command rejected by policy gate", {"command": command[:120]})
        raise ValueError("Command not allowed. Use status, help, or diagnostics.")
    result = allowed[normalized]()
    record_event("command.accepted", f"Runtime command executed: {normalized}", {"command": normalized})
    return {"ok": True, "command": normalized, "result": result}


class Handler(BaseHTTPRequestHandler):
    server_version = "SysCentreRuntime/0.1"

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:5173")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self._send_json(200, {"ok": True})

    def do_GET(self) -> None:
        if self.path == "/api/health":
            self._send_json(200, {"ok": True, "service": "syscentre-runtime"})
        elif self.path == "/api/status":
            self._send_json(200, runtime_status())
        elif self.path == "/api/events":
            with _LEDGER_LOCK:
                events = list(reversed(_LEDGER[-50:]))
            self._send_json(200, {"events": events, "count": len(events)})
        else:
            self._send_json(404, {"ok": False, "error": "Route not found"})

    def do_POST(self) -> None:
        if self.path != "/api/command":
            self._send_json(404, {"ok": False, "error": "Route not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY_BYTES:
                raise ValueError("Request body must be between 1 and 8192 bytes.")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict) or not isinstance(payload.get("command"), str):
                raise ValueError("JSON body must contain a string 'command'.")
            self._send_json(200, execute_command(payload["command"]))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            self._send_json(400, {"ok": False, "error": str(exc)})

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
