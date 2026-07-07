param(
  [Parameter(Mandatory=$true)][string]$Query,
  [int]$MaxResults = 20,
  [string]$PathFilter,
  [ValidateSet('auto','default','1.5a')][string]$Instance = 'auto',
  [switch]$Regex,
  [switch]$FilesOnly,
  [switch]$AutoStart,
  [string]$EverythingPath
)
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$check = & pwsh -NoProfile -File (Join-Path $scriptDir 'check-everything.ps1') -Instance $Instance -Start:$AutoStart -EverythingPath $EverythingPath | ConvertFrom-Json
if (-not $check.ok) {
  $check | ConvertTo-Json -Depth 4
  exit 1
}

$args = @('-json','-name','-path-column','-size','-date-modified','-date-format','1','-n',"$MaxResults")
if ($check.instance -eq '1.5a') { $args += @('-instance','1.5a') }
if ($PathFilter) { $args += @('-path',$PathFilter) }
if ($FilesOnly) { $args += '/a-d' }
if ($Regex) { $args += @('-regex',$Query) } else { $args += $Query }

& es.exe @args
