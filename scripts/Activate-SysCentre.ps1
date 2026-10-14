[CmdletBinding()]
param(
    [switch]$NoBrowser,
    [switch]$NoGitWatcher,
    [switch]$AutoCommitSync,
    [int]$SyncIntervalSeconds = 60
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$WebRoot = Join-Path $ProjectRoot "webapp"
$RuntimeScript = Join-Path $ProjectRoot "runtime\server.py"
$GitSyncScript = Join-Path $PSScriptRoot "SysCentre-GitSync.ps1"
$PackageLock = Join-Path $WebRoot "package-lock.json"

function Require-Command {
    param([Parameter(Mandatory = $true)][string]$Name, [Parameter(Mandatory = $true)][string]$InstallHint)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name was not found on PATH. $InstallHint Install it, reopen PowerShell, and rerun this script."
    }
}

function Invoke-GitChecked {
    param([Parameter(Mandatory = $true)][string[]]$GitArgs)
    & git @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Git command failed (exit $LASTEXITCODE): git $($GitArgs -join ' ')"
    }
}

function Test-Listener {
    param([int]$Port)
    return [bool](Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1)
}

Write-Host ""
Write-Host "SYS CENTRE | ACTIVATE LOCAL ENVIRONMENT" -ForegroundColor Cyan
Write-Host "Repository: $ProjectRoot" -ForegroundColor DarkGray

Require-Command -Name "git.exe" -InstallHint "Install Git for Windows."
Require-Command -Name "node.exe" -InstallHint "Install Node.js 20 or newer."
Require-Command -Name "npm.cmd" -InstallHint "Install Node.js 20 or newer (includes npm)."

$Python = Get-Command python.exe -ErrorAction SilentlyContinue
if (-not $Python) { $Python = Get-Command python -ErrorAction SilentlyContinue }
if (-not $Python) { throw "Python 3.11 or newer was not found on PATH. Install Python and reopen PowerShell." }

$pythonVersionText = & $Python.Source --version 2>&1
if ($LASTEXITCODE -ne 0 -or $pythonVersionText -notmatch "Python\s+(\d+)\.(\d+)") {
    throw "Unable to determine Python version: $pythonVersionText"
}
$pythonMajor = [int]$Matches[1]
$pythonMinor = [int]$Matches[2]
if (($pythonMajor -lt 3) -or ($pythonMajor -eq 3 -and $pythonMinor -lt 11)) {
    throw "SysCentre requires Python 3.11+. Found: $pythonVersionText"
}

$nodeVersionText = & node.exe --version
if ($LASTEXITCODE -ne 0 -or $nodeVersionText -notmatch "^v(\d+)\.") {
    throw "Unable to determine Node.js version: $nodeVersionText"
}
if ([int]$Matches[1] -lt 20) { throw "SysCentre requires Node.js 20+. Found: $nodeVersionText" }

foreach ($requiredPath in @($RuntimeScript, (Join-Path $WebRoot "package.json"), $GitSyncScript)) {
    if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
        throw "Required SysCentre file is missing: $requiredPath"
    }
}

