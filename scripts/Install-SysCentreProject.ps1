[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("localhost-webapp")]
    [string]$ProjectId,
    [switch]$InstallDependencies
)

$ErrorActionPreference = "Stop"
$WorkspaceRoot = if ($env:SYSCENTRE_WORKSPACES) {
    [System.IO.Path]::GetFullPath($env:SYSCENTRE_WORKSPACES)
} else {
    Join-Path $HOME ".syscentre\workspaces"
}
$Workspace = Join-Path $WorkspaceRoot $ProjectId

$Projects = @{
    "localhost-webapp" = @{
        Repository = "https://github.com/Daniel550-pixel/Localhost-webapp.git"
        Branch = "main"
        PackageName = "localhost-webapp"
    }
}

function Require-Command {
    param([Parameter(Mandatory = $true)][string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' is not available on PATH."
    }
}

Require-Command "git.exe"
if ($InstallDependencies) {
    Require-Command "node.exe"
    Require-Command "npm.cmd"
    $NodeVersion = (& node.exe --version).Trim()
    if ($LASTEXITCODE -ne 0 -or $NodeVersion -notmatch "^v(\d+)\.(\d+)\.(\d+)") {
        throw "Could not determine Node.js version."
    }
    $NodeMajor = [int]$Matches[1]
    $NodeMinor = [int]$Matches[2]
    if (($NodeMajor -lt 20) -or ($NodeMajor -eq 20 -and $NodeMinor -lt 9)) {
        throw "Localhost-webapp requires Node.js 20.9 or newer. Found $NodeVersion."
    }
}

$Project = $Projects[$ProjectId]
New-Item -ItemType Directory -Path $WorkspaceRoot -Force | Out-Null

if (-not (Test-Path -LiteralPath $Workspace)) {
    Write-Host "Cloning $ProjectId into isolated workspace: $Workspace" -ForegroundColor Cyan
    & git.exe clone --depth 1 --branch $Project.Branch $Project.Repository $Workspace
    if ($LASTEXITCODE -ne 0) { throw "Git clone failed for $ProjectId (exit $LASTEXITCODE)." }
} else {
    if (-not (Test-Path -LiteralPath (Join-Path $Workspace ".git") -PathType Container)) {
        throw "Workspace exists but is not a Git checkout. Nothing was overwritten: $Workspace"
    }
    $Origin = (& git.exe -C $Workspace remote get-url origin).Trim()
    if ($LASTEXITCODE -ne 0) { throw "Could not read the existing workspace Git remote." }
    # Compare normalized URLs without changing the existing remote.
    $NormalizedExpected = $Project.Repository -replace "\.git$", ""
    $NormalizedOrigin = $Origin -replace "\.git$", ""
    if ($NormalizedOrigin -ne $NormalizedExpected) {
        throw "Existing workspace has an unexpected Git remote: $Origin"
    }
    Write-Host "Existing verified checkout found; no pull or reset was performed." -ForegroundColor Yellow
}

$PackagePath = Join-Path $Workspace "package.json"
$LockPath = Join-Path $Workspace "package-lock.json"
if (-not (Test-Path -LiteralPath $PackagePath -PathType Leaf) -or -not (Test-Path -LiteralPath $LockPath -PathType Leaf)) {
    throw "Expected package.json and package-lock.json are missing. Project is not ready for Node provisioning."
}
$Package = Get-Content -LiteralPath $PackagePath -Raw | ConvertFrom-Json
if ($Package.name -ne $Project.PackageName) {
    throw "Unexpected package name '$($Package.name)'; expected '$($Project.PackageName)'."
}

if ($InstallDependencies) {
    Write-Host "Installing locked dependencies with npm ci. npm lifecycle scripts may execute." -ForegroundColor Yellow
    Push-Location $Workspace
    try {
        & npm.cmd ci
        if ($LASTEXITCODE -ne 0) { throw "npm ci failed (exit $LASTEXITCODE)." }
    } finally { Pop-Location }
} else {
    Write-Host "Dependencies were not installed. Re-run with -InstallDependencies after reviewing the repository." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Workspace ready: $Workspace" -ForegroundColor Green
Write-Host "SysCentre can manage this project at http://127.0.0.1:4180 after dependencies are installed."
