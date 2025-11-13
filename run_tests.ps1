# Run integration tests with environment from .env file
# Usage: .\run_tests.ps1 [pytest arguments]
# Example: .\run_tests.ps1 -xvs tests/integration/test_snapshot.py

# Load .env file if it exists
if (Test-Path .env) {
    Write-Host "Loading environment from .env file..." -ForegroundColor Green
    Get-Content .env | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.+)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, 'Process')
            Write-Host "  Set $key=$value" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "No .env file found. Copy .env.example to .env to customize settings." -ForegroundColor Yellow
}

# Display current TEST_ES_SERVER
$testServer = if ($env:TEST_ES_SERVER) { $env:TEST_ES_SERVER } else { "http://127.0.0.1:9200" }
Write-Host "`nTEST_ES_SERVER: $testServer" -ForegroundColor Cyan

# Run pytest with all arguments passed to this script
Write-Host "`nRunning pytest..." -ForegroundColor Green
python -m pytest @args
