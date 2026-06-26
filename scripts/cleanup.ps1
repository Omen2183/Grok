# Grok D&D skills maintenance — removes install clutter without touching campaign data.
# Usage: .\scripts\cleanup.ps1 [-SkillsRoot <path>] [-DryRun]

param(
    [string]$SkillsRoot = (Join-Path $env:USERPROFILE ".grok\skills"),
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Remove-ClutterItem($path, $label) {
    if (-not (Test-Path $path)) { return }
    if ($DryRun) {
        Write-Host "  [dry-run] would remove $label : $path" -ForegroundColor Yellow
        return
    }
    Remove-Item -Recurse -Force $path
    Write-Host "  removed $label" -ForegroundColor Green
}

Write-Host "`nGrok skills cleanup`n" -ForegroundColor Cyan
Write-Host "Skills root: $SkillsRoot"

if (-not (Test-Path $SkillsRoot)) {
    Write-Host "Nothing to clean — skills root does not exist." -ForegroundColor Yellow
    exit 0
}

$removed = 0

# Nested skill-name/skill-name folders from old installs
Get-ChildItem $SkillsRoot -Directory | ForEach-Object {
    $nested = Join-Path $_.FullName $_.Name
    if (Test-Path $nested) {
        Remove-ClutterItem $nested "nested duplicate ($($_.Name))"
        $removed++
    }
}

# Stale nested .grok tree under home
$staleGrok = Join-Path (Split-Path $SkillsRoot -Parent) ".grok"
if (Test-Path $staleGrok) {
    Remove-ClutterItem $staleGrok "stale .grok/.grok tree"
    $removed++
}

# Python caches under skills
Get-ChildItem $SkillsRoot -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
    ForEach-Object {
        Remove-ClutterItem $_.FullName "__pycache__"
        $removed++
    }

# Pytest cache in repo (when run from repo root)
$repoRoot = Split-Path $PSScriptRoot -Parent
$pytestCache = Join-Path $repoRoot ".pytest_cache"
if (Test-Path $pytestCache) {
    Remove-ClutterItem $pytestCache ".pytest_cache"
    $removed++
}

Write-Host "`nCleanup complete ($removed items)." -ForegroundColor Green
if ($DryRun) {
    Write-Host "Re-run without -DryRun to apply changes.`n" -ForegroundColor Gray
}