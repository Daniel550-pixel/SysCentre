#Requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("localhost-webapp", "networklab")]
    [string]$ProjectId,
    [string]$RuntimeBaseUrl = "http://127.0.0.1:8765",
    [ValidateRange(1, 60)]
    [int]$StartupTimeoutSeconds = 15
)

$ErrorActionPreference = "Stop"
$RuntimeBaseUrl = $RuntimeBaseUrl.TrimEnd("/")
$HealthUrls = @{
    "localhost-webapp" = "http://127.0.0.1:4180/"
    "networklab"       = "http://127.0.0.1:8501/healthz"
}
$LifecycleUrl = "$RuntimeBaseUrl/api/runtime-projects/$ProjectId"

function Invoke-LifecycleAction {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("start", "stop", "restart")]
        [string]$Action
    )
    $Response = Invoke-RestMethod -Uri "$LifecycleUrl/$Action" -Method Post -ContentType "application/json" -Body "{}" -TimeoutSec 5
    Write-Host ("{0}: {1}" -f $Action.ToUpperInvariant(), ($Response | ConvertTo-Json -Compress))
    return $Response
}

function Wait-ForProjectHealth {
    param([int]$TimeoutSeconds)
    $Deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $LastError = "Health endpoint has not responded yet."
    do {
        try {
            $Response = Invoke-WebRequest -Uri $HealthUrls[$ProjectId] -UseBasicParsing -TimeoutSec 2
            if ([int]$Response.StatusCode -ge 200 -and [int]$Response.StatusCode -lt 400) {
                Write-Host ("HEALTHY: {0} returned HTTP {1}" -f $HealthUrls[$ProjectId], $Response.StatusCode) -ForegroundColor Green
                return
            }
            $LastError = "Health endpoint returned HTTP $($Response.StatusCode)."
        } catch {
            $LastError = $_.Exception.Message
        }
        Start-Sleep -Milliseconds 500
    } while ((Get-Date) -lt $Deadline)
    throw "Project '$ProjectId' did not become healthy within $TimeoutSeconds seconds. Last result: $LastError. Inspect ~/.syscentre/logs/$ProjectId.log."
}

# Do not disrupt a session that was started outside this test.
try {
    $Sessions = Invoke-RestMethod -Uri "$RuntimeBaseUrl/api/runtime-sessions" -Method Get -TimeoutSec 5
} catch {
    throw "Cannot reach SysCentre runtime at $RuntimeBaseUrl. Start SysCentre first. Details: $($_.Exception.Message)"
}
$Existing = @($Sessions.sessions | Where-Object { $_.project_id -eq $ProjectId -and $_.state -eq "running" })
if ($Existing.Count -gt 0) {
    throw "Project '$ProjectId' is already running. The smoke test will not stop or restart an existing session."
}

$StartedByTest = $false
try {
    Write-Host "Testing SysCentre lifecycle for '$ProjectId'..."
    $null = Invoke-LifecycleAction -Action start
    $StartedByTest = $true
    Wait-ForProjectHealth -TimeoutSeconds $StartupTimeoutSeconds
    $null = Invoke-LifecycleAction -Action restart
    Wait-ForProjectHealth -TimeoutSeconds $StartupTimeoutSeconds
    $null = Invoke-LifecycleAction -Action stop
    $StartedByTest = $false

    $FinalSessions = Invoke-RestMethod -Uri "$RuntimeBaseUrl/api/runtime-sessions" -Method Get -TimeoutSec 5
    $Final = @($FinalSessions.sessions | Where-Object { $_.project_id -eq $ProjectId }) | Select-Object -First 1
    if ($Final -and $Final.state -eq "running") {
        throw "Lifecycle API reported the project as running after stop."
    }
    Write-Host "PASS: start, HTTP health, restart, HTTP health, and stop completed." -ForegroundColor Green
} finally {
    if ($StartedByTest) {
        try {
            $null = Invoke-LifecycleAction -Action stop
            Write-Host "Cleanup: stop requested for the test-owned session." -ForegroundColor Yellow
        } catch {
            Write-Warning "Cleanup could not stop '$ProjectId'. Check SysCentre runtime sessions and the project log. $($_.Exception.Message)"
        }
    }
}
