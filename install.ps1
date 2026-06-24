# Install Grok D&D skills into Grok Build.
# Usage: .\install.ps1 [-Target <path>] [-Global]

param(
    [string]$Target = ".",
    [switch]$Global
)

$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot
$SourceSkills = Join-Path $RepoRoot ".grok\skills"

function Write-Step($msg) { Write-Host "`n$msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "  OK $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "  WARN $msg" -ForegroundColor Yellow }

if (-not (Test-Path $SourceSkills)) {
    Write-Error "Skills directory not found: $SourceSkills"
}

if ($Global) {
    $Target = Join-Path $env:USERPROFILE ".grok"
    New-Item -ItemType Directory -Force -Path $Target | Out-Null
}

$DestSkills = Join-Path $Target ".grok\skills"
New-Item -ItemType Directory -Force -Path $DestSkills | Out-Null

Write-Host "`nGrok D&D Skills Installer`n" -ForegroundColor Magenta
Write-Step "Installing skills to $DestSkills"

$count = 0
Get-ChildItem $SourceSkills -Directory | ForEach-Object {
    $skillFile = Join-Path $_.FullName "SKILL.md"
    if (Test-Path $skillFile) {
        $dest = Join-Path $DestSkills $_.Name
        Copy-Item -Recurse -Force $_.FullName $dest
        Write-Ok $_.Name
        $count++
    }
}

Write-Host "`nInstalled $count skills." -ForegroundColor Green
Write-Host "Campaign data will be stored at: $(Join-Path $env:USERPROFILE '.grok\artifacts\dnd-campaigns')" -ForegroundColor Gray
Write-Host "Say 'Let's play D&D' to start a campaign.`n" -ForegroundColor Gray