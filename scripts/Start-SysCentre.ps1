[CmdletBinding()]
param(
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$RuntimeScript = Join-Path $ProjectRoot "runtime\server.py"
$WebRoot = Join-Path $ProjectRoot "webapp"
$PackageFile = Join-Path $WebRoot "package.json"
$NodeModules = Join-Path $WebRoot "node_modules"

Write-Host ""
Write-Host "  SYS CENTRE  |  LOCAL SYSTEMS CONTROL PLANE" -ForegroundColor Cyan
Write-Host "  ------------------------------------------" -ForegroundColor DarkGray

$Python = Get-Command python.exe -ErrorAction SilentlyContinue
if (-not $Python) { $Python = Get-Command python -ErrorAction SilentlyContinue }
if (-not $Python) { throw "Python was not found. Install Python 3.11+ and reopen PowerShell." }

$Node = Get-Command node.exe -ErrorAction SilentlyContinue
$Npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (-not $Node -or -not $Npm) { throw "Node.js/npm was not found. Install Node.js 20+ and reopen PowerShell." }
if (-not (Test-Path $RuntimeScript)) { throw "Runtime script not found: $RuntimeScript" }
if (-not (Test-Path $PackageFile)) { throw "Webapp package file not found: $PackageFile" }

if (-not (Test-Path $NodeModules)) {
    Write-Host "[1/3] Installing webapp dependencies..." -ForegroundColor Yellow
    Push-Location $WebRoot
    try {
        & $Npm.Source install
        if ($LASTEXITCODE -ne 0) { throw "npm install failed with exit code $LASTEXITCODE" }
    }
    finally { Pop-Location }
} else {
    Write-Host "[1/3] Webapp dependencies already installed." -ForegroundColor DarkGray
}

$RuntimeListener = Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue
if (-not $RuntimeListener) {
    Write-Host "[2/3] Starting SysCentre runtime on 127.0.0.1:8765..." -ForegroundColor Cyan
    Start-Process -FilePath $Python.Source -ArgumentList ('"' + $RuntimeScript + '"') -WorkingDirectory $ProjectRoot
} else {
    Write-Host "[2/3] Port 8765 already has a listener; runtime startup skipped." -ForegroundColor DarkGray
}

$WebListener = Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue
if (-not $WebListener) {
    Write-Host "[3/3] Starting SysCentre webapp on 127.0.0.1:5173..." -ForegroundColor Cyan
    Start-Process -FilePath $env:ComSpec -ArgumentList ('/c npm --prefix "' + $WebRoot + '" run dev') -WorkingDirectory $ProjectRoot
} else {
    Write-Host "[3/3] Port 5173 already has a listener; webapp startup skipped." -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "SysCentre startup requested." -ForegroundColor Green
Write-Host "Dashboard : http://127.0.0.1:5173"
Write-Host "Runtime   : http://127.0.0.1:8765/api/status"
Write-Host "Tests     : python -m unittest discover -s runtime -p test_server.py -v"
if (-not $NoBrowser) {
    Start-Sleep -Seconds 2
    Start-Process "http://127.0.0.1:5173"
}
