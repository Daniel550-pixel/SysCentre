param(
    [string]$RepoPath = (Split-Path -Parent $PSScriptRoot),
    [int]$IntervalSeconds = 60,
    [switch]$Watch,
    [switch]$AutoCommit,
    [string]$CommitMessage = "Automated SysCentre checkpoint"
)

$ErrorActionPreference = "Stop"

function Invoke-Git {
    param([string[]]$GitArgs)
    & git @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Git command failed: git $($GitArgs -join ' ')"
    }
}

if (-not (Get-Command git.exe -ErrorAction SilentlyContinue)) {
    throw "Git is not installed or git.exe is not on PATH."
}
if (-not (Test-Path -LiteralPath $RepoPath -PathType Container)) {
    throw "Repository folder not found: $RepoPath"
}

Set-Location -LiteralPath $RepoPath

$insideRepo = & git rev-parse --is-inside-work-tree 2>$null
if ($LASTEXITCODE -ne 0 -or $insideRepo -ne "true") {
    throw "The selected folder is not a Git repository: $RepoPath"
}

$branch = (& git branch --show-current).Trim()
if ($branch -ne "main") {
    throw "Current branch is '$branch', not 'main'. Switch to main before using this sync helper."
}

$origin = & git remote get-url origin 2>$null
if ($LASTEXITCODE -ne 0 -or -not $origin) {
    throw "Remote 'origin' is not configured."
}

function Sync-SysCentre {
    Write-Host ""
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] SysCentre sync check" -ForegroundColor Cyan

    $changes = @(& git status --porcelain)
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to read Git status."
    }

    if ($changes.Count -gt 0) {
        if (-not $AutoCommit) {
            Write-Host "Local changes detected. Skipping pull/push to protect your work." -ForegroundColor Yellow
            Write-Host "Review changes, or restart with -AutoCommit if automatic commits are intended."
            return
        }

        Invoke-Git -GitArgs @("add", "-A")
        & git diff --cached --quiet
        $diffExit = $LASTEXITCODE
        if ($diffExit -eq 1) {
            $message = "$CommitMessage - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
            Invoke-Git -GitArgs @("commit", "-m", $message)
        } elseif ($diffExit -ne 0) {
            throw "Unable to inspect staged changes."
        }
    }

    # Rebase local commits onto the latest remote main. Never force-push.
    Invoke-Git -GitArgs @("fetch", "origin", "main")
    & git pull --rebase origin main
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Pull/rebase stopped. Resolve the Git issue manually; sync will not push." -ForegroundColor Red
        throw "Pull/rebase failed. No push was attempted."
    }

    Invoke-Git -GitArgs @("push", "origin", "main")
    Write-Host "Sync complete." -ForegroundColor Green
}

if ($IntervalSeconds -lt 15) {
    throw "IntervalSeconds must be at least 15 to avoid excessive GitHub requests."
}

if (-not $Watch) {
    Sync-SysCentre
    exit 0
}

Write-Host "Watching SysCentre every $IntervalSeconds seconds. Press Ctrl+C to stop." -ForegroundColor Green
if ($AutoCommit) {
    Write-Host "Auto-commit is ON: all repository changes may be committed and pushed automatically." -ForegroundColor Yellow
} else {
    Write-Host "Auto-commit is OFF: local edits block sync until the working tree is clean." -ForegroundColor Cyan
}

while ($true) {
    try {
        Sync-SysCentre
    } catch {
        Write-Host "Sync paused after error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Fix the issue, then restart the script. No force-push is ever used." -ForegroundColor Yellow
        break
    }
    Start-Sleep -Seconds $IntervalSeconds
}
