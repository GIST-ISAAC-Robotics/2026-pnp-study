#Requires -RunAsAdministrator

# Host-specific recovery helper. Review the peer list and interval before reuse.

[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$backupRoot = Join-Path $env:ProgramData 'PnPStudy\time-sync-backups'
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backupPath = Join-Path $backupRoot "W32Time-$timestamp.reg"
$ntpClientPath = 'HKLM:\SYSTEM\CurrentControlSet\Services\W32Time\TimeProviders\NtpClient'
$peerList = 'time.windows.com,0x9 time.cloudflare.com,0x9 time.google.com,0x9'

New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null

& reg.exe export 'HKLM\SYSTEM\CurrentControlSet\Services\W32Time' $backupPath /y | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Failed to back up W32Time registry configuration to $backupPath"
}

Set-Service -Name W32Time -StartupType Automatic

& w32tm.exe /config "/manualpeerlist:$peerList" /syncfromflags:manual /update
if ($LASTEXITCODE -ne 0) {
    throw 'w32tm peer configuration failed'
}

Set-ItemProperty -LiteralPath $ntpClientPath -Name SpecialPollInterval -Type DWord -Value 1024

Restart-Service -Name W32Time -Force
Start-Sleep -Seconds 3

& w32tm.exe /config /update
if ($LASTEXITCODE -ne 0) {
    throw 'w32tm configuration reload failed'
}

& w32tm.exe /resync /rediscover
if ($LASTEXITCODE -ne 0) {
    Start-Sleep -Seconds 5
    & w32tm.exe /resync /rediscover
    if ($LASTEXITCODE -ne 0) {
        throw 'W32Time resynchronization failed twice'
    }
}

Write-Output "BACKUP=$backupPath"
Write-Output "PEERS=$peerList"
Write-Output 'SPECIAL_POLL_INTERVAL_SECONDS=1024'
Get-Service -Name W32Time | Select-Object Name, Status, StartType
& w32tm.exe /query /status /verbose
