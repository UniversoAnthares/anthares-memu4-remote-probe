$ErrorActionPreference = 'Stop'

Write-Host '=== Anthares MEmu4 Remote Probe: Item 1 ==='
Write-Host ('Timestamp UTC: ' + [DateTime]::UtcNow.ToString('o'))
Write-Host ('Machine: ' + $env:COMPUTERNAME)
Write-Host ('AppVeyor worker image: ' + $env:APPVEYOR_BUILD_WORKER_IMAGE)
Write-Host ('AppVeyor build ID: ' + $env:APPVEYOR_BUILD_ID)

$os = Get-CimInstance Win32_OperatingSystem
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
$cs = Get-CimInstance Win32_ComputerSystem
$drive = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"

$logicalProcessors = [int]$cs.NumberOfLogicalProcessors
$totalRamGiB = [math]::Round($cs.TotalPhysicalMemory / 1GB, 2)
$freeDiskGiB = [math]::Round($drive.FreeSpace / 1GB, 2)

Write-Host ('OS: ' + $os.Caption + ' ' + $os.Version)
Write-Host ('CPU: ' + $cpu.Name)
Write-Host ('Logical processors: ' + $logicalProcessors)
Write-Host ('RAM GiB: ' + $totalRamGiB)
Write-Host ('Free C: GiB: ' + $freeDiskGiB)
Write-Host ('VirtualizationFirmwareEnabled: ' + $cpu.VirtualizationFirmwareEnabled)
Write-Host ('SecondLevelAddressTranslationExtensions: ' + $cpu.SecondLevelAddressTranslationExtensions)
Write-Host ('VMMonitorModeExtensions: ' + $cpu.VMMonitorModeExtensions)
Write-Host ('HypervisorPresent: ' + $cs.HypervisorPresent)

$nestedSignals = @(
  [bool]$cpu.VirtualizationFirmwareEnabled,
  [bool]$cpu.SecondLevelAddressTranslationExtensions,
  [bool]$cpu.VMMonitorModeExtensions
)
$nestedEligible = ($logicalProcessors -ge 4) -and ($nestedSignals -notcontains $false)

$result = [ordered]@{
  timestamp_utc = [DateTime]::UtcNow.ToString('o')
  machine = $env:COMPUTERNAME
  appveyor_worker_image = $env:APPVEYOR_BUILD_WORKER_IMAGE
  appveyor_build_id = $env:APPVEYOR_BUILD_ID
  os = $os.Caption
  os_version = $os.Version
  cpu = $cpu.Name
  logical_processors = $logicalProcessors
  ram_gib = $totalRamGiB
  free_c_gib = $freeDiskGiB
  virtualization_firmware_enabled = [bool]$cpu.VirtualizationFirmwareEnabled
  slat = [bool]$cpu.SecondLevelAddressTranslationExtensions
  vm_monitor_mode_extensions = [bool]$cpu.VMMonitorModeExtensions
  hypervisor_present = [bool]$cs.HypervisorPresent
  nested_virtualization_gate = [bool]$nestedEligible
}

$result | ConvertTo-Json -Depth 5 | Set-Content -Path '.\item1-probe-result.json' -Encoding UTF8
$result | ConvertTo-Json -Depth 5 | Write-Host

if (-not $nestedEligible) {
  Write-Error 'ITEM1_FAIL: worker does not expose the required 4-core nested-virtualization signals. MEmu installation must not start.'
  exit 42
}

Write-Host 'ITEM1_PASS: 4-core nested-virtualization gate satisfied.'
