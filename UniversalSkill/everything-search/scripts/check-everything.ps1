param(
  [switch]$Start,
  [ValidateSet('auto','default','1.5a')][string]$Instance = 'auto',
  [int]$TimeoutSeconds = 15,
  [string]$EverythingPath
)
$ErrorActionPreference = 'Stop'

function Find-CommandPath($Name) {
  $cmd = Get-Command $Name -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  return $null
}

function Find-EverythingExe([string]$ConfiguredPath) {
  if ($ConfiguredPath) {
    if (Test-Path -LiteralPath $ConfiguredPath) { return $ConfiguredPath }
    throw "Everything.exe not found at configured path: $ConfiguredPath"
  }
  $fromPath = Find-CommandPath 'Everything.exe'
  if ($fromPath) { return $fromPath }
  $candidates = @(
    "$env:ProgramFiles\Everything\Everything.exe",
    "${env:ProgramFiles(x86)}\Everything\Everything.exe",
    "$env:LOCALAPPDATA\Everything\Everything.exe",
    "$env:USERPROFILE\scoop\apps\everything\current\Everything.exe",
    "$env:USERPROFILE\scoop\apps\everything-beta\current\Everything.exe"
  )
  foreach ($candidate in $candidates) {
    if ($candidate -and (Test-Path -LiteralPath $candidate)) { return $candidate }
  }
  return $null
}

function Es-Args([string]$InstanceName) {
  if ($InstanceName -eq '1.5a') { return @('-instance','1.5a') }
  return @()
}

function Probe([string]$InstanceName) {
  $es = Find-CommandPath 'es.exe'
  if (-not $es) { return [pscustomobject]@{ ok = $false; error = 'es.exe not found' } }
  $args = (Es-Args $InstanceName) + @('-get-everything-version')
  $out = & $es @args 2>&1
  if ($LASTEXITCODE -eq 0 -and "$out".Trim()) {
    return [pscustomobject]@{ ok = $true; version = "$out".Trim(); instance = $InstanceName }
  }
  return [pscustomobject]@{ ok = $false; error = "$out".Trim(); instance = $InstanceName }
}

if (-not ($IsWindows -or $env:OS -eq 'Windows_NT')) {
  [pscustomobject]@{ ok = $false; platform = $PSVersionTable.Platform; error = 'Everything/es.exe is Windows-only' } | ConvertTo-Json -Depth 4
  exit 0
}

$esPath = Find-CommandPath 'es.exe'
$everythingExe = Find-EverythingExe $EverythingPath
$instances = if ($Instance -eq 'auto') { @('default','1.5a') } else { @($Instance) }

foreach ($i in $instances) {
  $probe = Probe $i
  if ($probe.ok) {
    [pscustomobject]@{ ok = $true; es = $esPath; everything = $everythingExe; instance = $probe.instance; version = $probe.version; started = $false } | ConvertTo-Json -Depth 4
    exit 0
  }
}

if ($Start -and $everythingExe) {
  Start-Process -FilePath $everythingExe -ArgumentList '-startup' -WindowStyle Hidden | Out-Null
  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  do {
    foreach ($i in $instances) {
      $probe = Probe $i
      if ($probe.ok) {
        [pscustomobject]@{ ok = $true; es = $esPath; everything = $everythingExe; instance = $probe.instance; version = $probe.version; started = $true } | ConvertTo-Json -Depth 4
        exit 0
      }
    }
    Start-Sleep -Milliseconds 500
  } while ((Get-Date) -lt $deadline)
}

[pscustomobject]@{ ok = $false; es = $esPath; everything = $everythingExe; error = 'Everything IPC not ready'; startAttempted = [bool]$Start } | ConvertTo-Json -Depth 4
