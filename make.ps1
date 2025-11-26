# make.ps1 - PowerShell equivalent of Makefile for Windows
# Usage: .\make.ps1 <command>

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

$ComposeFile = "test-environments/compose/docker-compose.test.yml"

function Show-Help {
    Write-Host "OpenSearch Curator - Development Commands (PowerShell)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Setup:" -ForegroundColor Yellow
    Write-Host "  .\make.ps1 install          Install dependencies"
    Write-Host "  .\make.ps1 install-dev      Install with development dependencies"
    Write-Host ""
    Write-Host "Docker:" -ForegroundColor Yellow
    Write-Host "  .\make.ps1 docker-up        Start OpenSearch test environment"
    Write-Host "  .\make.ps1 docker-down      Stop OpenSearch test environment"
    Write-Host "  .\make.ps1 docker-logs      View OpenSearch logs"
    Write-Host "  .\make.ps1 docker-clean     Stop and remove all data"
    Write-Host ""
    Write-Host "Testing:" -ForegroundColor Yellow
    Write-Host "  .\make.ps1 test             Run all tests"
    Write-Host "  .\make.ps1 test-unit        Run unit tests only"
    Write-Host "  .\make.ps1 test-integration Run integration tests only"
    Write-Host "  .\make.ps1 test-cov         Run tests with coverage"
    Write-Host "  .\make.ps1 test-client      Run opensearch_client tests"
    Write-Host ""
    Write-Host "Code Quality:" -ForegroundColor Yellow
    Write-Host "  .\make.ps1 lint             Run all linters"
    Write-Host "  .\make.ps1 format           Format code with black"
    Write-Host "  .\make.ps1 mypy             Run type checking"
    Write-Host ""
    Write-Host "Build:" -ForegroundColor Yellow
    Write-Host "  .\make.ps1 build            Build distribution packages"
    Write-Host "  .\make.ps1 clean            Clean build artifacts"
    Write-Host ""
    Write-Host "Note: This script uses 'python -m' for all Python commands" -ForegroundColor Green
}

function Install {
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        Write-Host "Using UV for faster installation" -ForegroundColor Green
        uv pip install -e .
    } else {
        python -m pip install -e .
    }
}

function Install-Dev {
    Write-Host "Installing with test dependencies..." -ForegroundColor Cyan
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        Write-Host "Using UV for faster installation" -ForegroundColor Green
        uv pip install -e ".[test]"
    } else {
        python -m pip install -e ".[test]"
    }
}

function Docker-Up {
    Write-Host "Starting OpenSearch..." -ForegroundColor Cyan
    docker-compose -f $ComposeFile up -d
    Write-Host "Waiting for OpenSearch to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    try {
        $caCert = if ($env:TEST_ES_CA_CERT) { $env:TEST_ES_CA_CERT } else { "certs/generated/ca/root-ca.pem" }
        $username = if ($env:TEST_ES_USERNAME) { $env:TEST_ES_USERNAME } else { "admin" }
        $password = if ($env:TEST_ES_PASSWORD) { $env:TEST_ES_PASSWORD } else { $env:OPENSEARCH_INITIAL_ADMIN_PASSWORD }
        $curlArgs = @("--silent", "--show-error", "--fail", "https://localhost:19200/_cluster/health")
        if ($password) {
            $curlArgs = @("--user", "$username`:$password") + $curlArgs
        }
        if ($caCert -and (Test-Path $caCert)) {
            $curlArgs = @("--cacert", $caCert) + $curlArgs
        } else {
            $curlArgs = @("--insecure") + $curlArgs
        }
        $healthJson = & curl @curlArgs
        $health = $healthJson | ConvertFrom-Json
        Write-Host "OpenSearch is running!" -ForegroundColor Green
        Write-Host "Cluster: $($health.cluster_name)" -ForegroundColor Cyan
        Write-Host "Status: $($health.status)" -ForegroundColor Cyan
    } catch {
        Write-Host "OpenSearch may still be starting up. Check with: docker-compose -f $ComposeFile logs opensearch" -ForegroundColor Yellow
    }
}

function Docker-Down {
    Write-Host "Stopping OpenSearch..." -ForegroundColor Cyan
    docker-compose -f $ComposeFile down
    Write-Host "OpenSearch stopped" -ForegroundColor Green
}

function Docker-Logs {
    docker-compose -f $ComposeFile logs -f opensearch
}

function Docker-Clean {
    Write-Host "Removing OpenSearch containers and volumes..." -ForegroundColor Cyan
    docker-compose -f $ComposeFile down -v
    Write-Host "Cleaned!" -ForegroundColor Green
}

function Run-Tests {
    Write-Host "Running all tests..." -ForegroundColor Cyan
    python -m pytest
}

function Run-TestUnit {
    Write-Host "Running unit tests..." -ForegroundColor Cyan
    python -m pytest tests/unit
}

function Run-TestIntegration {
    Write-Host "Running integration tests..." -ForegroundColor Cyan
    python -m pytest tests/integration
}

function Run-TestCov {
    Write-Host "Running tests with coverage..." -ForegroundColor Cyan
    python -m pytest --cov=curator --cov-report=term-missing
}

function Run-TestClient {
    Write-Host "Running opensearch_client tests..." -ForegroundColor Cyan
    python -m pytest opensearch_client/tests/unit -v
}

function Run-Lint {
    Write-Host "Running linters..." -ForegroundColor Cyan
    python -m ruff check .
    python -m black --check .
    python -m mypy .
}

function Run-Format {
    Write-Host "Formatting code..." -ForegroundColor Cyan
    python -m black .
    python -m ruff check --fix .
}

function Run-Mypy {
    Write-Host "Running type checking..." -ForegroundColor Cyan
    python -m mypy curator
}

function Run-Build {
    Write-Host "Building distribution..." -ForegroundColor Cyan
    if (Get-Command hatch -ErrorAction SilentlyContinue) {
        hatch build
    } else {
        python -m build
    }
}

function Run-Clean {
    Write-Host "Cleaning build artifacts..." -ForegroundColor Cyan
    Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue
    Get-ChildItem -Recurse -Directory __pycache__ | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Recurse -Filter *.pyc | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "Cleaned!" -ForegroundColor Green
}

# Command routing
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "install" { Install }
    "install-dev" { Install-Dev }
    "docker-up" { Docker-Up }
    "docker-down" { Docker-Down }
    "docker-logs" { Docker-Logs }
    "docker-clean" { Docker-Clean }
    "test" { Run-Tests }
    "test-unit" { Run-TestUnit }
    "test-integration" { Run-TestIntegration }
    "test-cov" { Run-TestCov }
    "test-client" { Run-TestClient }
    "lint" { Run-Lint }
    "format" { Run-Format }
    "mypy" { Run-Mypy }
    "build" { Run-Build }
    "clean" { Run-Clean }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Run '.\make.ps1 help' to see available commands" -ForegroundColor Yellow
    }
}
