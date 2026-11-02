param([switch]$IncludeTests, [switch]$IncludeBuild, [switch]$CheckMigrations)
$ErrorActionPreference = 'Continue'
$root = 'D:\Ecommerce\EVUE'
if (-not (Test-Path (Join-Path $root 'docker-compose.yml')) -and -not (Test-Path (Join-Path $root 'compose.yaml'))) { throw "Cannot locate Compose file in $root" }
Set-Location $root
$script:failures = 0
function Invoke-Check([string]$Title, [scriptblock]$Action) {
  Write-Host "`n=== $Title ===" -ForegroundColor Cyan
  & $Action
  $code = $LASTEXITCODE
  if ($null -ne $code -and $code -ne 0) { Write-Host "FAIL: $Title (exit $code)" -ForegroundColor Red; $script:failures++ }
  else { Write-Host "PASS: $Title" -ForegroundColor Green }
  $global:LASTEXITCODE = 0
}
Invoke-Check 'Compose configuration' { docker compose config --quiet }
Invoke-Check 'Container state' { docker compose ps --all }
Invoke-Check 'Django system checks' { docker compose exec -T backend python manage.py check }
Invoke-Check 'Django deployment checks (warnings require review)' { docker compose exec -T backend python manage.py check --deploy }
Invoke-Check 'Migration plan (read-only)' { docker compose exec -T backend python manage.py showmigrations --plan }
if ($CheckMigrations) { Invoke-Check 'No unapplied migrations' { docker compose exec -T backend python manage.py migrate --check } }
if ($IncludeTests) { Invoke-Check 'Django test suite' { docker compose exec -T backend python manage.py test --noinput } }
if ($IncludeBuild) { Invoke-Check 'Frontend production build' { docker compose build frontend } }
Invoke-Check 'Backend HTTP response' { curl.exe --silent --show-error --max-time 15 --output NUL --write-out 'HTTP %{http_code}\n' http://127.0.0.1:8000/ }
Invoke-Check 'Frontend HTTP response' { curl.exe --silent --show-error --max-time 15 --output NUL --write-out 'HTTP %{http_code}\n' http://127.0.0.1:3000/ }
Write-Host "`n=== Recent backend logs ==="; docker compose logs --no-color --tail 40 backend
Write-Host "`n=== Recent frontend logs ==="; docker compose logs --no-color --tail 40 frontend
Write-Host "`nCheck count with command failures: $script:failures"
if ($script:failures -gt 0) { exit 1 }