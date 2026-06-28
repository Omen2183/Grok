# Package current .grok/skills for Grok iOS import / drift comparison.
# Usage: .\scripts\ios-export.ps1 [-Output <path>]

param(
    [string]$Output = (Join-Path $env:USERPROFILE "Downloads\dnd_skills_export_$(Get-Date -Format 'yyyyMMdd').tar.gz")
)

$ErrorActionPreference = "Stop"
$repo = Split-Path $PSScriptRoot -Parent
$skills = Join-Path $repo ".grok\skills"
$staging = Join-Path $env:TEMP "dnd_ios_export_$(Get-Random)"

if (-not (Test-Path $skills)) { throw "Skills not found: $skills" }

New-Item -ItemType Directory -Path (Join-Path $staging "skills") -Force | Out-Null
Get-ChildItem $skills -Directory | Where-Object { $_.Name -like "dnd-*" } | ForEach-Object {
    $dest = Join-Path $staging "skills" $_.Name
    Copy-Item $_.FullName $dest -Recurse -Force
    Get-ChildItem $dest -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
}

if (Test-Path $Output) { Remove-Item $Output -Force }
tar -czf $Output -C $staging skills
Remove-Item $staging -Recurse -Force

Write-Host "Exported: $Output" -ForegroundColor Green
Write-Host "Verify: python .grok/skills/dnd-skills-manager/scripts/skills_manager.py sync-check --against (tar -xzf ... skills folder)" -ForegroundColor Gray