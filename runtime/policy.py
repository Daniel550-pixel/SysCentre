"""Small deterministic policy engine for SysCentre runtime actions."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    action: str
    risk: str
    reason: str
    requires_approval: bool = False


# Deliberately narrow: these commands are read-only and cannot invoke a shell.
_COMMANDS: dict[str, tuple[str, str]] = {
    "status": ("read", "Read runtime status"),
    "help": ("read", "List supported commands"),
    "diagnostics": ("read", "Run non-destructive runtime diagnostics"),
}


def evaluate_command(command: str) -> PolicyDecision:
    normalized = command.strip().lower()
    if not normalized:
        return PolicyDecision(False, normalized, "unknown", "A command is required")
    spec = _COMMANDS.get(normalized)
    if spec is None:
        return PolicyDecision(False, normalized[:120], "blocked", "Command is not in the explicit allowlist")
    risk, reason = spec
    return PolicyDecision(True, normalized, risk, reason)


def policy_catalog() -> list[dict[str, str | bool]]:
    return [
        {"command": name, "risk": risk, "description": description, "requires_approval": False}
        for name, (risk, description) in sorted(_COMMANDS.items())
    ]
