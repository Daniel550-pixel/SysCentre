import { useCallback, useEffect, useState, type FormEvent } from "react";
import {
  Activity, ArrowDownRight, ArrowUpRight, Bot, Check, ChevronRight,
  CircleDot, Command, Cpu, Database, FolderGit2, Gauge, Layers3, LockKeyhole, RefreshCw,
  Send, ShieldCheck, TerminalSquare, Wifi, WifiOff, Zap,
} from "lucide-react";

const API = "http://127.0.0.1:8765";
type RuntimeStatus = { name: string; state: string; host: string; port: number; uptime_seconds: number; python_version: string; platform: string; policy_gate: string; event_ledger: string; event_ledger_path?: string; timestamp: string };
type RuntimeEvent = { id: string; timestamp: string; type: string; message: string; details: Record<string, unknown> };
type CommandResponse = { ok: boolean; command: string; result?: unknown; error?: string };

function formatUptime(seconds = 0) {
  const total = Math.max(0, Math.floor(seconds));
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  const secs = total % 60;
  return hours ? hours + "h " + minutes + "m" : minutes ? minutes + "m " + secs + "s" : secs + "s";
}
function formatTime(value: string) {
  try { return new Date(value).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }); }
  catch { return value; }
}

export default function App() {
  const [status, setStatus] = useState<RuntimeStatus | null>(null);
  const [events, setEvents] = useState<RuntimeEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const [busy, setBusy] = useState(false);
  const [command, setCommand] = useState("");
  const [output, setOutput] = useState("Runtime console ready. Enter help to see available commands.");
  const [lastUpdated, setLastUpdated] = useState("");

  const refresh = useCallback(async () => {
    try {
      const responses = await Promise.all([
        fetch(API + "/api/status", { signal: AbortSignal.timeout(2500) }),
        fetch(API + "/api/events", { signal: AbortSignal.timeout(2500) }),
      ]);
      if (!responses[0].ok || !responses[1].ok) throw new Error("Runtime API returned an error");
      const nextStatus = (await responses[0].json()) as RuntimeStatus;
      const nextEvents = (await responses[1].json()) as { events: RuntimeEvent[] };
      setStatus(nextStatus);
      setEvents(nextEvents.events ?? []);
      setConnected(true);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch {
      setConnected(false);
      setStatus(null);
    }
  }, []);

  useEffect(() => {
    void refresh();
    const timer = window.setInterval(() => void refresh(), 5000);
    return () => window.clearInterval(timer);
  }, [refresh]);

  async function runCommand(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const submitted = command.trim();
    if (!submitted || busy) return;
    setBusy(true);
    setOutput("> " + submitted + "\n\nRunning through policy gate…");
    setCommand("");
    try {
      const response = await fetch(API + "/api/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: submitted }),
        signal: AbortSignal.timeout(5000),
      });
      const data = (await response.json()) as CommandResponse;
      setOutput(data.ok ? "> " + submitted + "\n\n" + JSON.stringify(data.result, null, 2) : "> " + submitted + "\n\nREJECTED: " + (data.error ?? "Request failed"));
      await refresh();
    } catch {
      setOutput("> " + submitted + "\n\nERROR: Could not reach the local runtime at " + API + ".");
    } finally {
      setBusy(false);
    }
  }

  const uptime = status ? formatUptime(status.uptime_seconds) : "—";

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><Layers3 size={22} strokeWidth={2.2} /></div>
          <div><div className="brand-name">SysCentre<span>.</span></div><div className="brand-subtitle">SYSTEMS CONTROL PLANE</div></div>
        </div>
        <div className="workspace-label">WORKSPACE</div>
        <nav className="nav-list" aria-label="Main navigation">
          <a className="nav-item active" href="#overview"><Gauge size={17} /><span>Overview</span><ChevronRight className="nav-chevron" size={15} /></a>
          <a className="nav-item" href="#runtime"><Cpu size={17} /><span>Runtime</span></a>
          <a className="nav-item" href="#console"><TerminalSquare size={17} /><span>Command console</span></a>
          <a className="nav-item" href="#security"><ShieldCheck size={17} /><span>Policy & security</span></a>
          <a className="nav-item" href="#events"><Activity size={17} /><span>Event ledger</span></a>
        </nav>
        <div className="sidebar-spacer" />
        <div className="sidebar-runtime">
          <div className="sidebar-runtime-top"><span className={"status-dot " + (connected ? "online" : "offline")} /><span>{connected ? "Local runtime connected" : "Runtime disconnected"}</span></div>
          <div className="runtime-address">127.0.0.1:8765</div>
          <div className="sidebar-meter"><span style={{ width: connected ? "100%" : "12%" }} /></div>
        </div>
        <div className="sidebar-footer"><div className="avatar">SC</div><div><div className="footer-name">Local workspace</div><div className="footer-role">Administrator session</div></div><span className="footer-menu">•••</span></div>
      </aside>

      <main className="main-content" id="overview">
        <header className="topbar">
          <div className="breadcrumbs"><span>Workspace</span><ChevronRight size={14} /><strong>Overview</strong></div>
          <div className="topbar-right"><span className="local-badge"><span className="tiny-dot" /> LOCAL ENVIRONMENT</span><span className="topbar-divider" /><button className="icon-button" onClick={() => void refresh()} title="Refresh data" aria-label="Refresh data"><RefreshCw size={16} /></button><div className="topbar-avatar">SC</div></div>
        </header>

        <div className="page-wrap">
          <section className="page-heading">
            <div><div className="eyebrow"><span className="eyebrow-line" /> CONTROL PLANE / 001</div><h1>System overview</h1><p className="page-description">Observe runtime health, verify policy controls, and operate your local system.</p></div>
            <div className="heading-actions"><span className={"connection-pill " + (connected ? "connected" : "disconnected")}>{connected ? <Check size={14} /> : <WifiOff size={14} />}{connected ? "All systems operational" : "Runtime unavailable"}</span><button className="secondary-button" onClick={() => void refresh()}><RefreshCw size={15} /> Refresh</button></div>
          </section>

          {!connected && <div className="connection-alert"><WifiOff size={18} /><div><strong>Runtime not detected</strong><p>Start the Python runtime to populate live system data. The dashboard will reconnect automatically.</p></div><code>python .\runtime\server.py</code></div>}

          <section className="metric-grid" aria-label="Runtime metrics">
            <article className="metric-card"><div className="metric-top"><span>Runtime status</span><span className="metric-icon purple"><Activity size={17} /></span></div><div className="metric-value status-value"><span className={"status-dot " + (connected ? "online" : "offline")} />{connected ? "Operational" : "Offline"}</div><div className="metric-foot"><span className="muted">Local API service</span><span className="metric-foot-icon"><ArrowUpRight size={14} /></span></div></article>
            <article className="metric-card"><div className="metric-top"><span>Runtime uptime</span><span className="metric-icon blue"><Zap size={17} /></span></div><div className="metric-value">{uptime}</div><div className="metric-foot"><span className="muted">Current process session</span><span className="metric-foot-icon"><Activity size={14} /></span></div></article>
            <article className="metric-card"><div className="metric-top"><span>Policy gate</span><span className="metric-icon green"><LockKeyhole size={17} /></span></div><div className="metric-value">{status?.policy_gate === "enabled" ? "Enforced" : "—"}</div><div className="metric-foot"><span className="muted">Allowlisted commands only</span><span className="positive-text"><ShieldCheck size={14} /> Active</span></div></article>
            <article className="metric-card"><div className="metric-top"><span>Ledger events</span><span className="metric-icon amber"><Layers3 size={17} /></span></div><div className="metric-value">{events.length.toString().padStart(2, "0")}<span className="value-suffix"> / 50</span></div><div className="metric-foot"><span className="muted">Recent persisted records</span><span className="metric-foot-icon"><ArrowDownRight size={14} /></span></div></article>
          </section>

          <div className="content-grid">
            <section className="panel runtime-panel" id="runtime">
              <div className="panel-header"><div><div className="panel-kicker">INFRASTRUCTURE</div><h2>Runtime environment</h2></div><span className="panel-icon"><Cpu size={18} /></span></div>
              <div className="runtime-hero"><div className="runtime-orb"><div className="orb-core"><Bot size={25} /></div><span className="orb-ring ring-one" /><span className="orb-ring ring-two" /></div><div className="runtime-hero-copy"><div className="runtime-name">SysCentre Runtime</div><div className="runtime-caption">Local execution environment</div><div className={"runtime-state " + (connected ? "state-online" : "state-offline")}><span className="status-dot" />{connected ? "RUNNING" : "NOT CONNECTED"}</div></div></div>
              <div className="detail-list">
                <div className="detail-row"><span>API endpoint</span><code>127.0.0.1:{status?.port ?? 8765}</code></div>
                <div className="detail-row"><span>Python version</span><strong>{status?.python_version ?? "Waiting for runtime"}</strong></div>
                <div className="detail-row"><span>Operating system</span><strong className="truncate">{status?.platform ?? "—"}</strong></div>
                <div className="detail-row"><span>Event storage</span><span className="storage-tag"><CircleDot size={11} /> {status?.event_ledger === "sqlite" ? "SQLite persistent" : "Waiting"}</span></div>
              </div>
            </section>

            <section className="panel console-panel" id="console">
              <div className="panel-header"><div><div className="panel-kicker">INTERACTIVE</div><h2>Command console</h2></div><span className="console-live"><span className="status-dot online" /> LIVE</span></div>
              <div className="console-window">
                <div className="console-titlebar"><div className="window-dots"><i /><i /><i /></div><span>syscentre — local shell interface</span><Command size={14} /></div>
                <pre className="console-output">{output}</pre>
                <form className="console-input-row" onSubmit={runCommand}><span className="prompt-symbol">›</span><input value={command} onChange={(e) => setCommand(e.target.value)} placeholder="Enter a runtime command…" aria-label="Runtime command" disabled={!connected || busy} /><button type="submit" disabled={!connected || busy || !command.trim()} aria-label="Run command"><Send size={15} /></button></form>
              </div>
              <div className="command-hints"><span>QUICK COMMANDS</span>{["status", "diagnostics", "help"].map((item) => <button key={item} onClick={() => setCommand(item)} disabled={!connected}>{item}</button>)}</div>
              <div className="console-note"><LockKeyhole size={13} /> Commands are checked against the runtime allowlist.</div>
            </section>
          </div>

          <section className="panel policy-panel" id="security">
            <div className="panel-header"><div><div className="panel-kicker">TRUST BOUNDARY</div><h2>Policy & execution controls</h2></div><span className="policy-status"><ShieldCheck size={14} /> POLICY GATE ENABLED</span></div>
            <p className="panel-description">SysCentre separates decision-making from execution. Requests are validated before any runtime operation is permitted.</p>
            <div className="policy-flow">
              <div className="policy-step"><span className="step-icon"><Bot size={18} /></span><div><strong>Request</strong><span>Input received</span></div></div><div className="flow-arrow"><ChevronRight size={18} /></div>
              <div className="policy-step gate-step"><span className="step-icon"><ShieldCheck size={18} /></span><div><strong>Policy gate</strong><span>Allowlist validation</span></div><span className="gate-chip">ACTIVE</span></div><div className="flow-arrow"><ChevronRight size={18} /></div>
              <div className="policy-step"><span className="step-icon"><TerminalSquare size={18} /></span><div><strong>Runtime</strong><span>Approved operation</span></div></div>
            </div>
            <div className="policy-footnote"><LockKeyhole size={14} /><span>Arbitrary shell commands are not exposed. This is an initial control boundary, not yet a full sandbox or authentication system.</span></div>
          </section>

          <section className="panel events-panel" id="events">
            <div className="panel-header"><div><div className="panel-kicker">OBSERVABILITY</div><h2>Recent event ledger</h2></div><button className="text-button" onClick={() => void refresh()}>View latest <ChevronRight size={14} /></button></div>
            <div className="events-table-wrap"><table className="events-table"><thead><tr><th>EVENT</th><th>TYPE</th><th>TIME</th><th>STATUS</th></tr></thead><tbody>
              {events.length ? events.slice(0, 6).map((item) => <tr key={item.id}><td><span className="event-name"><span className={"event-dot " + (item.type.includes("denied") ? "event-denied" : "")} />{item.message}</span></td><td><code className="event-type">{item.type}</code></td><td className="event-time">{formatTime(item.timestamp)}</td><td><span className={"event-result " + (item.type.includes("denied") ? "result-denied" : "result-ok")}>{item.type.includes("denied") ? "Denied" : "Recorded"}</span></td></tr>) : <tr><td colSpan={4} className="empty-state">{connected ? "No events recorded yet. Run a command to create the first event." : "Waiting for a runtime connection…"}</td></tr>}
            </tbody></table></div>
            <div className="events-footer"><span><span className="status-dot online" /> Event ledger {connected ? "synchronized" : "not connected"}</span><span>Auto-refresh · 5 seconds{lastUpdated ? " · Updated " + lastUpdated : ""}</span></div>
          </section>
          <footer className="page-footer"><span>SYSCENTRE <span className="footer-version">v0.2.0 PERSISTENT RUNTIME</span></span><span><Wifi size={13} /> Local-first by design</span></footer>
        </div>
      </main>
    </div>
  );
}
