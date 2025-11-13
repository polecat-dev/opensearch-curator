# Setup script for ConvertIndexToRemote integration tests (Windows/PowerShell)
#
# This script:
# 1. Starts LocalStack (S3) and OpenSearch with remote store configuration
# 2. Waits for services to be healthy
# 3. Creates S3 buckets in LocalStack
# 4. Registers snapshot repository in OpenSearch
# 5. Prepares environment for running tests
#

$ErrorActionPreference = "Stop"

# Configuration
$LOCALSTACK_ENDPOINT = "http://localhost:4566"
$OPENSEARCH_ENDPOINT = "http://localhost:19200"
$AWS_ACCESS_KEY = "test"
$AWS_SECRET_KEY = "test"
$AWS_REGION = "us-east-1"

Write-Host "=== OpenSearch Curator - Remote Index Conversion Test Setup ===" -ForegroundColor Green
Write-Host ""

# Function to wait for a service
function Wait-ForService {
    param(
        [string]$ServiceName,
        [string]$HealthCheckUrl,
        [int]$MaxAttempts = 30
    )
    
    Write-Host "Waiting for $ServiceName to be ready..." -ForegroundColor Yellow
    
    for ($attempt = 0; $attempt -lt $MaxAttempts; $attempt++) {
        try {
            $response = Invoke-WebRequest -Uri $HealthCheckUrl -Method Get -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "✓ $ServiceName is ready" -ForegroundColor Green
                return $true
            }
        }
        catch {
            Write-Host "." -NoNewline
            Start-Sleep -Seconds 2
        }
    }
    
    Write-Host ""
    Write-Host "✗ $ServiceName failed to start" -ForegroundColor Red
    return $false
}

# Step 1: Check if Docker is running
Write-Host "Step 1: Checking Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
}
catch {
    Write-Host "✗ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Step 2: Start services
Write-Host ""
Write-Host "Step 2: Starting services with docker-compose..." -ForegroundColor Yellow
docker-compose -f docker-compose.test.yml up -d

# Step 3: Wait for LocalStack
Write-Host ""
Write-Host "Step 3: Waiting for LocalStack..." -ForegroundColor Yellow
if (-not (Wait-ForService "LocalStack" "$LOCALSTACK_ENDPOINT/_localstack/health")) {
    exit 1
}

# Step 4: Wait for OpenSearch
Write-Host ""
Write-Host "Step 4: Waiting for OpenSearch..." -ForegroundColor Yellow
if (-not (Wait-ForService "OpenSearch" "$OPENSEARCH_ENDPOINT/_cluster/health")) {
    exit 1
}

# Step 5: Set AWS environment variables
Write-Host ""
Write-Host "Step 5: Setting up AWS credentials..." -ForegroundColor Yellow
$env:AWS_ACCESS_KEY_ID = $AWS_ACCESS_KEY
$env:AWS_SECRET_ACCESS_KEY = $AWS_SECRET_KEY
$env:AWS_DEFAULT_REGION = $AWS_REGION

# Step 6: Create S3 buckets
Write-Host ""
Write-Host "Step 6: Creating S3 buckets in LocalStack..." -ForegroundColor Yellow

$buckets = @("test-curator-snapshots", "test-remote-segments", "test-remote-translogs")

foreach ($bucket in $buckets) {
    Write-Host "  Creating bucket: $bucket... " -NoNewline
    
    try {
        # Try to create bucket
        aws --endpoint-url=$LOCALSTACK_ENDPOINT s3 mb "s3://$bucket" 2>&1 | Out-Null
        Write-Host "✓" -ForegroundColor Green
    }
    catch {
        # Check if bucket already exists
        try {
            aws --endpoint-url=$LOCALSTACK_ENDPOINT s3 ls "s3://$bucket" 2>&1 | Out-Null
            Write-Host "✓ (already exists)" -ForegroundColor Yellow
        }
        catch {
            Write-Host "✗ Failed" -ForegroundColor Red
        }
    }
}

# Step 7: Verify OpenSearch remote store configuration
Write-Host ""
Write-Host "Step 7: Verifying OpenSearch remote store configuration..." -ForegroundColor Yellow

try {
    $clusterSettings = Invoke-RestMethod -Uri "$OPENSEARCH_ENDPOINT/_cluster/settings?include_defaults=true" -Method Get
    $settingsJson = $clusterSettings | ConvertTo-Json -Depth 10
    
    if ($settingsJson -match "remote_store") {
        Write-Host "✓ Remote store configuration detected" -ForegroundColor Green
    }
    else {
        Write-Host "⚠ Remote store configuration not found (may not be enabled)" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "⚠ Could not verify remote store configuration" -ForegroundColor Yellow
}

# Step 8: List registered repositories
Write-Host ""
Write-Host "Step 8: Checking registered repositories..." -ForegroundColor Yellow
try {
    $repos = Invoke-RestMethod -Uri "$OPENSEARCH_ENDPOINT/_snapshot" -Method Get
    Write-Host "Repositories: $($repos | ConvertTo-Json -Compress)"
}
catch {
    Write-Host "No repositories registered yet (this is normal)"
}

# Step 9: Display service information
Write-Host ""
Write-Host "=== Test Environment Ready ===" -ForegroundColor Green
Write-Host ""
Write-Host "Services:"
Write-Host "  OpenSearch: $OPENSEARCH_ENDPOINT"
Write-Host "  LocalStack: $LOCALSTACK_ENDPOINT"
Write-Host ""
Write-Host "S3 Buckets:"
foreach ($bucket in $buckets) {
    Write-Host "  - $bucket"
}
Write-Host ""
Write-Host "Environment variables set:"
Write-Host "  `$env:TEST_ES_SERVER = '$OPENSEARCH_ENDPOINT'"
Write-Host "  `$env:LOCALSTACK_ENDPOINT = '$LOCALSTACK_ENDPOINT'"
Write-Host "  `$env:AWS_ACCESS_KEY_ID = '$AWS_ACCESS_KEY'"
Write-Host "  `$env:AWS_SECRET_ACCESS_KEY = '$AWS_SECRET_KEY'"
Write-Host ""

# Set environment variables for the session
$env:TEST_ES_SERVER = $OPENSEARCH_ENDPOINT
$env:LOCALSTACK_ENDPOINT = $LOCALSTACK_ENDPOINT

Write-Host "To run tests:" -ForegroundColor Green
Write-Host "  pytest tests/integration/test_convert_index_to_remote.py -v"
Write-Host ""
Write-Host "To stop services:" -ForegroundColor Green
Write-Host "  docker-compose -f docker-compose.test.yml down -v"
Write-Host ""
