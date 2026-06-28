# Safe system + Grok skills cleanup. Does NOT touch campaign data or Documents.
# Usage: .\scripts\cleanup-system.ps1 [-DryRun]

param(
    [switch]$DryRun
)

$ErrorActionPreference = "Continue"
$stats = @{ removed = 0; freed_bytes = 0 }

function Remove-SafePath {
    param([string]$Path, [string]$Label)
    if (-not (Test-Path $Path)) { return }
    try {
        $size = (Get-ChildItem $Path -Recurse -Force -ErrorAction SilentlyContinue |
            Measure-Object -Property Length -Sum).Sum
        if ($DryRun) {
            Write-Host "[dry-run] $Label : $Path ($([math]::Round($size/1MB,1)) MB)" -ForegroundColor Yellow
            return
        }
        Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction Stop
        $script:stats.removed++
        $script:stats.freed_bytes += $size
        Write-Host "removed $Label ($([math]::Round($size/1MB,1)) MB)" -ForegroundColor Green
    } catch {
        Write-Host "skip $Label : $($_.Exception.Message)" -ForegroundColor DarkYellow
    }
}

function Remove-OldTempFiles {
    param([string]$Pattern, [int]$MinSizeMB = 0)
    $temp = [System.IO.Path]::GetTempPath()
    Get-ChildItem $temp -File -Force -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -like $Pattern -and $_.Length -ge ($MinSizeMB * 1MB) } |
        ForEach-Object {
            try {
                if ($DryRun) {
                    Write-Host "[dry-run] temp file $($_.Name) ($([math]::Round($_.Length/1MB,1)) MB)" -ForegroundColor Yellow
                } else {
                    $script:stats.freed_bytes += $_.Length
                    Remove-Item -LiteralPath $_.FullName -Force -ErrorAction Stop
                    $script:stats.removed++
                }
            } catch {
                Write-Host "skip locked: $($_.Name)" -ForegroundColor DarkYellow
            }
        }
}

Write-Host "`n=== Grok system cleanup ===`n" -ForegroundColor Cyan

# 1) Giant orphaned .tmp* files in user Temp (common Windows bloat)
Remove-OldTempFiles -Pattern ".tmp*" -MinSizeMB 50

# 2) Stale session export scratch dirs
Remove-SafePath "$env:LOCALAPPDATA\Temp\dnd_export_check" "dnd_export_check temp"

# 3) Grok skills caches (repo + global install)
$repo = Split-Path $PSScriptRoot -Parent
foreach ($root in @(
    (Join-Path $repo ".grok\skills"),
    (Join-Path $env:USERPROFILE ".grok\skills")
)) {
    if (-not (Test-Path $root)) { continue }
    Get-ChildItem $root -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
        ForEach-Object { Remove-SafePath $_.FullName "__pycache__" }
}

Remove-SafePath (Join-Path $repo ".pytest_cache") ".pytest_cache"

# 4) Nested duplicate .grok under plugins (install clutter)
$nested = Join-Path $env:USERPROFILE ".grok\installed-plugins"
if (Test-Path $nested) {
    Get-ChildItem $nested -Recurse -Directory -Filter ".grok" -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -match 'installed-plugins\\.*\\\.grok$' } |
        ForEach-Object { Remove-SafePath $_.FullName "nested plugin .grok" }
}

# 5) Old Grok Build session assets (>14 days)
$sessions = "C:\Grok Build\sessions"
if (Test-Path $sessions) {
    $cutoff = (Get-Date).AddDays(-14)
    Get-ChildItem $sessions -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTime -lt $cutoff } |
        ForEach-Object { Remove-SafePath $_.FullName "old session $($_.Name)" }
}

# 6) Home-root one-off logs (keep scripts in archive)
$archive = Join-Path $env:USERPROFILE "Projects\_archive\home-clutter"
if (-not $DryRun -and -not (Test-Path $archive)) {
    New-Item -ItemType Directory -Path $archive -Force | Out-Null
}
@("AMD_RyzenMaster.log", "AMDRM_Install.log", "cleanup_dism.log", "norton-grok-setup.log") |
    ForEach-Object {
        $src = Join-Path $env:USERPROFILE $_
        if (-not (Test-Path $src)) { return }
        if ($DryRun) {
            Write-Host "[dry-run] archive log $_" -ForegroundColor Yellow
        } else {
            Move-Item -LiteralPath $src -Destination (Join-Path $archive $_) -Force -ErrorAction SilentlyContinue
            Write-Host "archived $_" -ForegroundColor Green
            $script:stats.removed++
        }
    }

$freedGb = [math]::Round($stats.freed_bytes / 1GB, 2)
Write-Host "`nCleanup done: $($stats.removed) items, ~${freedGb} GB freed`n" -ForegroundColor Cyan
if ($DryRun) { Write-Host "Re-run without -DryRun to apply.`n" }