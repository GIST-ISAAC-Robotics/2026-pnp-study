[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$TaskName = 'PnP-WSL-Time-Sync',
    [string]$SyncScriptPath = (Join-Path $PSScriptRoot 'sync-running-wsl-time.ps1'),
    [ValidateRange(0, 300)]
    [int]$DelaySeconds = 30
)

$ErrorActionPreference = 'Stop'

$resolvedScriptPath = (Resolve-Path -LiteralPath $SyncScriptPath).Path
$powershellPath = Join-Path $PSHOME 'powershell.exe'
$taskArguments = '-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "{0}"' -f $resolvedScriptPath
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

$eventSubscription = @'
<QueryList>
  <Query Id="0" Path="System">
    <Select Path="System">*[System[Provider[@Name='Microsoft-Windows-Power-Troubleshooter'] and EventID=1]]</Select>
  </Query>
</QueryList>
'@

$triggerClass = Get-CimClass -Namespace 'Root/Microsoft/Windows/TaskScheduler' -ClassName 'MSFT_TaskEventTrigger'
$trigger = New-CimInstance -CimClass $triggerClass -ClientOnly
$trigger.Enabled = $true
$trigger.Subscription = $eventSubscription
if ($DelaySeconds -gt 0) {
    $trigger.Delay = [System.Xml.XmlConvert]::ToString([TimeSpan]::FromSeconds($DelaySeconds))
}

$action = New-ScheduledTaskAction -Execute $powershellPath -Argument $taskArguments
$principalParameters = @{
    UserId = $currentUser
    LogonType = 'Interactive'
    RunLevel = 'Limited'
}
$principal = New-ScheduledTaskPrincipal @principalParameters

$settingsParameters = @{
    AllowStartIfOnBatteries = $true
    DontStopIfGoingOnBatteries = $true
    ExecutionTimeLimit = (New-TimeSpan -Minutes 2)
    MultipleInstances = 'IgnoreNew'
}
$settings = New-ScheduledTaskSettingsSet @settingsParameters

if ($PSCmdlet.ShouldProcess($TaskName, 'Register resume-only WSL time synchronization task')) {
    $registrationParameters = @{
        TaskName = $TaskName
        Action = $action
        Trigger = $trigger
        Principal = $principal
        Settings = $settings
        Force = $true
    }
    Register-ScheduledTask @registrationParameters | Out-Null
}

Write-Output "TASK=$TaskName"
Write-Output 'TRIGGER=Power-Troubleshooter/EventID=1'
Write-Output "DELAY_SECONDS=$DelaySeconds"
Write-Output "SCRIPT=$resolvedScriptPath"
