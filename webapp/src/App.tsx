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
type PortfolioDimension = "business_model" | "system_type" | "sector" | "market_category";
type Project = { project_id: string; name: string; repository_url: string; default_branch: string; description: string; latest_commit: string; indexed_at: string; file_count: number; text_file_count: number; skipped_file_count: number; status: string; category?: string; purpose?: string; capabilities?: string[]; interface_kind?: string; interface_status?: string; interface_source_url?: string; business_model?: string; system_type?: string; sector?: string; target_market?: string; market_segments?: string[]; market_category?: string; portfolio_role?: string; lifecycle_stage?: string; monetization_status?: string; market_validation?: string; classification_basis?: string; classification_note?: string };
type SourceResult = { project_id: string; project_name: string; repository_url: string; path: string; blob_sha: string; size_bytes: number; excerpt: string };
type InventoryProject = { id: string; name: string; status: string; category: string; candidate_repositories: string[]; description?: string; origin?: string; created_at?: string };
type RuntimeProject = { project_id: string; name: string; repository_url: string; adapter_type: string; runtime_mode: string; execution_state: string; requires_approval: boolean; notes: string; system_type?: string; sector?: string; market_category?: string };
type HostingProject = { project_id: string; name: string; repository_url: string; category?: string; hosting: { adapter_type: string; configured: boolean; ready: boolean; state: string; health: string; readiness_reason?: string; url?: string | null; healthcheck_url?: string; required_paths?: string[]; workspace?: string | null; pid?: number | null; started_at?: number | null; log_path?: string | null; available_actions: string[] } };
type HostingOverview = { ok: boolean; subsystem: string; schema_version: number; workspace_root: string; counts: { total: number; configured: number; ready: number; running: number; setup_required: number; not_configured: number; unhealthy: number }; projects: HostingProject[] };
type IngestJob = { project_id: string; target_commit: string; branch: string; started_at: string; updated_at: string; status: string; files_seen: number; files_processed: number; files_indexed: number; files_skipped: number; error: string };
type ArchitectureLayer = { name: string; role: string; components: string; evidence_paths: string[] };
type ArchitectureFinding = {
  severity: "critical" | "high" | "medium" | "low" | string;
  category: string; title: string; description: string;
  evidence_paths: string[]; recommended_action: string;
};
type ApiRelationship = {
  caller: { project_id: string; name: string; repository_url: string; indexed_commit: string };
  provider: { project_id: string; name: string; repository_url: string; indexed_commit: string };
  target: string; method: string; route: string; caller_evidence: string; caller_line: string; provider_evidence: string; provider_line: string;
  confidence: string; evidence: string;
};
type ApiRelationshipMap = {
  ok: boolean; mode: string; repositories_analyzed: number;
  repositories_skipped: Array<{ project_id: string; name: string; reason: string }>;
  relationships: ApiRelationship[];
  unmatched_outbound_calls: Array<{ caller: { project_id: string; name: string; repository_url: string; indexed_commit: string }; client: string; target: string; source: string; line: string; reason: string }>;
  limitations: string[];
};
type ArchitectureAnalysis = {
  ok: boolean;
  project: { project_id: string; name: string; indexed_commit: string; indexed_at: string; index_status: string };
  analysis: {
    mode: string; generated_at: string; source_files_analyzed: number; source_bytes_analyzed: number;
    code_files: number; lines_of_source: number; imports_detected: number; local_dependency_edges: number;
    functions_detected: number; classes_detected: number; routes_detected: number; entrypoints: string[];
    framework_signals: Array<{ name: string; evidence_count: number }>;
    api_routes: Array<{ method: string; path: string; source: string; line?: string }>;
    outbound_api_calls: Array<{ client: string; target: string; source: string; evidence: string; line?: string }>;
    data_store_signals: Array<{ name: string; source: string; evidence: string; line?: string }>;
    modules: Array<{ path: string; language: string; lines: number; imports: number; role: string }>;
    dependency_edges: Array<{ from: string; to: string; kind: string }>;
    findings: Array<{ severity: string; title: string; detail: string }>;
    limitations: string[];
  };
};
type RepositoryArchitecture = {
  project_id: string; name: string; repository_url: string; default_branch: string;
  architecture_status: string; architecture_summary: string; technology_stack: string[];
  entrypoints: string[]; layers: ArchitectureLayer[]; state_and_data: string[];
  external_integrations: string[]; evidence_paths: string[]; limitations: string[];
  repository_hygiene_findings?: ArchitectureFinding[];
  source_snapshot: {
    commit: string | null; tree_sha?: string | null; commit_date?: string | null;
    source_checked_at?: string; deployment_verified: boolean; runtime_health_verified: boolean
  };
};

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
const portfolioDimensions: Array<{ key: PortfolioDimension; label: string }> = [
  { key: "business_model", label: "Business model" },
  { key: "system_type", label: "System" },
  { key: "sector", label: "Sector" },
  { key: "market_category", label: "Market" },
];
function dimensionValue(project: Project, dimension: PortfolioDimension) {
  return project[dimension]?.trim() || "Not classified";
}
function architectureSearchText(item: RepositoryArchitecture) {
  return [
    item.name,
    item.architecture_summary,
    item.technology_stack.join(" "),
    item.entrypoints.join(" "),
    item.layers.map((layer) => [layer.name, layer.role, layer.components, layer.evidence_paths.join(" ")].join(" ")).join(" "),
    item.state_and_data.join(" "),
    item.external_integrations.join(" "),
    item.evidence_paths.join(" "),
    item.limitations.join(" "),
    JSON.stringify(item.repository_hygiene_findings ?? []),
  ].join(" ").toLowerCase();
}
function architectureStatusLabel(status: string) {
  const labels: Record<string, string> = {
    "source-verified": "Source verified",
    "source-limited": "Source limited",
    "documentation-only": "Documentation only",
    "empty": "Empty repository",
  };
  return labels[status] || status.replaceAll("-", " ");
}