Push-Location $ProjectRoot
try {
    $branch = (& git branch --show-current).Trim()
    if ($LASTEXITCODE -ne 0 -or $branch -ne "main") {
        throw "Current branch is '$branch', not 'main'. Switch to main before activation; this script will not change branches."
    }

    $origin = (& git remote get-url origin 2>$null)
    if ($LASTEXITCODE -ne 0 -or -not $origin) { throw "Git remote 'origin' is not configured." }
    if ($origin -notmatch "Daniel550-pixel/SysCentre(?:\.git)?$") {
        throw "Unexpected origin remote: $origin. Expected Daniel550-pixel/SysCentre; no Git sync was attempted."
    }

    $dirty = @(& git status --porcelain)
    if ($LASTEXITCODE -ne 0) { throw "Could not read Git status." }
    if ($dirty.Count -gt 0) {
        Write-Host "Local working tree is not clean. Activation stopped before pull/rebase to protect local work." -ForegroundColor Yellow
        $dirty | ForEach-Object { Write-Host "  $_" }
        throw "Commit or safely stash/review these changes, then rerun activation."
    }

    Write-Host "[1/5] Checking GitHub access and refreshing main..." -ForegroundColor Cyan
    Invoke-GitChecked -GitArgs @("ls-remote", "origin", "refs/heads/main")
    Invoke-GitChecked -GitArgs @("pull", "--rebase", "origin", "main")

    Write-Host "[2/5] Installing locked webapp dependencies with npm ci..." -ForegroundColor Cyan
    Push-Location $WebRoot
    try {
        if (Test-Path -LiteralPath $PackageLock -PathType Leaf) {
            & npm.cmd ci
        } else {
            Write-Host "No package-lock.json found; using npm install." -ForegroundColor Yellow
            & npm.cmd install
        }
        if ($LASTEXITCODE -ne 0) { throw "Webapp dependency installation failed (exit $LASTEXITCODE)." }
    } finally { Pop-Location }

    Write-Host "[3/5] Building webapp to validate installed dependencies..." -ForegroundColor Cyan
    Push-Location $WebRoot
    try {
        & npm.cmd run build
        if ($LASTEXITCODE -ne 0) { throw "Webapp build failed (exit $LASTEXITCODE). Resolve build errors before continuing." }
    } finally { Pop-Location }

    Write-Host "[4/5] Starting runtime and webapp..." -ForegroundColor Cyan
    if (-not (Test-Listener -Port 8765) -or -not (Test-Listener -Port 5173)) {
        $startArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $PSScriptRoot "Start-SysCentre.ps1"), "-NoBrowser")
        Start-Process -FilePath "powershell.exe" -ArgumentList $startArgs -WorkingDirectory $ProjectRoot
    } else {
        Write-Host "Both service ports already have listeners; duplicate startup skipped." -ForegroundColor DarkGray
    }

    $runtimeReady = $false
    $webReady = $false
    for ($i = 0; $i -lt 20; $i++) {
        Start-Sleep -Seconds 1
        try {
            $runtimeResponse = Invoke-WebRequest -Uri "http://127.0.0.1:8765/api/health" -UseBasicParsing -TimeoutSec 2
            if ($runtimeResponse.StatusCode -ge 200 -and $runtimeResponse.StatusCode -lt 300) { $runtimeReady = $true }
        } catch {
            try {
                $runtimeResponse = Invoke-WebRequest -Uri "http://127.0.0.1:8765/api/status" -UseBasicParsing -TimeoutSec 2
                if ($runtimeResponse.StatusCode -ge 200 -and $runtimeResponse.StatusCode -lt 300) { $runtimeReady = $true }
            } catch { }
        }
        try {
            $webResponse = Invoke-WebRequest -Uri "http://127.0.0.1:5173" -UseBasicParsing -TimeoutSec 2
            if ($webResponse.StatusCode -ge 200 -and $webResponse.StatusCode -lt 300) { $webReady = $true }
        } catch { }
        if ($runtimeReady -and $webReady) { break }
    }

    if ($runtimeReady) { Write-Host "Runtime health check: PASS" -ForegroundColor Green }
    else { Write-Host "Runtime health check: NOT CONFIRMED. Check port 8765 and its terminal." -ForegroundColor Yellow }
    if ($webReady) { Write-Host "Webapp HTTP check: PASS" -ForegroundColor Green }
    else { Write-Host "Webapp HTTP check: NOT CONFIRMED. Check port 5173 and its terminal." -ForegroundColor Yellow }

    Write-Host "[5/5] Git push/pull watcher..." -ForegroundColor Cyan
    if (-not $NoGitWatcher) {
        $watchArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $GitSyncScript, "-RepoPath", $ProjectRoot, "-IntervalSeconds", $SyncIntervalSeconds, "-Watch")
        if ($AutoCommitSync) { $watchArgs += "-AutoCommit" }
        Start-Process -FilePath "powershell.exe" -ArgumentList $watchArgs -WorkingDirectory $ProjectRoot
        Write-Host "Dedicated Git sync terminal opened (interval: $SyncIntervalSeconds seconds)." -ForegroundColor Green
        if ($AutoCommitSync) {
            Write-Host "Auto-commit is ENABLED. Review this choice carefully: local changes can be committed and pushed automatically." -ForegroundColor Yellow
        } else {
            Write-Host "Auto-commit remains OFF. Dirty working trees are protected; no force-push is used." -ForegroundColor DarkGray
        }
    } else {
        Write-Host "Git watcher skipped by -NoGitWatcher." -ForegroundColor DarkGray
    }
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "Activation sequence finished." -ForegroundColor Green
Write-Host "Dashboard : http://127.0.0.1:5173"
Write-Host "Runtime   : http://127.0.0.1:8765/api/status"
Write-Host "Git sync  : dedicated PowerShell window (unless skipped)"
if (-not $NoBrowser) { Start-Process "http://127.0.0.1:5173" }
