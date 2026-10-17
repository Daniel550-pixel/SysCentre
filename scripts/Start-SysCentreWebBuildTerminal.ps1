#Requires -Version 5.1
[CmdletBinding()]
param([string]$RepositoryPath = '')

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($RepositoryPath)) { $RepositoryPath = Join-Path $PSScriptRoot '..' }
$repo = (Resolve-Path -LiteralPath $RepositoryPath).Path
$webapp = Join-Path $repo 'webapp'
if (-not (Test-Path -LiteralPath (Join-Path $webapp 'package.json'))) { throw "Could not find webapp/package.json under: $repo" }

function Show-Heading {
    param([string]$Text)
    Write-Host ''
    Write-Host ('=' * 68) -ForegroundColor DarkCyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host ('=' * 68) -ForegroundColor DarkCyan
}
function Show-NodeProcesses {
    Show-Heading 'Active Node.js processes'
    $processes = @(Get-CimInstance Win32_Process -Filter "Name = 'node.exe'" -ErrorAction SilentlyContinue)
    if ($processes.Count -eq 0) { Write-Host 'No node.exe processes found.' -ForegroundColor Green; return }
    $processes | Select-Object ProcessId, ParentProcessId, CommandLine | Format-List
    Write-Host 'Only stop a process if you recognize it as a SysCentre/Vite process.' -ForegroundColor Yellow
    $rawPid = Read-Host 'Enter one PID to stop, or press Enter to leave all processes running'
    if ([string]::IsNullOrWhiteSpace($rawPid)) { return }
    $targetPid = 0
    if (-not [int]::TryParse($rawPid, [ref]$targetPid)) { Write-Host 'Invalid PID; no process was stopped.' -ForegroundColor Yellow; return }
    $target = $processes | Where-Object { $_.ProcessId -eq $targetPid } | Select-Object -First 1
    if (-not $target) { Write-Host 'That PID was not in the displayed list. Nothing was stopped.' -ForegroundColor Yellow; return }
    Write-Host "Selected PID: $($target.ProcessId)" -ForegroundColor Yellow
    Write-Host "Command: $($target.CommandLine)"
    $confirm = Read-Host 'Stop this exact process? Type STOP to confirm'
    if ($confirm -cne 'STOP') { Write-Host 'Cancelled; process remains running.'; return }
    Stop-Process -Id $target.ProcessId -ErrorAction Stop
    Write-Host "Stopped Node.js process $($target.ProcessId)." -ForegroundColor Green
}
function Invoke-NpmCommand {
    param([Parameter(Mandatory=$true)][string[]]$Arguments, [Parameter(Mandatory=$true)][string]$Description)
    Show-Heading $Description
    Push-Location $webapp
    try {
        Write-Host "Working directory: $webapp" -ForegroundColor Gray
        & npm @Arguments
        $exitCode = $LASTEXITCODE
        if ($exitCode -eq 0) { Write-Host ""; Write-Host "SUCCESS: $Description completed." -ForegroundColor Green }
        else {
            Write-Host ""; Write-Host "FAILED: $Description (exit code $exitCode)." -ForegroundColor Red
            if ($Description -like '*install*') {
                Write-Host 'If this is EPERM on esbuild.exe, inspect active Node.js processes (menu option 1).' -ForegroundColor Yellow
                Write-Host 'Close only the identified SysCentre/Vite process, then retry. Do not delete package-lock.json.' -ForegroundColor Yellow
            }
            if ($Description -like '*build*') { Write-Host 'If tsc is missing, dependency installation did not complete successfully.' -ForegroundColor Yellow }
        }
        return $exitCode
    } finally { Pop-Location }
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { throw 'npm was not found. Install/repair Node.js, then reopen PowerShell.' }

while ($true) {
    Show-Heading 'SYSCENTRE | Web Build Repair Terminal'
    Write-Host "Repository : $repo" -ForegroundColor Gray
    Write-Host "Web app    : $webapp" -ForegroundColor Gray
    Write-Host '  1. Inspect Node.js processes (optionally stop one selected PID)'
    Write-Host '  2. Install dependencies (npm ci)'
    Write-Host '  3. Build frontend (npm run build)'
    Write-Host '  4. Full cycle (inspect -> npm ci -> build)'
    Write-Host '  5. Repeat install/build cycle'
    Write-Host '  0. Exit'
    $choice = Read-Host 'Choose an action'
    try {
        switch ($choice) {
            '1' { Show-NodeProcesses }
            '2' { [void](Invoke-NpmCommand -Arguments @('ci') -Description 'Dependency install (npm ci)') }
            '3' { [void](Invoke-NpmCommand -Arguments @('run','build') -Description 'Frontend build (npm run build)') }
            '4' {
                Show-NodeProcesses
                $installCode = Invoke-NpmCommand -Arguments @('ci') -Description 'Dependency install (npm ci)'
                if ($installCode -eq 0) { [void](Invoke-NpmCommand -Arguments @('run','build') -Description 'Frontend build (npm run build)') }
                else { Write-Host 'Build skipped because npm ci failed.' -ForegroundColor Yellow }
            }
            '5' {
                do {
                    Show-NodeProcesses
                    $installCode = Invoke-NpmCommand -Arguments @('ci') -Description 'Dependency install (npm ci)'
                    if ($installCode -eq 0) { $buildCode = Invoke-NpmCommand -Arguments @('run','build') -Description 'Frontend build (npm run build)' }
                    else { $buildCode = 1; Write-Host 'Build skipped because npm ci failed.' -ForegroundColor Yellow }
                    if ($installCode -eq 0 -and $buildCode -eq 0) { Write-Host 'Full cycle succeeded.' -ForegroundColor Green; break }
                    $retry = Read-Host 'Cycle failed. Retry after resolving the issue? (y/N)'
                } while ($retry -in @('y','Y','yes','YES'))
            }
            '0' { break }
            default { Write-Host 'Choose one of the listed options.' -ForegroundColor Yellow }
        }
    } catch { Write-Host ""; Write-Host "ACTION FAILED: $($_.Exception.Message)" -ForegroundColor Red }
    if ($choice -eq '0') { break }
    [void](Read-Host 'Press Enter to return to the menu')
}