export default function App() {
  const [status, setStatus] = useState<RuntimeStatus | null>(null);
  const [events, setEvents] = useState<RuntimeEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const [busy, setBusy] = useState(false);
  const [command, setCommand] = useState("");
  const [output, setOutput] = useState("Runtime console ready. Enter help to see available commands.");
  const [lastUpdated, setLastUpdated] = useState("");
  const [projects, setProjects] = useState<Project[]>([]);
  const [ingestJobs, setIngestJobs] = useState<IngestJob[]>([]);
  const [inventoryProjects, setInventoryProjects] = useState<InventoryProject[]>([]);
  const [runtimeProjects, setRuntimeProjects] = useState<RuntimeProject[]>([]);
  const [hostingProjects, setHostingProjects] = useState<HostingProject[]>([]);
  const [runtimeActionBusy, setRuntimeActionBusy] = useState<string | null>(null);
  const [architectures, setArchitectures] = useState<RepositoryArchitecture[]>([]);
  const [architectureAnalyses, setArchitectureAnalyses] = useState<Record<string, ArchitectureAnalysis>>({});
  const [analyzingArchitecture, setAnalyzingArchitecture] = useState<string | null>(null);
  const [apiRelationshipMap, setApiRelationshipMap] = useState<ApiRelationshipMap | null>(null);
  const [apiRelationshipMapLoading, setApiRelationshipMapLoading] = useState(false);
  const [architectureSearch, setArchitectureSearch] = useState("");
  const [architectureStatusFilter, setArchitectureStatusFilter] = useState("all");
  const [ingesting, setIngesting] = useState<string | null>(null);
  const [projectMessage, setProjectMessage] = useState("");
  const [newProjectName, setNewProjectName] = useState("");
  const [newProjectCategory, setNewProjectCategory] = useState("new-project");
  const [newProjectDescription, setNewProjectDescription] = useState("");
  const [newProjectRepository, setNewProjectRepository] = useState("");
  const [registeringProject, setRegisteringProject] = useState(false);
  const [projectSearch, setProjectSearch] = useState("");
  const [hubSearch, setHubSearch] = useState("");
  const [portfolioDimension, setPortfolioDimension] = useState<PortfolioDimension>("business_model");
  const [portfolioGroupFilter, setPortfolioGroupFilter] = useState("");
  const [portfolioFilters, setPortfolioFilters] = useState<Record<PortfolioDimension, string>>({ business_model: "", system_type: "", sector: "", market_category: "" });
  const [portfolioSearch, setPortfolioSearch] = useState("");
  const [sourceQuery, setSourceQuery] = useState("");
  const [sourceResults, setSourceResults] = useState<SourceResult[]>([]);
  const [sourceSearching, setSourceSearching] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const responses = await Promise.all([
        fetch(API + "/api/status", { signal: AbortSignal.timeout(2500) }),
        fetch(API + "/api/events", { signal: AbortSignal.timeout(2500) }),
        fetch(API + "/api/repositories", { signal: AbortSignal.timeout(5000) }),
        fetch(API + "/api/project-inventory", { signal: AbortSignal.timeout(5000) }),
        fetch(API + "/api/ingest-status", { signal: AbortSignal.timeout(5000) }),
        fetch(API + "/api/runtime-projects", { signal: AbortSignal.timeout(5000) }),
        fetch(API + "/api/repository-architectures", { signal: AbortSignal.timeout(5000) }),
        fetch(API + "/api/hosting/projects", { signal: AbortSignal.timeout(5000) }),
      ]);
      if (!responses[0].ok || !responses[1].ok) throw new Error("Runtime API returned an error");
      const nextStatus = (await responses[0].json()) as RuntimeStatus;
      const nextEvents = (await responses[1].json()) as { events: RuntimeEvent[] };
      if (responses[2].ok) { const nextProjects = (await responses[2].json()) as { projects: Project[] }; setProjects(nextProjects.projects ?? []); }
      if (responses[3].ok) { const inventory = (await responses[3].json()) as { projects: InventoryProject[] }; setInventoryProjects(inventory.projects ?? []); }
      if (responses[4].ok) { const ingestStatus = (await responses[4].json()) as { jobs: IngestJob[] }; setIngestJobs(ingestStatus.jobs ?? []); }
      if (responses[5].ok) { const registry = (await responses[5].json()) as { projects: RuntimeProject[] }; setRuntimeProjects(registry.projects ?? []); }
      if (responses[6].ok) { const inventory = (await responses[6].json()) as { repositories: RepositoryArchitecture[] }; setArchitectures(inventory.repositories ?? []); }
      if (responses[7].ok) { const hosting = (await responses[7].json()) as HostingOverview; setHostingProjects(hosting.projects ?? []); }
      else { setHostingProjects([]); }
      setStatus(nextStatus);
      setEvents(nextEvents.events ?? []);
      setConnected(true);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch {
      setConnected(false);
      setStatus(null);
      setHostingProjects([]);
    }
  }, []);

  useEffect(() => {
    void refresh();
    const timer = window.setInterval(() => void refresh(), 5000);
    return () => window.clearInterval(timer);
  }, [refresh]);

  async function runRuntimeAction(projectId: string, action: "start" | "stop" | "restart") {
    if (runtimeActionBusy) return;
    setRuntimeActionBusy(projectId + ":" + action);
    setProjectMessage("");
    try {
      const response = await fetch(API + "/api/hosting/projects/" + encodeURIComponent(projectId) + "/" + action, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
        signal: AbortSignal.timeout(10000),
      });
      const data = (await response.json()) as { ok?: boolean; error?: string; state?: string };
      if (!response.ok || !data.ok) throw new Error(data.error || "Lifecycle action failed");
      await refresh();
      const readbackResponse = await fetch(API + "/api/hosting/projects", { signal: AbortSignal.timeout(5000) });
      if (!readbackResponse.ok) throw new Error("Action was accepted, but hosting state could not be verified.");
      const readback = (await readbackResponse.json()) as HostingOverview;
      setHostingProjects(readback.projects ?? []);
      const project = readback.projects?.find((item) => item.project_id === projectId);
      if (!project) throw new Error("Action was accepted, but the project is missing from the hosting read-back.");
      const actualState = project.hosting.state;
      const expectedState = action === "stop" ? "stopped" : "running";
      const verified = actualState === expectedState && (action === "stop" || project.hosting.health === "healthy");
      setProjectMessage(verified
        ? `${project.name}: ${action} verified — state ${actualState}${action === "stop" ? "." : `, health ${project.hosting.health}.`}`
        : `${project.name}: ${action} was accepted, but verification is incomplete — state ${actualState}, health ${project.hosting.health}.`);
    } catch (error) {
      setProjectMessage(projectId + ": " + (error instanceof Error ? error.message : "Lifecycle request failed"));
    } finally {
      setRuntimeActionBusy(null);
    }
  }

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

  async function registerProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!newProjectName.trim() || registeringProject) return;
    setRegisteringProject(true);
    setProjectMessage("Registering project identity…");
    try {
      const response = await fetch(API + "/api/project-inventory", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newProjectName.trim(), category: newProjectCategory.trim() || "new-project", description: newProjectDescription.trim(), repository_url: newProjectRepository.trim() }),
        signal: AbortSignal.timeout(10000),
      });
      const data = await response.json() as { ok?: boolean; project?: InventoryProject; error?: string };
      if (!response.ok || !data.ok) throw new Error(data.error ?? "Project registration failed");
      setNewProjectName(""); setNewProjectCategory("new-project"); setNewProjectDescription(""); setNewProjectRepository("");
      setProjectMessage((data.project?.name ?? "Project") + " registered. Repository matching and runtime adapter setup remain separate steps.");
      await refresh();
    } catch (error) { setProjectMessage("Project registration failed: " + (error instanceof Error ? error.message : "unknown error")); }
    finally { setRegisteringProject(false); }
  }
  async function indexProject(projectId: string, projectName: string) {
    if (ingesting) return;
    setIngesting(projectId);
    setProjectMessage("Indexing " + projectName + " from GitHub. Larger repositories can take several minutes.");
    try {
      const response = await fetch(API + "/api/repositories/ingest", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ project_id: projectId }), signal: AbortSignal.timeout(300000) });
      const data = await response.json() as { ok?: boolean; files_seen?: number; files_indexed?: number; files_skipped?: number; error?: string };
      if (!response.ok || !data.ok) throw new Error(data.error ?? "Repository indexing failed");
      setProjectMessage(projectName + " indexed: " + data.files_indexed + " text files stored, " + data.files_skipped + " excluded out of " + data.files_seen + " files.");
      await refresh();
      if (architectureAnalyses[projectId]) {
        setProjectMessage(projectName + " indexed. Refreshing its source architecture against the newly indexed commit…");
        await analyzeArchitecture(projectId, projectName);
      }
    } catch (error) { setProjectMessage("Indexing failed for " + projectName + ": " + (error instanceof Error ? error.message : "unknown error")); }
    finally { setIngesting(null); }
  }

  async function analyzeArchitecture(projectId: string, projectName: string) {
    if (analyzingArchitecture) return;
    setAnalyzingArchitecture(projectId);
    try {
      const response = await fetch(API + "/api/repositories/" + encodeURIComponent(projectId) + "/architecture-analysis", { signal: AbortSignal.timeout(30000) });
      const data = await response.json() as ArchitectureAnalysis & { error?: string };
      if (!response.ok || !data.ok) throw new Error(data.error ?? "Source architecture analysis failed");
      setArchitectureAnalyses((current) => ({ ...current, [projectId]: data }));
      setProjectMessage("Source analysis complete for " + projectName + ": " + data.analysis.source_files_analyzed + " files inspected, " + data.analysis.routes_detected + " route patterns and " + data.analysis.local_dependency_edges + " local dependency edges detected.");
    } catch (error) {
      setProjectMessage("Source analysis unavailable for " + projectName + ": " + (error instanceof Error ? error.message : "unknown error") + " Index the repository first if it has not been indexed.");
    } finally { setAnalyzingArchitecture(null); }
  }

  async function buildApiRelationshipMap() {
    if (apiRelationshipMapLoading) return;
    setApiRelationshipMapLoading(true);
    try {
      const response = await fetch(API + "/api/architecture/api-map", { signal: AbortSignal.timeout(120000) });
      const data = await response.json() as ApiRelationshipMap & { error?: string };
      if (!response.ok || !data.ok) throw new Error(data.error ?? "API relationship mapping failed");
      setApiRelationshipMap(data);
      setProjectMessage("API relationship scan complete: " + data.relationships.length + " static candidate relationships across " + data.repositories_analyzed + " indexed repositories.");
    } catch (error) {
      setProjectMessage("API relationship mapping failed: " + (error instanceof Error ? error.message : "unknown error") + ". Confirm the local runtime is updated and repositories are indexed.");
    } finally { setApiRelationshipMapLoading(false); }
  }

  async function searchSource(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (sourceQuery.trim().length < 2 || sourceSearching) return;
    setSourceSearching(true);
    try {
      const response = await fetch(API + "/api/search?q=" + encodeURIComponent(sourceQuery.trim()) + "&limit=50", { signal: AbortSignal.timeout(15000) });
      const data = await response.json() as { results?: SourceResult[]; error?: string };
      if (!response.ok) throw new Error(data.error ?? "Search failed");
      setSourceResults(data.results ?? []);
    } catch (error) { setProjectMessage("Source search failed: " + (error instanceof Error ? error.message : "unknown error")); }
    finally { setSourceSearching(false); }
  }

  async function indexAllProjects() {
    if (ingesting || !projects.length) return;
    setIngesting("ALL");
    let completed = 0;
    const failures: string[] = [];
    for (const project of projects) {
      setProjectMessage("Indexing project " + (completed + 1) + " of " + projects.length + ": " + project.name);
      try {
        const response = await fetch(API + "/api/repositories/ingest", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ project_id: project.project_id }), signal: AbortSignal.timeout(300000) });
        const data = await response.json() as { ok?: boolean; error?: string };
        if (!response.ok || !data.ok) throw new Error(data.error ?? "indexing failed");
        completed += 1;
      } catch (error) { failures.push(project.name + ": " + (error instanceof Error ? error.message : "unknown error")); }
    }
    await refresh();
    setProjectMessage("Bulk indexing finished. Successful: " + completed + " of " + projects.length + ". " + (failures.length ? "Failed: " + failures.join(" | ") : "No failures."));
    setIngesting(null);
  }

  const uptime = status ? formatUptime(status.uptime_seconds) : "—";
  const hubProjects = projects.filter((project) => [project.name, project.project_id, project.purpose, project.interface_kind, project.interface_status].some((value) => value?.toLowerCase().includes(hubSearch.trim().toLowerCase())));
  const configuredAdapterCount = runtimeProjects.filter((project) => project.adapter_type !== "unconfigured" && project.runtime_mode !== "not_configured").length;
  const sourceVerifiedCount = architectures.filter((item) => item.architecture_status === "source-verified").length;
  const portfolioGroups = projects.reduce<Record<string, Project[]>>((groups, project) => {
    const label = dimensionValue(project, portfolioDimension);
    (groups[label] ??= []).push(project);
    return groups;
  }, {});
  const sortedPortfolioGroups = Object.entries(portfolioGroups).sort((a, b) => b[1].length - a[1].length || a[0].localeCompare(b[0]));
  const maxGroupSize = Math.max(1, ...sortedPortfolioGroups.map(([, items]) => items.length));
  const activePortfolioGroup = portfolioGroupFilter ? (portfolioGroups[portfolioGroupFilter] ?? []) : [];
  const sectorCount = new Set(projects.map((project) => project.sector).filter((value): value is string => Boolean(value))).size;
  const marketCount = new Set(projects.map((project) => project.target_market).filter((value): value is string => Boolean(value))).size;
  const verifiedCommercialModels = projects.filter((project) => /verified|confirmed|pricing evidence|customer evidence|revenue evidence/i.test(project.monetization_status || "") && !/unverified|not verified|no confirmed|undefined|undocumented/i.test(project.monetization_status || "")).length;
  const filteredExecutiveProjects = projects.filter((project) => portfolioDimensions.every(({ key }) => !portfolioFilters[key] || dimensionValue(project, key) === portfolioFilters[key]) && (!portfolioSearch.trim() || [project.name, project.purpose, project.target_market, project.portfolio_role].some((value) => value?.toLowerCase().includes(portfolioSearch.trim().toLowerCase())))).sort((left, right) => left.name.localeCompare(right.name));
  const evidenceGapCount = projects.filter((project) => !project.market_validation || project.market_validation.toLowerCase().startsWith("unverified")).length;
  const unbuiltCount = projects.filter((project) => /empty|scaffold|concept|unverified|unvalidated/i.test((project.lifecycle_stage || "") + " " + (project.interface_status || ""))).length;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><Layers3 size={22} strokeWidth={2.2} /></div>
          <div><div className="brand-name">SysCentre<span>.</span></div><div className="brand-subtitle">SYSTEMS CONTROL PLANE</div></div>
        </div>
        <div className="workspace-label">WORKSPACE</div>
        <nav className="nav-list" aria-label="Main navigation">
          <a className="nav-item active" href="#hub"><Layers3 size={17} /><span>Project hub</span><ChevronRight className="nav-chevron" size={15} /></a>
          <a className="nav-item" href="#portfolio"><Gauge size={17} /><span>Executive portfolio</span></a>
          <a className="nav-item" href="#projects"><FolderGit2 size={17} /><span>Project registry</span></a>
          <a className="nav-item" href="#architectures"><Layers3 size={17} /><span>App architectures</span></a>
          <a className="nav-item" href="#runtime"><Cpu size={17} /><span>Runtime</span></a>
          <a className="nav-item" href="#runtime-adapters"><Zap size={17} /><span>Runtime adapters</span></a>
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
          <div className="breadcrumbs"><span>Workspace</span><ChevronRight size={14} /><strong>Executive portfolio</strong></div>
          <div className="topbar-right"><span className="local-badge"><span className="tiny-dot" /> LOCAL ENVIRONMENT</span><span className="topbar-divider" /><button className="icon-button" onClick={() => void refresh()} title="Refresh data" aria-label="Refresh data"><RefreshCw size={16} /></button><div className="topbar-avatar">SC</div></div>
        </header>

        <div className="page-wrap">
          <section className="page-heading">
            <div><div className="eyebrow"><span className="eyebrow-line" /> EXECUTIVE CONTROL PLANE / 001</div><h1>Executive portfolio</h1><p className="page-description">One decision layer across 28 independent systems: business-model hypotheses, system roles, sectors, and target markets.</p></div>
            <div className="heading-actions"><span className={"connection-pill " + (connected ? "connected" : "disconnected")}>{connected ? <Check size={14} /> : <WifiOff size={14} />}{connected ? "Runtime connected" : "Runtime unavailable"}</span><button className="secondary-button" onClick={() => void refresh()}><RefreshCw size={15} /> Refresh</button></div>
          </section>

          {!connected && <div className="connection-alert"><WifiOff size={18} /><div><strong>Runtime not detected</strong><p>Start the Python runtime to populate live system data. The dashboard will reconnect automatically.</p></div><code>python .\runtime\server.py</code></div>}

          <section className="panel projects-panel hub-panel" id="hub">
            <div className="panel-header"><div><div className="panel-kicker">UNIFIED PROJECT ACCESS</div><h2>Project hub</h2></div><span className="project-count">{projects.length} projects</span></div>
            <p className="panel-description">One entry point to every registered system. Open its source, inspect its architecture, index its code, and check whether a verified runtime adapter exists. A repository link is not a claim that the app is deployed or runnable.</p>
            <div className="hub-metrics">
              <article><span>Registered</span><strong>{projects.length}</strong><small>Canonical repositories</small></article>
              <article><span>Source-verified</span><strong>{sourceVerifiedCount}</strong><small>Architecture evidence found</small></article>
              <article><span>Runtime adapters configured</span><strong>{configuredAdapterCount}</strong><small>Does not imply health</small></article>
              <article><span>Deployment URLs verified</span><strong>0</strong><small>Not yet confirmed in this hub</small></article>
            </div>
            <div className="project-toolbar"><input className="project-filter" value={hubSearch} onChange={(event) => setHubSearch(event.target.value)} placeholder="Find any project by name, purpose or interface…" aria-label="Search project hub" /><span className="project-count">{hubProjects.length} shown</span></div>
            <div className="hub-project-grid">
              {hubProjects.map((project) => {
                const architecture = architectures.find((item) => item.project_id === project.project_id);
                const adapter = runtimeProjects.find((item) => item.project_id === project.project_id);
                const indexed = project.status !== "registered";
                const configured = Boolean(adapter && adapter.adapter_type !== "unconfigured" && adapter.runtime_mode !== "not_configured");
                return <article className="hub-project-card" key={project.project_id}>
                  <div className="hub-project-card-head"><div><strong>{project.name}</strong><span>{project.interface_kind || project.category || "Project"}</span></div><span className={"hub-state " + (configured ? "configured" : indexed ? "indexed" : "setup")}>{configured ? "Adapter configured" : indexed ? "Source indexed" : "Setup required"}</span></div>
                  <p>{project.purpose || "Purpose not yet documented in the canonical catalog."}</p>
                  <div className="hub-project-meta"><span>Architecture: {architecture ? architecture.architecture_status.replaceAll("-", " ") : "Unavailable"}</span><span>Interface: {project.interface_status || "Not verified"}</span></div>
                  <div className="hub-project-actions">
                    <a href={project.repository_url} target="_blank" rel="noreferrer">Open repository ↗</a>
                    {project.interface_source_url && <a href={project.interface_source_url} target="_blank" rel="noreferrer">Open UI source ↗</a>}
                    <a href={"#architectures"} onClick={() => { setArchitectureSearch(project.name); setArchitectureStatusFilter("all"); }}>Architecture ↗</a>
                    <button className="secondary-button project-index-button" disabled={ingesting !== null} onClick={() => void indexProject(project.project_id, project.name)}>{ingesting === project.project_id ? "Indexing…" : indexed ? "Re-index source" : "Index source"}</button>
                  </div>
                </article>;
              })}
              {!hubProjects.length && <div className="empty-state">No projects match this search.</div>}
            </div>
            <div className="project-disclaimer"><ShieldCheck size={14} /><span>Safety boundary: no arbitrary project code is executed from this hub. Launch controls remain disabled until a project-specific adapter and health check are verified.</span></div>
          </section>

          <section className="executive-portfolio" id="portfolio">
            <div className="portfolio-header">
              <div><div className="panel-kicker">PORTFOLIO INTELLIGENCE</div><h2>28 systems · one executive view</h2><p>Classify the portfolio by its intended business model, system function, sector, or target market. Values are planning classifications derived from repository evidence—not verified revenue, customers, or market validation.</p></div>
              <span className="portfolio-meta">CATALOG v2 · READ-ONLY</span>
            </div>
            <div className="portfolio-kpis">
              <article><span>Registered systems</span><strong>{projects.length || "—"}</strong><small>Independent repositories</small></article>
              <article><span>Sector coverage</span><strong>{sectorCount || "—"}</strong><small>Distinct sector groupings</small></article>
              <article><span>Target markets</span><strong>{marketCount || "—"}</strong><small>Market hypotheses, not TAM estimates</small></article>
              <article><span>Commercial evidence</span><strong>{verifiedCommercialModels}</strong><small>Pricing / customers / revenue verified</small></article>
            </div>
            <div className="portfolio-explorer panel">
              <div className="portfolio-explorer-head"><div><h3>Portfolio segmentation</h3><p>Switch dimension to regroup every repository using the catalog’s strategy metadata.</p></div><div className="portfolio-dimensions" role="group" aria-label="Portfolio segmentation dimension">
                {portfolioDimensions.map((dimension) => <button key={dimension.key} className={portfolioDimension === dimension.key ? "active" : ""} onClick={() => { setPortfolioDimension(dimension.key); setPortfolioGroupFilter(""); }}>{dimension.label}</button>)}
              </div></div>
              <div className="portfolio-group-grid">
                {sortedPortfolioGroups.map(([label, items]) => <button type="button" key={label} className={"portfolio-group-card " + (portfolioGroupFilter === label ? "selected" : "")} onClick={() => setPortfolioGroupFilter((current) => current === label ? "" : label)}>
                  <div className="portfolio-group-title"><strong>{label}</strong><span>{items.length.toString().padStart(2, "0")}</span></div>
                  <div className="portfolio-share-track"><span style={{ width: Math.max(6, Math.round(items.length / maxGroupSize * 100)) + "%" }} /></div>
                  <p>{items.slice(0, 3).map((project) => project.name).join(" · ")}{items.length > 3 ? " · +" + (items.length - 3) + " more" : ""}</p>
                  <small>{portfolioGroupFilter === label ? "Selected · click to clear" : "Select to drill into systems"}</small>
                </button>)}
                {!projects.length && <div className="empty-state portfolio-empty">Portfolio metadata will appear when the local runtime is connected.</div>}
              </div>
              {portfolioGroupFilter && <div className="portfolio-drilldown">
                <div className="portfolio-drilldown-head"><div><span className="panel-kicker">GROUP DRILL-DOWN</span><h3>{portfolioGroupFilter}</h3><p>{activePortfolioGroup.length} repository records · {portfolioDimensions.find((dimension) => dimension.key === portfolioDimension)?.label}</p></div><button className="text-button" onClick={() => setPortfolioGroupFilter("")}>Clear selection</button></div>
                <div className="portfolio-drilldown-grid">{activePortfolioGroup.map((project) => <article key={project.project_id}>
                  <div className="portfolio-drilldown-top"><strong>{project.name}</strong><span>{project.status.replaceAll("_", " ")}</span></div>
                  <p>{project.portfolio_role || "Role not classified"} · {project.lifecycle_stage || "Stage unverified"}</p>
                  <div className="portfolio-detail-line"><span>Sector</span><b>{project.sector || "Unclassified"}</b></div>
                  <div className="portfolio-detail-line"><span>Target market</span><b>{project.target_market || "Unclassified"}</b></div>
                  <a href={project.repository_url} target="_blank" rel="noreferrer">Open repository ↗</a>
                </article>)}</div>
              </div>}
            </div>
            <div className="portfolio-caveat"><ShieldCheck size={15} /><span><strong>Evidence boundary:</strong> business models and markets are hypotheses; pricing, customers, revenue, and geographic reach are not verified by this catalog. Projects remain separate and no runtime is controlled from this portfolio layer.</span></div>
            <section className="executive-register" aria-labelledby="executive-register-title">
              <div className="executive-register-heading">
                <div><div className="panel-kicker">DECISION SUPPORT</div><h3 id="executive-register-title">Executive portfolio register</h3><p>Apply all four lenses together to isolate a business line, system family, sector, or market. Use this register to identify what is built, what remains unverified, and where evidence is missing.</p></div>
                <span className="register-count">{filteredExecutiveProjects.length} / {projects.length} systems</span>
              </div>
              <div className="register-filters">
                <label className="register-search"><span>Search portfolio</span><input value={portfolioSearch} onChange={(event) => setPortfolioSearch(event.target.value)} placeholder="Name, purpose, role, target market…" /></label>
                {portfolioDimensions.map(({ key, label }) => {
                  const options = Array.from(new Set(projects.map((project) => dimensionValue(project, key)))).sort((left, right) => left.localeCompare(right));
                  return <label key={key}><span>{label}</span><select value={portfolioFilters[key]} onChange={(event) => setPortfolioFilters((current) => ({ ...current, [key]: event.target.value }))}><option value="">All {label.toLowerCase()}s</option>{options.map((option) => <option key={option} value={option}>{option}</option>)}</select></label>;
                })}
                <button className="secondary-button register-reset" onClick={() => { setPortfolioSearch(""); setPortfolioFilters({ business_model: "", system_type: "", sector: "", market_category: "" }); }}>Reset filters</button>
              </div>
              <div className="register-summary">
                <div><span>Market evidence gaps</span><strong>{evidenceGapCount}</strong><small>Market validation not verified</small></div>
                <div><span>Build / maturity review</span><strong>{unbuiltCount}</strong><small>Scaffolds, concepts, empty or unverified interfaces</small></div>
                <div><span>Commercial models evidenced</span><strong>{verifiedCommercialModels}</strong><small>Pricing, customers, or revenue evidence</small></div>
              </div>
              <div className="executive-register-list">
                {filteredExecutiveProjects.map((project) => <article className="executive-register-row" key={project.project_id}>
                  <div className="register-project-identity"><strong>{project.name}</strong><span>{project.portfolio_role || "Portfolio role not classified"}</span><a href={project.repository_url} target="_blank" rel="noreferrer">Open source repository ↗</a></div>
                  <div className="register-project-fields">
                    <div><span>Business model</span><strong>{project.business_model || "Not classified"}</strong></div>
                    <div><span>System</span><strong>{project.system_type || "Not classified"}</strong></div>
                    <div><span>Sector</span><strong>{project.sector || "Not classified"}</strong></div>
                    <div><span>Market category</span><strong>{project.market_category || "Not classified"}</strong></div>
                    <div><span>Target customer / market</span><strong>{project.target_market || "Not classified"}</strong></div>
                    <div><span>Lifecycle</span><strong>{project.lifecycle_stage || "Not verified"}</strong></div>
                    <div><span>Commercial evidence</span><strong>{project.monetization_status || "Not recorded"}</strong></div>
                  </div>
                  <div className="register-validation"><span className={project.market_validation && !project.market_validation.toLowerCase().startsWith("unverified") ? "evidence-confirmed" : "evidence-unverified"}>{project.market_validation && !project.market_validation.toLowerCase().startsWith("unverified") ? "Evidence recorded" : "Validation gap"}</span><p>{project.classification_basis || "Classification basis not recorded"}</p></div>
                </article>)}
                {!filteredExecutiveProjects.length && <div className="empty-state">No systems match the current combination of filters.</div>}
              </div>
            </section>
          </section>

          <section className="panel projects-panel" id="projects">
            <div className="panel-header"><div><div className="panel-kicker">PROJECT INTELLIGENCE</div><h2>Project registry</h2></div><button className="secondary-button project-index-button" disabled={ingesting !== null || projects.length === 0} onClick={() => void indexAllProjects()}>{ingesting === "ALL" ? "Indexing all..." : "Index all projects"}</button></div>
            <p className="panel-description">Independent repositories registered for indexing. Source remains in its own repository; indexing does not merge or execute project code.</p>
            <div className="project-toolbar"><input className="project-filter" value={projectSearch} onChange={(event) => setProjectSearch(event.target.value)} placeholder="Filter projects..." aria-label="Filter projects" /><span className="project-count">{projects.length} registered</span></div>
            {projectMessage && <div className="project-message" role="status">{projectMessage}</div>}
            {ingestJobs.some((job) => job.status === "running" || job.status === "failed") && <div className="ingest-progress-list" aria-live="polite">
              {ingestJobs.filter((job) => job.status === "running" || job.status === "failed").map((job) => {
                const percent = job.files_seen > 0 ? Math.min(100, Math.round(job.files_processed / job.files_seen * 100)) : 0;
                return <article className={"ingest-progress " + job.status} key={job.project_id}>
                  <div className="ingest-progress-top"><strong>{job.project_id}</strong><span>{job.status === "running" ? "Indexing" : "Interrupted — retry to resume"}</span></div>
                  <div className="ingest-progress-track"><span style={{ width: percent + "%" }} /></div>
                  <div className="ingest-progress-meta">{job.files_processed} / {job.files_seen} files checked · {job.files_indexed} text · {job.files_skipped} excluded</div>
                  {job.status === "failed" && <div className="ingest-progress-error">{job.error || "Indexing stopped unexpectedly. Retry to resume from saved checkpoints."}</div>}
                </article>;
              })}
            </div>}
            <form className="source-search" onSubmit={searchSource}><input value={sourceQuery} onChange={(event) => setSourceQuery(event.target.value)} placeholder="Search indexed source across projects..." aria-label="Search indexed source" /><button className="secondary-button project-index-button" type="submit" disabled={sourceSearching || sourceQuery.trim().length < 2}>{sourceSearching ? "Searching..." : "Search source"}</button></form>
            {sourceResults.length > 0 && <div className="source-results"><div className="source-results-heading">{sourceResults.length} source matches</div>{sourceResults.map((result, index) => <article className="source-result" key={result.project_id + result.path + index}><div><strong>{result.project_name}</strong><span>{result.path}</span></div><pre>{result.excerpt}</pre><a href={result.repository_url + "/blob/" + (projects.find((project) => project.project_id === result.project_id)?.default_branch ?? "main") + "/" + result.path} target="_blank" rel="noreferrer">Open source on GitHub</a></article>)}</div>}
            <div className="project-list">
              {projects.filter((project) => project.name.toLowerCase().includes(projectSearch.toLowerCase()) || project.project_id.includes(projectSearch.toLowerCase())).map((project) => (
                <article className="project-row" key={project.project_id}>
                  <div className="project-symbol"><Database size={17} /></div>
                  <div className="project-main"><strong>{project.name}</strong><a href={project.repository_url} target="_blank" rel="noreferrer">{project.repository_url.replace("https://github.com/", "")}</a><span>{project.status === "registered" ? "Registered · not indexed" : project.file_count + " files · " + project.text_file_count + " text indexed · " + project.skipped_file_count + " excluded"}</span></div>
                  <div className="project-actions"><span className={"project-status " + (project.status === "registered" ? "" : "indexed")}>{project.status.replaceAll("_", " ")}</span><button className="secondary-button project-index-button" disabled={ingesting !== null} onClick={() => void indexProject(project.project_id, project.name)}>{ingesting === project.project_id ? "Indexing..." : project.status === "registered" ? "Index repo" : "Re-index"}</button></div>
                </article>
              ))}
              {!projects.length && <div className="empty-state">Waiting for the local repository catalog...</div>}
            </div>
            <div className="project-disclaimer"><ShieldCheck size={14} /><span>Sensitive-looking paths, generated folders, binary files, and oversized files are excluded from the text index.</span></div>
          </section>

          <section className="panel architecture-panel" id="architectures">
            <div className="panel-header">
              <div><div className="panel-kicker">SOURCE-LEVEL SYSTEM MAP</div><h2>Application architectures</h2></div>
              <span className="project-count">{architectures.length} architecture records</span>
            </div>
            <p className="panel-description">Layer-by-layer architecture snapshots from each repository's actual tracked files, manifests and entrypoints. Expand a project to inspect its application boundaries, state layer, integrations and GitHub evidence.</p>
            <div className="architecture-kpis">
              <article><span>Source inspected</span><strong>{architectures.filter((item) => item.architecture_status === "source-verified").length}</strong><small>Entry points / implementation files found</small></article>
              <article><span>Partial implementation</span><strong>{architectures.filter((item) => item.architecture_status === "source-limited").length}</strong><small>Scaffold or missing evidence</small></article>
              <article><span>Documentation only</span><strong>{architectures.filter((item) => item.architecture_status === "documentation-only").length}</strong><small>Design described, code not found</small></article>
              <article><span>Empty repositories</span><strong>{architectures.filter((item) => item.architecture_status === "empty").length}</strong><small>No Git tree available</small></article>
            </div>
            <div className="architecture-toolbar">
              <input className="project-filter" value={architectureSearch} onChange={(event) => setArchitectureSearch(event.target.value)} placeholder="Search layers, integrations, data, components or paths..." aria-label="Search application architectures" />
              <select className="architecture-status-filter" value={architectureStatusFilter} onChange={(event) => setArchitectureStatusFilter(event.target.value)} aria-label="Filter architecture status">
                <option value="all">All source states</option>
                <option value="source-verified">Source verified</option>
                <option value="source-limited">Source limited</option>
                <option value="documentation-only">Documentation only</option>
                <option value="empty">Empty repository</option>
              </select>
              <span className="project-count">{architectures.filter((item) => (architectureStatusFilter === "all" || item.architecture_status === architectureStatusFilter) && architectureSearchText(item).includes(architectureSearch.toLowerCase())).length} shown</span>
            </div>
            <div className="architecture-analysis-actions">
              <button className="secondary-button project-index-button" disabled={apiRelationshipMapLoading} onClick={() => void buildApiRelationshipMap()}>{apiRelationshipMapLoading ? "Mapping indexed APIs…" : apiRelationshipMap ? "Refresh cross-repository API map" : "Build cross-repository API map"}</button>
              <span>Matches static outbound URLs to another indexed repository's configured API base URL and exact route. No network calls are made.</span>
            </div>
            {apiRelationshipMap && <section className="architecture-analysis-result" aria-label="Cross-repository API relationship map">
              <div className="architecture-analysis-heading"><div><strong>Cross-repository API relationships</strong><span>Static evidence only · {apiRelationshipMap.mode.replaceAll("-", " ")}</span></div><span>{apiRelationshipMap.repositories_analyzed} repositories analyzed</span></div>
              <div className="architecture-analysis-metrics">
                <article><span>Candidate links</span><strong>{apiRelationshipMap.relationships.length}</strong></article>
                <article><span>Repositories analyzed</span><strong>{apiRelationshipMap.repositories_analyzed}</strong></article>
                <article><span>Repositories skipped</span><strong>{apiRelationshipMap.repositories_skipped.length}</strong></article>
                <article><span>Unmatched outbound calls</span><strong>{apiRelationshipMap.unmatched_outbound_calls.length}</strong></article>
              </div>
              {apiRelationshipMap.relationships.length ? <div className="architecture-module-list">
                {apiRelationshipMap.relationships.map((relationship, index) => <div key={relationship.caller.project_id + relationship.provider.project_id + relationship.target + index}>
                  <strong>{relationship.caller.name}</strong><span>→</span><strong>{relationship.provider.name}</strong>
                  <code>{relationship.method} {relationship.route}</code>
                  <span>Target: {relationship.target}</span>
                  <span>Caller evidence: {relationship.caller_evidence}:{relationship.caller_line || "?"}</span>
                  <span>Provider evidence: {relationship.provider_evidence}:{relationship.provider_line || "?"}</span>
                  <span>{relationship.confidence.replaceAll("-", " ")}</span>
                  <a href={relationship.caller.repository_url + "/blob/" + relationship.caller.indexed_commit + "/" + relationship.caller_evidence + (relationship.caller_line ? "#L" + relationship.caller_line : "")} target="_blank" rel="noreferrer">Open caller evidence</a>
                  <a href={relationship.provider.repository_url + "/blob/" + relationship.provider.indexed_commit + "/" + relationship.provider_evidence + (relationship.provider_line ? "#L" + relationship.provider_line : "")} target="_blank" rel="noreferrer">Open provider evidence</a>
                </div>)}
              </div> : <div className="empty-state">No exact static API relationships were identified. This does not prove that repositories have no integrations; dynamic configuration and gateway routing may be invisible.</div>}
              {!!apiRelationshipMap.unmatched_outbound_calls.length && <details className="architecture-module-details">
                <summary>Outbound API targets without an exact repository match ({apiRelationshipMap.unmatched_outbound_calls.length})</summary>
                <div className="architecture-module-list">
                  {apiRelationshipMap.unmatched_outbound_calls.map((call, index) => <div key={call.caller.project_id + call.source + call.target + index}>
                    <strong>{call.caller.name}</strong><code>{call.client}</code><span>{call.target}</span><span>Evidence: {call.source}:{call.line || "?"}</span><span>{call.reason}</span>
                    <a href={call.caller.repository_url + "/blob/" + call.caller.indexed_commit + "/" + call.source + (call.line ? "#L" + call.line : "")} target="_blank" rel="noreferrer">Open caller evidence</a>
                  </div>)}
                </div>
              </details>}
              {!!apiRelationshipMap.repositories_skipped.length && <div className="architecture-analysis-findings"><strong>Repositories skipped</strong>{apiRelationshipMap.repositories_skipped.map((item) => <p key={item.project_id}>{item.name}: {item.reason}</p>)}</div>}
              <div className="architecture-analysis-limitations">{apiRelationshipMap.limitations.map((limitation) => <span key={limitation}>{limitation}</span>)}</div>
            </section>}
            <div className="architecture-list">
              {architectures.filter((item) => (architectureStatusFilter === "all" || item.architecture_status === architectureStatusFilter) && architectureSearchText(item).includes(architectureSearch.toLowerCase())).map((item) => (
                <details className="architecture-card" key={item.project_id}>
                  <summary>
                    <div className="architecture-identity"><strong>{item.name}</strong><span>{item.default_branch} · {item.layers.length} architecture layers</span></div>
                    <div className="architecture-stack">{item.technology_stack.slice(0, 4).map((technology) => <span key={technology}>{technology}</span>)}</div>
                    <span className={"architecture-status " + item.architecture_status}>{architectureStatusLabel(item.architecture_status)}</span>
                    <ChevronRight className="architecture-chevron" size={17} />
                  </summary>
                  <div className="architecture-detail">
                    <p className="architecture-summary">{item.architecture_summary}</p>
                    <div className="architecture-analysis-actions">
                      <button className="secondary-button project-index-button" disabled={analyzingArchitecture !== null} onClick={() => void analyzeArchitecture(item.project_id, item.name)}>{analyzingArchitecture === item.project_id ? "Analyzing indexed source…" : architectureAnalyses[item.project_id] ? "Refresh source analysis" : "Analyze indexed source"}</button>
                      <span>Read-only static analysis. Index this repository first; project code is never executed.</span>
                    </div>
                    {architectureAnalyses[item.project_id] && <section className="architecture-analysis-result" aria-label={"Static source analysis for " + item.name}>
                      <div className="architecture-analysis-heading"><div><strong>Static source analysis</strong><span>Indexed commit <code>{architectureAnalyses[item.project_id].project.indexed_commit.slice(0, 12) || "unknown"}</code></span></div><span>{architectureAnalyses[item.project_id].analysis.source_files_analyzed} text files</span></div>
                      <div className="architecture-analysis-metrics">
                        <article><span>Source lines</span><strong>{architectureAnalyses[item.project_id].analysis.lines_of_source.toLocaleString()}</strong></article>
                        <article><span>Imports</span><strong>{architectureAnalyses[item.project_id].analysis.imports_detected}</strong></article>
                        <article><span>Local dependencies</span><strong>{architectureAnalyses[item.project_id].analysis.local_dependency_edges}</strong></article>
                        <article><span>Routes detected</span><strong>{architectureAnalyses[item.project_id].analysis.routes_detected}</strong></article>
                        <article><span>Functions / classes</span><strong>{architectureAnalyses[item.project_id].analysis.functions_detected} / {architectureAnalyses[item.project_id].analysis.classes_detected}</strong></article>
                      </div>
                      <div className="architecture-analysis-grid">
                        <article><strong>Framework signals</strong>{architectureAnalyses[item.project_id].analysis.framework_signals.length ? architectureAnalyses[item.project_id].analysis.framework_signals.slice(0, 12).map((signal) => <span key={signal.name}>{signal.name} · {signal.evidence_count} signals</span>) : <span>No framework signals detected</span>}</article>
                        <article><strong>Entry points</strong>{architectureAnalyses[item.project_id].analysis.entrypoints.length ? architectureAnalyses[item.project_id].analysis.entrypoints.map((path) => <a key={path} href={item.repository_url + "/blob/" + (architectureAnalyses[item.project_id].project.indexed_commit || item.default_branch) + "/" + path} target="_blank" rel="noreferrer">{path}</a>) : <span>No conventional entrypoint identified</span>}</article>
                        <article><strong>Data-store signals</strong>{architectureAnalyses[item.project_id].analysis.data_store_signals.length ? architectureAnalyses[item.project_id].analysis.data_store_signals.slice(0, 12).map((signal, index) => <a key={signal.name + signal.source + index} href={item.repository_url + "/blob/" + (architectureAnalyses[item.project_id].project.indexed_commit || item.default_branch) + "/" + signal.source + (signal.line ? "#L" + signal.line : "")} target="_blank" rel="noreferrer">{signal.name} <small>· {signal.source}:{signal.line || "?"}</small></a>) : <span>No supported data-store patterns detected</span>}</article>
                        <article><strong>API / route patterns</strong>{architectureAnalyses[item.project_id].analysis.api_routes.length ? architectureAnalyses[item.project_id].analysis.api_routes.slice(0, 20).map((route, index) => <a key={route.method + route.path + route.source + index} href={item.repository_url + "/blob/" + (architectureAnalyses[item.project_id].project.indexed_commit || item.default_branch) + "/" + route.source + (route.line ? "#L" + route.line : "")} target="_blank" rel="noreferrer"><code>{route.method}</code> {route.path} <small>· {route.source}:{route.line || "?"}</small></a>) : <span>No supported route patterns detected</span>}</article>
                        <article><strong>Outbound API calls</strong>{architectureAnalyses[item.project_id].analysis.outbound_api_calls.length ? architectureAnalyses[item.project_id].analysis.outbound_api_calls.slice(0, 20).map((call, index) => <a key={call.client + call.target + call.source + index} href={item.repository_url + "/blob/" + (architectureAnalyses[item.project_id].project.indexed_commit || item.default_branch) + "/" + call.source + (call.line ? "#L" + call.line : "")} target="_blank" rel="noreferrer"><code>{call.client}</code> {call.target} <small>· {call.source}:{call.line || "?"}</small></a>) : <span>No supported outbound HTTP-client targets detected</span>}</article>
                      </div>
                      <details className="architecture-module-details"><summary>Module inventory ({architectureAnalyses[item.project_id].analysis.modules.length}) and dependency edges ({architectureAnalyses[item.project_id].analysis.dependency_edges.length})</summary>
                        <div className="architecture-module-list">{architectureAnalyses[item.project_id].analysis.modules.slice(0, 80).map((module) => <div key={module.path}><code>{module.path}</code><span>{module.role} · {module.lines} lines · {module.imports} imports</span></div>)}</div>
                        {architectureAnalyses[item.project_id].analysis.dependency_edges.length > 0 && <div className="architecture-edge-list">{architectureAnalyses[item.project_id].analysis.dependency_edges.slice(0, 100).map((edge, index) => <div key={edge.from + edge.to + index}><code>{edge.from}</code><span>→</span><code>{edge.to}</code></div>)}</div>}
                      </details>
                      {!!architectureAnalyses[item.project_id].analysis.findings.length && <div className="architecture-analysis-findings"><strong>Analysis notes</strong>{architectureAnalyses[item.project_id].analysis.findings.map((finding) => <p key={finding.title}>{finding.severity.toUpperCase()} · {finding.title}: {finding.detail}</p>)}</div>}
                      <div className="architecture-analysis-limitations">{architectureAnalyses[item.project_id].analysis.limitations.map((limitation) => <span key={limitation}>{limitation}</span>)}</div>
                    </section>}
                    <div className="architecture-detail-grid">
                      {item.layers.map((layer) => <article className="architecture-layer" key={layer.name}>
                        <span>{layer.name}</span><strong>{layer.role}</strong><p>{layer.components}</p>
                        {layer.evidence_paths.length > 0 && <div className="architecture-paths">{layer.evidence_paths.map((path) => <a key={path} href={item.repository_url + "/blob/" + (item.source_snapshot.commit ?? item.default_branch) + "/" + path} target="_blank" rel="noreferrer">{path}</a>)}</div>}
                      </article>)}
                    </div>
                    <div className="architecture-metadata-grid">
                      <article><strong>Application entrypoints</strong>{item.entrypoints.length ? item.entrypoints.map((path) => <a key={path} href={item.repository_url + "/blob/" + (item.source_snapshot.commit ?? item.default_branch) + "/" + path} target="_blank" rel="noreferrer">{path}</a>) : <span>None verified</span>}</article>
                      <article><strong>State and data</strong>{item.state_and_data.length ? item.state_and_data.map((value) => <span key={value}>{value}</span>) : <span>Not confirmed from the inspected source</span>}</article>
                      <article><strong>External integrations</strong>{item.external_integrations.length ? item.external_integrations.map((value) => <span key={value}>{value}</span>) : <span>No integration verified</span>}</article>
                      <article><strong>Evidence files</strong>{item.evidence_paths.slice(0, 10).map((path) => <a key={path} href={item.repository_url + "/blob/" + (item.source_snapshot.commit ?? item.default_branch) + "/" + path} target="_blank" rel="noreferrer">{path}</a>)}</article>
                    </div>
                    <div className="architecture-snapshot">
                      <span>Source commit: <code>{item.source_snapshot.commit ? item.source_snapshot.commit.slice(0, 12) : "No Git commit"}</code></span>
                      {item.source_snapshot.tree_sha && <span>Tree SHA: <code>{item.source_snapshot.tree_sha.slice(0, 12)}</code></span>}
                      <span>Commit date: {item.source_snapshot.commit_date ? item.source_snapshot.commit_date.slice(0, 10) : "No commit"}</span>
                      <span>Inventory checked: {item.source_snapshot.source_checked_at || "Unknown"}</span>
                      {item.source_snapshot.commit && <a href={item.repository_url + "/commit/" + item.source_snapshot.commit} target="_blank" rel="noreferrer">View inspected commit ↗</a>}
                      <span>Deployment verified: No</span><span>Runtime health verified: No</span>
                    </div>
                    {!!item.repository_hygiene_findings?.length && <div className="architecture-hygiene">
                      <div className="architecture-hygiene-heading"><strong>Repository hygiene findings</strong><span>Path metadata only · no file contents copied</span></div>
                      <div className="architecture-hygiene-list">
                        {item.repository_hygiene_findings.map((finding, index) => <article className={"architecture-hygiene-finding severity-" + finding.severity} key={finding.category + finding.title + index}>
                          <div className="architecture-hygiene-title"><span className={"hygiene-severity severity-" + finding.severity}>{finding.severity}</span><strong>{finding.title}</strong><span className="hygiene-category">{finding.category.replaceAll("-", " ")}</span></div>
                          <p>{finding.description}</p>
                          {finding.evidence_paths.length > 0 && <div className="architecture-paths">{finding.evidence_paths.map((path) => <a key={path} href={item.repository_url + "/blob/" + (item.source_snapshot.commit ?? item.default_branch) + "/" + path} target="_blank" rel="noreferrer">{path}</a>)}</div>}
                          <div className="hygiene-recommendation"><strong>Recommended action:</strong> {finding.recommended_action}</div>
                        </article>)}
                      </div>
                    </div>}
                    {item.limitations.length > 0 && <div className="architecture-limitations"><strong>Gaps / caveats</strong>{item.limitations.map((note) => <p key={note}>{note}</p>)}</div>}
                  </div>
                </details>
              ))}
              {!architectures.length && <div className="empty-state">Architecture inventory unavailable. Pull the latest SysCentre changes and restart the local runtime.</div>}
              {architectures.length > 0 && !architectures.some((item) => (architectureStatusFilter === "all" || item.architecture_status === architectureStatusFilter) && architectureSearchText(item).includes(architectureSearch.toLowerCase())) && <div className="empty-state">No application architecture matches this filter.</div>}
            </div>
            <div className="project-disclaimer"><ShieldCheck size={14} /><span>Snapshot-based architecture is not a live health check. Empty and README-only repositories remain explicitly unimplemented; integration declarations are not proof of active connections.</span></div>
          </section>

          <section className="panel projects-panel intake-panel" id="project-intake">
            <div className="panel-header"><div><div className="panel-kicker">PORTFOLIO EXPANSION</div><h2>Register a new project</h2></div><span className="project-count">Extensible registry</span></div>
            <p className="panel-description">Add a project created here or elsewhere without changing the existing 28 repositories. Registration records the project identity; it does not claim the code exists, map an unverified repository, or execute anything.</p>
            <form className="project-intake-form" onSubmit={registerProject}>
              <label><span>Project name *</span><input required maxLength={120} value={newProjectName} onChange={(event) => setNewProjectName(event.target.value)} placeholder="e.g. AI Appointment Setter SaaS" /></label>
              <label><span>System category</span><input maxLength={60} value={newProjectCategory} onChange={(event) => setNewProjectCategory(event.target.value)} placeholder="ai-platform, finance, security…" /></label>
              <label className="intake-wide"><span>Purpose / description</span><textarea maxLength={1000} value={newProjectDescription} onChange={(event) => setNewProjectDescription(event.target.value)} placeholder="What should this project do? Keep it concise." rows={2} /></label>
              <label className="intake-wide"><span>GitHub repository URL (optional)</span><input type="url" value={newProjectRepository} onChange={(event) => setNewProjectRepository(event.target.value)} placeholder="https://github.com/owner/repository" /></label>
              <div className="intake-actions"><button className="secondary-button project-index-button" type="submit" disabled={registeringProject || !newProjectName.trim()}>{registeringProject ? "Registering…" : "Add to project inventory"}</button><span>New entries require repository verification and an execution adapter before they can be run.</span></div>
            </form>
          </section>
          <section className="panel projects-panel runtime-adapters-panel" id="runtime-adapters">
            <div className="panel-header"><div><div className="panel-kicker">EXECUTION READINESS</div><h2>Project hosting</h2></div><span className="project-count">{hostingProjects.filter((project) => project.hosting.configured).length} / {hostingProjects.length} configured</span></div>
            <p className="panel-description">Live hosting data comes from the project-hosting subsystem. Runtime connectivity, launch readiness, process state and health are shown separately. Actions are only reported as verified after reading the resulting state back from the runtime.</p>
            <div className="runtime-adapter-list">
              {hostingProjects.map((project) => {
                const hosting = project.hosting;
                const configured = hosting.configured;
                const ready = hosting.ready;
                const running = hosting.state === "running";
                const canStart = hosting.available_actions.includes("start") && !running;
                const canStop = hosting.available_actions.includes("stop") && running;
                const canRestart = hosting.available_actions.includes("restart");
                const statusClass = hosting.health === "healthy" ? "configured" : hosting.health === "unhealthy" ? "unconfigured" : "";
                return <article className="runtime-adapter-row" key={project.project_id}>
                  <div className="runtime-adapter-name"><strong>{project.name}</strong><span>{project.project_id} · {hosting.adapter_type}</span></div>
                  <div className="runtime-adapter-context"><span>{hosting.workspace || "Workspace not provisioned"}</span><span title={hosting.readiness_reason || undefined}>{hosting.readiness_reason || (ready ? "Required paths verified" : "Readiness not verified")}</span></div>
                  <span className={"runtime-adapter-status " + (ready ? "configured" : "unconfigured")}>{!configured ? "Not configured" : ready ? "Ready to launch" : "Setup required"}</span>
                  <span className={"runtime-adapter-status " + statusClass} title={hosting.healthcheck_url || undefined}>{hosting.state.replaceAll("_", " ")} · {hosting.health}</span>
                  <div className="runtime-adapter-actions">
                    <button className="secondary-button" type="button" disabled={!canStart || Boolean(runtimeActionBusy)} onClick={() => void runRuntimeAction(project.project_id, "start")}>{runtimeActionBusy === project.project_id + ":start" ? "Starting…" : "Start"}</button>
                    <button className="secondary-button" type="button" disabled={!canStop || Boolean(runtimeActionBusy)} onClick={() => void runRuntimeAction(project.project_id, "stop")}>{runtimeActionBusy === project.project_id + ":stop" ? "Stopping…" : "Stop"}</button>
                    <button className="secondary-button" type="button" disabled={!canRestart || Boolean(runtimeActionBusy)} onClick={() => void runRuntimeAction(project.project_id, "restart")}>{runtimeActionBusy === project.project_id + ":restart" ? "Restarting…" : "Restart"}</button>
                  </div>
                  {running && hosting.url && <a href={hosting.url} target="_blank" rel="noreferrer">Open app ↗</a>}
                  {project.repository_url && <a href={project.repository_url} target="_blank" rel="noreferrer">Source ↗</a>}
                </article>;
              })}
              {!hostingProjects.length && <div className="empty-state">Hosting data unavailable. Confirm the local runtime is updated and reachable.</div>}
            </div>
            {projectMessage && <p className="panel-description" role="status">{projectMessage}</p>}
          </section>
          {inventoryProjects.length > 0 && <section className="panel projects-panel inventory-panel" id="inventory-audit">
            <div className="panel-header"><div><div className="panel-kicker">INVENTORY RECONCILIATION</div><h2>Historical projects awaiting repository match</h2></div><span className="project-count">{inventoryProjects.length} unresolved</span></div>
            <p className="panel-description">These project identities were found in the historical project inventory but do not have a confirmed, exact repository mapping yet. Candidate repositories are suggestions only; SysCentre will not index them as these projects until the match is confirmed.</p>
            <div className="project-list">
              {inventoryProjects.map((project) => <article className="project-row" key={project.id}>
                <div className="project-symbol"><FolderGit2 size={17} /></div>
                <div className="project-main"><strong>{project.name}</strong><span>{project.category.replaceAll("-", " ")}</span><span>{project.candidate_repositories.length ? "Possible matches: " + project.candidate_repositories.join(", ") : "No candidate repository identified"}</span></div>
                <div className="project-actions"><span className="project-status">match required</span></div>
              </article>)}
            </div>
          </section>}

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
            <div className="panel-header"><div><div className="panel-kicker">TRUST BOUNDARY</div><h2>Policy & execution controls</h2></div><span className={"policy-status " + (status?.policy_gate === "enabled" ? "configured" : "unconfigured")}><ShieldCheck size={14} /> {status?.policy_gate === "enabled" ? "POLICY GATE ENABLED" : "POLICY GATE STATUS UNVERIFIED"}</span></div>
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
