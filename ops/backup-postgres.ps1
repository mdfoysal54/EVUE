[CmdletBinding()]
param(
    [string]$OutputDir = '.\backups'
)

$ErrorActionPreference = 'Stop'

# Ensure backup directory exists
$resolvedOutputDir = [System.IO.Path]::GetFullPath($OutputDir)
if (-not (Test-Path -Path $resolvedOutputDir)) {
    New-Item -ItemType Directory -Force -Path $resolvedOutputDir | Out-Null
}

# Resolve target file path and container temporary path
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$targetFile = Join-Path -Path $resolvedOutputDir -ChildPath "evu-$stamp.dump"
$containerTempPath = "/tmp/evu-$stamp.dump"

# Locate the database container
$container = (docker compose ps -q db)
if ($null -ne $container) {
    $container = $container.Trim()
}

if (-not $container) {
    throw 'Database container is not running.'
}

try {
    # Run pg_dump inside the container using custom format (-Fc)
    $dumpArgs = @(
        'exec',
        $container,
        'pg_dump',
        '-U', 'evu',
        '-d', 'evu',
        '-Fc',
        '-f', $containerTempPath
    )
    $process = Start-Process -FilePath 'docker' -ArgumentList $dumpArgs -Wait -NoNewWindow -PassThru

    if ($process.ExitCode -ne 0) {
        throw "pg_dump failed with exit code $($process.ExitCode)."
    }

    # Copy binary dump file from container to Windows host
    docker cp "${container}:${containerTempPath}" $targetFile
    if ($LASTEXITCODE -ne 0) {
        throw "docker cp failed with exit code $LASTEXITCODE."
    }

    Write-Output "Backup completed successfully: $targetFile"
}
finally {
    # Always clean up the temporary dump file inside the container
    docker exec $container rm -f $containerTempPath | Out-Null
}