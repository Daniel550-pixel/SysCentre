#Requires -Version 5.1
<#
.SYNOPSIS
    Interactive, safety-first Git push/pull terminal for SysCentre.
.DESCRIPTION
    Run from any directory inside the SysCentre repository. Supports status,
    fetch, fast-forward-only pull, push, pull+push sync, and an explicit
    stage/commit/push workflow. It never force-pushes, resets, or discards work.
.EXAMPLE
    .\scripts\Start-SysCentreGitTerminal.ps1
#>
[CmdletBinding()]
param(
    [string]$RepositoryPath = ''
)

$ErrorActionPreference = 'Stop'

function Write-Heading {
    param([string]$Text)
    Write-Host ''
    Write-Host ('=' * 64) -ForegroundColor DarkCyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host ('=' * 64) -ForegroundColor DarkCyan
}

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)][string[]]$GitArgs,
        [switch]$AllowFailure
    )
    & git -C $script:RepoRoot @GitArgs
    $code = $LASTEXITCODE
    if ($code -ne 0 -and -not $AllowFailure) {
        throw "Git command failed (exit $code): git $($GitArgs -join ' ')"
    }
    if ($AllowFailure) { return $code }
}

function Get-CurrentBranch {
    # Capture the native exit code immediately; a PowerShell pipeline can obscure it.
    $branch = & git -C $script:RepoRoot branch --show-current 2>$null
    $gitExitCode = $LASTEXITCODE
    if ($gitExitCode -ne 0 -or [string]::IsNullOrWhiteSpace(($branch -join '').Trim())) {
        throw 'HEAD is detached or Git could not resolve the current branch. Run: git status --short --branch'
    }
    return ($branch -join '').Trim()
}

function Test-WorkingTreeClean {
    $null = & git -C $script:RepoRoot diff --quiet
    $trackedDiff = $LASTEXITCODE -ne 0
    $null = & git -C $script:RepoRoot diff --cached --quiet
    $stagedDiff = $LASTEXITCODE -ne 0
    $untracked = @(& git -C $script:RepoRoot ls-files --others --exclude-standard)
    return (-not $trackedDiff -and -not $stagedDiff -and $untracked.Count -eq 0)
}

function Show-Status {
    Write-Heading 'Repository status'
    $branch = Get-CurrentBranch
    Write-Host "Repository : $script:RepoRoot"
    Write-Host "Branch     : $branch"
    $remote = & git -C $script:RepoRoot remote get-url origin 2>$null
    $remoteExitCode = $LASTEXITCODE
    $remoteText = ($remote -join '').Trim()
    if ($remoteExitCode -eq 0 -and -not [string]::IsNullOrWhiteSpace($remoteText)) {
        Write-Host "Origin     : $remoteText"
    } else {
        Write-Host 'Origin     : not configured' -ForegroundColor Yellow
    }
    Write-Host ''
    Invoke-Git -GitArgs @('status', '--short', '--branch')
    Write-Host ''
    Invoke-Git -GitArgs @('log', '-5', '--oneline', '--decorate')
}

function Assert-SyncPreconditions {
    $null = Invoke-Git -GitArgs @('remote', 'get-url', 'origin')
    $null = Get-CurrentBranch
}

function Invoke-Pull {
    Assert-SyncPreconditions
    if (-not (Test-WorkingTreeClean)) {
        throw 'Pull cancelled: the working tree has local changes. Commit or safely stash them first; this terminal will not alter them.'
    }
    Write-Host 'Fetching remote updates...' -ForegroundColor Cyan
    Invoke-Git -GitArgs @('fetch', 'origin', '--prune')
    $branch = Get-CurrentBranch
    $upstream = (& git -C $script:RepoRoot rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>$null | Select-Object -First 1)
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($upstream)) {
        throw "No upstream is configured for '$branch'. Use Push to publish this branch and set its upstream."
    }
    Write-Host "Fast-forward-only pull from $upstream..." -ForegroundColor Cyan
    Invoke-Git -GitArgs @('pull', '--ff-only')
    Write-Host 'Pull completed.' -ForegroundColor Green
}

