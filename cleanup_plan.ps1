# OpenSearch Curator - Repository Cleanup Plan
# This script organizes documentation and removes redundant files
# Review each section before executing

Write-Host "OpenSearch Curator - Repository Cleanup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Create archive directory for old docs
Write-Host "Step 1: Create archive directory" -ForegroundColor Yellow
$archiveDir = "docs/archive"
if (-not (Test-Path $archiveDir)) {
    New-Item -ItemType Directory -Path $archiveDir -Force
    Write-Host "  Created: $archiveDir" -ForegroundColor Green
}

# Files to archive (move to docs/archive/)
Write-Host ""
Write-Host "Step 2: Archive outdated/redundant documentation" -ForegroundColor Yellow
$toArchive = @(
    "INTEGRATION_TEST_RESULTS.md",  # Outdated, info in TESTING.md
    "RECENT_UPDATES.md",             # Outdated, info in MIGRATION_PROGRESS.md
    "MIGRATION_CHECKLIST.md",        # Migration complete
    "OPENSEARCH_CLIENT_MIGRATION_STATUS.md"  # Info in MIGRATION_PROGRESS.md
)

foreach ($file in $toArchive) {
    if (Test-Path $file) {
        Write-Host "  Archiving: $file" -ForegroundColor Cyan
        Move-Item -Path $file -Destination "$archiveDir/$file" -Force
    }
}

# Files to consolidate and then remove
Write-Host ""
Write-Host "Step 3: Files to consolidate (manual review needed)" -ForegroundColor Yellow
$toConsolidate = @{
    "OPENSEARCH_COMPATIBILITY.md" = "Merge into OPENSEARCH_API_FIXES.md"
    "OPENSEARCH_PY_3.0.md" = "Merge into OPENSEARCH_API_FIXES.md"
    "DOCKER_TESTING.md" = "Content already in TESTING.md"
    "QUICKSTART.md" = "Merge into README.rst or README_FIRST.md"
    "README_OPENSEARCH.md" = "Duplicate of README.rst, update README.rst instead"
    "CONVERT_INDEX_TO_REMOTE_SUMMARY.md" = "Move to docs/ or examples/"
    "DEVELOPMENT_CONVENTIONS.md" = "Merge into CONTRIBUTING.md"
}

foreach ($file in $toConsolidate.Keys) {
    if (Test-Path $file) {
        Write-Host "  REVIEW: $file" -ForegroundColor Yellow
        Write-Host "    Action: $($toConsolidate[$file])" -ForegroundColor Gray
    }
}

# Temporary test files to remove
Write-Host ""
Write-Host "Step 4: Remove temporary test files" -ForegroundColor Yellow
$toRemove = @(
    "test_builder.py",      # Temporary test file in root
    "test_connection.py",   # Temporary test file in root
    "load_env.py"          # Functionality in run_tests.ps1
)

foreach ($file in $toRemove) {
    if (Test-Path $file) {
        Write-Host "  Would remove: $file" -ForegroundColor Red
        # Uncomment to actually delete:
        # Remove-Item $file -Force
    }
}

# Scripts to organize
Write-Host ""
Write-Host "Step 5: Organize scripts directory" -ForegroundColor Yellow
$scriptsToMove = @(
    "post4docker.py",
    "alpine4docker.sh"
)

foreach ($script in $scriptsToMove) {
    if (Test-Path $script) {
        Write-Host "  Would move to scripts/: $script" -ForegroundColor Cyan
        # Uncomment to actually move:
        # Move-Item -Path $script -Destination "scripts/$script" -Force
    }
}

# Create scripts README
Write-Host ""
Write-Host "Step 6: Create scripts/README.md" -ForegroundColor Yellow
$scriptsReadme = @"
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
``````powershell
# From repository root
.\run_tests.ps1 tests/integration/ -q
``````

### Building Docker Image
``````bash
docker build -t opensearch-curator:latest .
``````

See TESTING.md for comprehensive testing documentation.
"@

$scriptsReadmePath = "scripts/README.md"
if (-not (Test-Path $scriptsReadmePath)) {
    Set-Content -Path $scriptsReadmePath -Value $scriptsReadme
    Write-Host "  Created: $scriptsReadmePath" -ForegroundColor Green
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Cleanup Plan Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "COMPLETED:" -ForegroundColor Green
Write-Host "  - Created docs/archive/ directory" -ForegroundColor Gray
Write-Host "  - Archived 4 outdated documentation files" -ForegroundColor Gray
Write-Host "  - Created scripts/README.md" -ForegroundColor Gray
Write-Host ""
Write-Host "MANUAL REVIEW NEEDED:" -ForegroundColor Yellow
Write-Host "  - 7 files to consolidate (see Step 3 above)" -ForegroundColor Gray
Write-Host "  - Review content before merging/removing" -ForegroundColor Gray
Write-Host ""
Write-Host "TO EXECUTE:" -ForegroundColor Red
Write-Host "  - Uncomment lines in Steps 4-5 to remove/move files" -ForegroundColor Gray
Write-Host "  - Only after manual consolidation is complete" -ForegroundColor Gray
Write-Host ""
Write-Host "Next: Review NEXT_STEPS.md for release preparation tasks" -ForegroundColor Cyan
