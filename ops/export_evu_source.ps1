# Read-only export of source files for a source-specific Phase 8 patch.
# Review ZIP contents before uploading; this excludes common secrets and dependencies.
param([string]$ProjectRoot = 'D:\Ecommerce\EVUE', [string]$OutputZip = 'D:\Ecommerce\EVUE_PHASE8_SOURCE.zip')
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $ProjectRoot)) { throw "Project not found: $ProjectRoot" }
$stage = Join-Path $env:TEMP ('evu-source-' + [guid]::NewGuid().ToString('N'))
$excludeDirs = @('.git','node_modules','.next','.venv','venv','__pycache__','media','staticfiles','dist','build','coverage','.pytest_cache')
$excludeNames = @('.env','.env.local','.env.production','.env.development','db.sqlite3','credentials.json','service-account.json')
$allowed = @('.py','.ts','.tsx','.js','.jsx','.json','.yaml','.yml','.toml','.txt','.md','.html','.css','.scss','.sql','.ps1')
try {
  New-Item -ItemType Directory -Path $stage -Force | Out-Null
  foreach ($folder in @('backend','frontend','ops')) {
    $src = Join-Path $ProjectRoot $folder
    if (-not (Test-Path -LiteralPath $src)) { continue }
    Get-ChildItem -LiteralPath $src -File -Recurse -Force | ForEach-Object {
      $file = $_
      $relative = $file.FullName.Substring($ProjectRoot.TrimEnd('\').Length).TrimStart('\')
      $parts = $relative -split '[\\/]'
      if (@($parts | Where-Object { $_ -in $excludeDirs }).Count -gt 0) { return }
      if ($file.Name -in $excludeNames -or $file.Name -match '^\.env\.' -or $file.Extension -notin $allowed) { return }
      if ($file.Length -gt 2MB) { return }
      $dest = Join-Path $stage $relative
      New-Item -ItemType Directory -Path (Split-Path $dest -Parent) -Force | Out-Null
      Copy-Item -LiteralPath $file.FullName -Destination $dest
    }
  }
  foreach ($name in @('compose.yaml','compose.yml','docker-compose.yml')) {
    $p = Join-Path $ProjectRoot $name
    if (Test-Path -LiteralPath $p) { Copy-Item -LiteralPath $p -Destination (Join-Path $stage $name) }
  }
  if (Test-Path -LiteralPath $OutputZip) { throw "Output already exists: $OutputZip" }
  Compress-Archive -Path (Join-Path $stage '*') -DestinationPath $OutputZip
  Write-Host "Created $OutputZip. IMPORTANT: Inspect ZIP for hardcoded credentials or personal data before sharing."
} finally { Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue }
