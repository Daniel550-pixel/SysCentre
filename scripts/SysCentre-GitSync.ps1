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

# Capture native stdout/stderr without letting PowerShell 5.1's
# ErrorActionPreference turn ordinary Git messages into terminating errors.
function Invoke-GitCapture {
    param([Parameter(Mandatory = $true)][string[]]$GitArgs)

    $previousPreference = $ErrorActionPreference
    $output = @()
    $exitCode = 1
    try {
        $ErrorActionPreference = "Continue"
        $output = @(& git @GitArgs 2>&1 | ForEach-Object { $_.ToString() })
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
    }

    return [pscustomobject]@{
        ExitCode = [int]$exitCode
        Output = [string[]]$output
        Command = "git $($GitArgs -join ' ')"
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
if ($LASTEXITCODE -ne 0 -or $branch -ne "main") {
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

    # The remote may change between pull and push. Always rebase first,
    # and retry only stale/non-fast-forward pushes. Never force-push.
    $maxPushAttempts = 4
    for ($attempt = 1; $attempt -le $maxPushAttempts; $attempt++) {
        $pull = Invoke-GitCapture -GitArgs @("pull", "--rebase", "origin", "main")
        foreach ($line in $pull.Output) {
            Write-Host $line
        }
        if ($pull.ExitCode -ne 0) {
            Write-Host "Pull/rebase stopped. Resolve the Git issue manually; no push was attempted." -ForegroundColor Red
            throw "Pull/rebase failed with exit code $($pull.ExitCode). Check for conflicts or a rebase in progress."
        }

        $push = Invoke-GitCapture -GitArgs @("push", "origin", "main")
        foreach ($line in $push.Output) {
            Write-Host $line
        }

        # Git reports success for both a real push and 'Everything up-to-date'.
        if ($push.ExitCode -eq 0) {
            Write-Host "Sync complete." -ForegroundColor Green
            return
        }

        $pushText = $push.Output -join "`n"
        $isRemoteRace = $pushText -match "(?i)(\[rejected\]|non-fast-forward|fetch first|failed to push some refs|stale info)"
        if (-not $isRemoteRace) {
            throw "git push failed with exit code $($push.ExitCode). Review the output above. No force-push was attempted."
        }

        if ($attempt -ge $maxPushAttempts) {
            throw "origin/main kept changing during push after $maxPushAttempts attempts. Sync stopped safely; no force-push was attempted."
        }

        Write-Host "origin/main changed during the push window. Refreshing and rebasing before retry $($attempt + 1) of $maxPushAttempts..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
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