function Invoke-Push {
    Assert-SyncPreconditions
    $branch = Get-CurrentBranch
    $upstream = (& git -C $script:RepoRoot rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>$null | Select-Object -First 1)
    if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($upstream)) {
        Invoke-Git -GitArgs @('push')
    } else {
        Write-Host "Branch '$branch' has no upstream. It will be published to origin/$branch." -ForegroundColor Yellow
        $answer = Read-Host 'Continue? (y/N)'
        if ($answer -notin @('y', 'Y', 'yes', 'YES')) {
            Write-Host 'Push cancelled.'
            return
        }
        Invoke-Git -GitArgs @('push', '--set-upstream', 'origin', $branch)
    }
    Write-Host 'Push completed.' -ForegroundColor Green
}

function Invoke-Sync {
    Write-Heading 'Pull then push'
    Invoke-Pull
    Invoke-Push
    Write-Host 'Sync completed. No force operations were used.' -ForegroundColor Green
}

function Invoke-CommitAndPush {
    Write-Heading 'Stage, commit, and push'
    Invoke-Git -GitArgs @('status', '--short')
    Write-Host ''
    $answer = Read-Host 'Stage ALL tracked and untracked changes with git add -A? (y/N)'
    if ($answer -notin @('y', 'Y', 'yes', 'YES')) {
        Write-Host 'No files were staged.'
        return
    }
    Invoke-Git -GitArgs @('add', '-A')
    Invoke-Git -GitArgs @('status', '--short')
    $message = Read-Host 'Commit message'
    if ([string]::IsNullOrWhiteSpace($message)) {
        throw 'Commit cancelled: a non-empty commit message is required. Changes remain staged.'
    }
    Write-Host ''
    Invoke-Git -GitArgs @('diff', '--cached', '--stat')
    $confirm = Read-Host "Create commit '$message' and push branch '$((Get-CurrentBranch))'? (y/N)"
    if ($confirm -notin @('y', 'Y', 'yes', 'YES')) {
        Write-Host 'Commit/push cancelled. Staged changes were left intact.'
        return
    }
    Invoke-Git -GitArgs @('commit', '-m', $message)
    Invoke-Push
}

# Resolve the repository root and verify the Git CLI before showing the menu.
if ([string]::IsNullOrWhiteSpace($RepositoryPath)) {
    $RepositoryPath = Join-Path $PSScriptRoot '..'
}
$resolvedPath = (Resolve-Path -LiteralPath $RepositoryPath).Path
$root = (& git -C $resolvedPath rev-parse --show-toplevel 2>$null | Select-Object -First 1)
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($root)) {
    throw "The specified path is not inside a Git repository: $resolvedPath"
}
$script:RepoRoot = $root.Trim()

try {
    $null = Invoke-Git -GitArgs @('--version')
} catch {
    throw 'Git is unavailable. Install Git for Windows and reopen PowerShell.'
}

while ($true) {
    Write-Heading 'SYSCENTRE | Git push / pull terminal'
    Write-Host "Repo: $script:RepoRoot" -ForegroundColor Gray
    Write-Host '  1. Status and recent commits'
    Write-Host '  2. Pull updates (fast-forward only)'
    Write-Host '  3. Push current branch'
    Write-Host '  4. Sync (pull, then push)'
    Write-Host '  5. Stage + commit + push (confirmation required)'
    Write-Host '  6. Fetch remote updates only'
    Write-Host '  0. Exit'
    $choice = Read-Host 'Choose an action'
    try {
        switch ($choice) {
            '1' { Show-Status }
            '2' { Invoke-Pull }
            '3' { Invoke-Push }
            '4' { Invoke-Sync }
            '5' { Invoke-CommitAndPush }
            '6' {
                Assert-SyncPreconditions
                Invoke-Git -GitArgs @('fetch', 'origin', '--prune')
                Write-Host 'Fetch completed; local files were not changed.' -ForegroundColor Green
            }
            '0' { return }
            default { Write-Host 'Unknown option. Choose 0-6.' -ForegroundColor Yellow }
        }
    } catch {
        Write-Host ''
        Write-Host "ACTION FAILED: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host 'Your local files were not reset or discarded by this tool.' -ForegroundColor DarkYellow
    }
    if ($choice -ne '0') {
        Write-Host ''
        [void](Read-Host 'Press Enter to return to the menu')
    }
}
