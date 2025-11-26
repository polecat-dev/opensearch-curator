# Setup script for ConvertIndexToRemote integration tests (Windows/PowerShell)
#
# This script:
# 1. Starts LocalStack (S3) and the secure OpenSearch stack
# 2. Waits for both services to become healthy
# 3. Creates the LocalStack buckets required by the integration tests
# 4. Prints the environment variables you should export before running pytest
#

$ErrorActionPreference = "Stop"

# Configuration
$LOCALSTACK_ENDPOINT = $env:LOCALSTACK_ENDPOINT
if (-not $LOCALSTACK_ENDPOINT) { $LOCALSTACK_ENDPOINT = "http://localhost:4566" }
$OPENSEARCH_ENDPOINT = $env:TEST_ES_SERVER
if (-not $OPENSEARCH_ENDPOINT) { $OPENSEARCH_ENDPOINT = "https://localhost:19200" }
$CA_CERT_PATH = $env:TEST_ES_CA_CERT
if (-not $CA_CERT_PATH) { $CA_CERT_PATH = "certs/generated/ca/root-ca.pem" }
$OPENSEARCH_USERNAME = $env:TEST_ES_USERNAME
if (-not $OPENSEARCH_USERNAME) { $OPENSEARCH_USERNAME = "admin" }
$OPENSEARCH_PASSWORD = $env:TEST_ES_PASSWORD
if (-not $OPENSEARCH_PASSWORD) { $OPENSEARCH_PASSWORD = $env:OPENSEARCH_INITIAL_ADMIN_PASSWORD }
$AWS_ACCESS_KEY = $env:AWS_ACCESS_KEY_ID
if (-not $AWS_ACCESS_KEY) { $AWS_ACCESS_KEY = "test" }
$AWS_SECRET_KEY = $env:AWS_SECRET_ACCESS_KEY
if (-not $AWS_SECRET_KEY) { $AWS_SECRET_KEY = "test" }
$AWS_REGION = $env:AWS_DEFAULT_REGION
if (-not $AWS_REGION) { $AWS_REGION = "us-east-1" }

function Get-CurlArgs {
    param([string]$Path)
    $args = @("--silent", "--show-error", "--fail")
    if (Test-Path $CA_CERT_PATH) {
        $args += @("--cacert", $CA_CERT_PATH)
    } else {
        $args += "--insecure"
    }
    if ($OPENSEARCH_PASSWORD) {
        $args = @("--user", "$OPENSEARCH_USERNAME`:$OPENSEARCH_PASSWORD") + $args
    }
    $args += ("{0}{1}" -f $OPENSEARCH_ENDPOINT, $Path)
    return ,$args
}

function Test-ServiceHealth {
    param(
        [string]$ServiceName,
        [scriptblock]$Command,
        [int]$MaxAttempts = 30
    )

    Write-Host "Waiting for $ServiceName to be ready..." -ForegroundColor Yellow
    for ($attempt = 0; $attempt -lt $MaxAttempts; $attempt++) {
        try {
            & $Command
            Write-Host "$ServiceName is ready" -ForegroundColor Green
            return $true
        } catch {
            Start-Sleep -Seconds 2
        }
    }

    Write-Host "$ServiceName failed to start" -ForegroundColor Red
    return $false
}

Write-Host "=== OpenSearch Curator - Remote Index Conversion Test Setup ===" -ForegroundColor Green

Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "Docker is running" -ForegroundColor Green
} catch {
    Write-Host "Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Starting services with docker-compose..." -ForegroundColor Yellow
docker-compose -f test-environments/compose/docker-compose.test.yml up -d | Out-Null

Write-Host ""
Write-Host "Waiting for LocalStack..." -ForegroundColor Yellow
$localStackReady = Test-ServiceHealth "LocalStack" {
    Invoke-WebRequest -Uri "$LOCALSTACK_ENDPOINT/_localstack/health" -TimeoutSec 2 -UseBasicParsing | Out-Null
}
if (-not $localStackReady) { exit 1 }

Write-Host ""
Write-Host "Waiting for OpenSearch..." -ForegroundColor Yellow
    $osReady = Test-ServiceHealth "OpenSearch" {
    $args = Get-CurlArgs "/_cluster/health"
    & curl.exe @args | Out-Null
}
if (-not $osReady) { exit 1 }

Write-Host ""
Write-Host "Configuring AWS credentials..." -ForegroundColor Yellow
$env:AWS_ACCESS_KEY_ID = $AWS_ACCESS_KEY
$env:AWS_SECRET_ACCESS_KEY = $AWS_SECRET_KEY
$env:AWS_DEFAULT_REGION = $AWS_REGION

Write-Host ""
Write-Host "Creating S3 buckets in LocalStack..." -ForegroundColor Yellow
$buckets = @("test-curator-snapshots", "test-remote-segments", "test-remote-translogs")
foreach ($bucket in $buckets) {
    Write-Host "  Bucket: $bucket... " -NoNewline
    try {
        aws --endpoint-url=$LOCALSTACK_ENDPOINT s3 mb "s3://$bucket" 2>&1 | Out-Null
        Write-Host "created" -ForegroundColor Green
    } catch {
        try {
            aws --endpoint-url=$LOCALSTACK_ENDPOINT s3 ls "s3://$bucket" 2>&1 | Out-Null
            Write-Host "already exists" -ForegroundColor Yellow
        } catch {
            Write-Host "failed" -ForegroundColor Red
            throw
        }
    }
}

Write-Host ""
Write-Host "Verifying remote store configuration..." -ForegroundColor Yellow
try {
    $settingsArgs = Get-CurlArgs "/_cluster/settings?include_defaults=true"
    $settingsJson = & curl.exe @settingsArgs | ConvertFrom-Json
    if ($settingsJson.ToString() -match "remote_store") {
        Write-Host "Remote store configuration detected" -ForegroundColor Green
    } else {
        Write-Host "Remote store configuration not found (may be disabled)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Could not verify remote store configuration" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Checking registered repositories..." -ForegroundColor Yellow
try {
    $reposArgs = Get-CurlArgs "/_snapshot"
    $reposJson = & curl.exe @reposArgs | ConvertFrom-Json
    Write-Host ("Repositories: {0}" -f ($reposJson | ConvertTo-Json -Compress))
} catch {
    Write-Host "No repositories registered yet (this is normal)"
}

Write-Host ""
Write-Host "=== Test Environment Ready ===" -ForegroundColor Green
Write-Host "Services:"
Write-Host "  OpenSearch: $OPENSEARCH_ENDPOINT"
Write-Host "  LocalStack: $LOCALSTACK_ENDPOINT"
Write-Host ""
Write-Host "Environment variables to export:"
Write-Host "  `$env:TEST_ES_SERVER = '$OPENSEARCH_ENDPOINT'"
Write-Host "  `$env:TEST_ES_CA_CERT = '$CA_CERT_PATH'"
Write-Host "  `$env:TEST_ES_USERNAME = '$OPENSEARCH_USERNAME'"
Write-Host "  `$env:TEST_ES_PASSWORD = '$OPENSEARCH_PASSWORD'"
Write-Host "  `$env:LOCALSTACK_ENDPOINT = '$LOCALSTACK_ENDPOINT'"
Write-Host ""
Write-Host "To run tests:"
Write-Host "  pytest tests/integration/test_convert_index_to_remote.py -v"
Write-Host ""
Write-Host "To stop services:"
Write-Host "  docker-compose -f test-environments/compose/docker-compose.test.yml down -v"
Write-Host ""
