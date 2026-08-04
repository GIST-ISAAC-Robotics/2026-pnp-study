[CmdletBinding()]
param(
    [string]$Distro = 'Ubuntu-24.04',
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$logDirectory = Join-Path $env:LOCALAPPDATA 'PnPStudy'
$logPath = Join-Path $logDirectory 'wsl-time-sync.log'

New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null

function Write-SyncLog {
    param([string]$Message)
    $line = '{0:o} {1}' -f (Get-Date), $Message
    Add-Content -LiteralPath $logPath -Value $line -Encoding utf8
    Write-Output $line
}

$runningDistros = @(
    & wsl.exe --list --running --quiet 2>$null |
        ForEach-Object { ($_ -replace "`0", '').Trim() } |
        Where-Object { $_ }
)

if (-not $Force -and $runningDistros -notcontains $Distro) {
    Write-SyncLog "SKIP distro=$Distro reason=not-running"
    exit 0
}

if ($Force -and $runningDistros -notcontains $Distro) {
    & wsl.exe -d $Distro -u root -- true
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to start WSL distro $Distro"
    }
}

# The WSL-specific timesyncd instance applied a competing frequency correction
# on this machine. Keep it stopped and align the shared WSL clock to Windows.
& wsl.exe -d $Distro -u root -- systemctl stop systemd-timesyncd.service
if ($LASTEXITCODE -ne 0) {
    throw 'Failed to stop systemd-timesyncd in WSL'
}

# Compensate for the short wsl.exe launch delay without requiring another NTP
# client inside WSL. A sub-500 ms local alignment is the ROS/Zenoh requirement.
$targetMilliseconds = [DateTimeOffset]::UtcNow.AddMilliseconds(100).ToUnixTimeMilliseconds()
$seconds = [math]::Floor($targetMilliseconds / 1000)
$milliseconds = $targetMilliseconds % 1000
$unixTimestamp = '{0}.{1:D3}' -f $seconds, $milliseconds

& wsl.exe -d $Distro -u root -- date --utc "--set=@$unixTimestamp" | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Failed to set WSL time for $Distro"
}

Write-SyncLog "SYNCED distro=$Distro target_epoch=$unixTimestamp"
