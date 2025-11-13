# Scripts Directory

This directory contains utility scripts for development and deployment.

## Test Execution
- **run_tests.ps1** - PowerShell test runner with .env loading (ROOT DIR)
- **run_curator.py** - Run curator CLI tool (ROOT DIR)
- **run_es_repo_mgr.py** - Run repository manager (ROOT DIR)
- **run_singleton.py** - Run singleton commands (ROOT DIR)

## Docker Build
- **post4docker.py** - Post-processing for Docker builds
- **alpine4docker.sh** - Alpine Linux binary building script

## Remote Testing
- **setup_remote_tests.ps1** - Windows setup for remote testing
- **setup_remote_tests.sh** - Linux/Mac setup for remote testing

## Usage

### Running Tests
```powershell
# From repository root
.\run_tests.ps1 tests/integration/ -q
```

### Building Docker Image
```bash
docker build -t opensearch-curator:latest .
```

See TESTING.md for comprehensive testing documentation.
