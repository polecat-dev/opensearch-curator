# Testing ConvertIndexToRemote with LocalStack

This directory contains integration tests for the `convert_index_to_remote` action using LocalStack as an S3-compatible storage backend.

## Overview

The tests verify that the action can successfully:
- Create snapshots in S3 (LocalStack)
- Restore indices with `storage_type='remote_snapshot'`
- Verify document counts between original and remote indices
- Create aliases pointing to remote indices
- Delete original indices with safety checks

## Prerequisites

### Required Software
- Docker & Docker Compose
- Python 3.8+
- AWS CLI (for bucket management)
- pytest

### Install Dependencies

```bash
# Install Python test dependencies (includes boto3)
pip install -e ".[test]"

# Or with uv:
uv sync --dev
```

## Test Environment Setup

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Test Environment                       │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐         ┌──────────────┐              │
│  │              │         │              │              │
│  │  OpenSearch  │◄───────►│  LocalStack  │              │
│  │    3.2.0     │         │  (S3 Mock)   │              │
│  │              │         │              │              │
│  │  Port: 19200 │         │  Port: 4566  │              │
│  └──────────────┘         └──────────────┘              │
│         │                        │                        │
│         │                        │                        │
│         │  Snapshot/Restore      │  S3 API                │
│         │  with remote storage   │  Operations            │
│         │                        │                        │
│         ▼                        ▼                        │
│  ┌──────────────────────────────────────┐               │
│  │         S3 Buckets (LocalStack)       │               │
│  ├──────────────────────────────────────┤               │
│  │  • test-curator-snapshots            │               │
│  │  • test-remote-segments              │               │
│  │  • test-remote-translogs             │               │
│  └──────────────────────────────────────┘               │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### Configuration

**OpenSearch** is configured with:
- Remote store enabled
- Segment repository: `remote-segment-repo` → `test-remote-segments` bucket
- Translog repository: `remote-translog-repo` → `test-remote-translogs` bucket
- Snapshot repository: Registered dynamically to `test-curator-snapshots` bucket

**LocalStack** provides:
- S3 API compatible storage
- No authentication required (test credentials)
- Persistent storage during test session

## Running Tests

### Quick Start (Linux/Mac)

```bash
# 1. Start test environment
./setup_remote_tests.sh

# 2. Run tests
pytest tests/integration/test_convert_index_to_remote.py -v

# 3. Stop environment
docker-compose -f test-environments/compose/docker-compose.test.yml down -v
```

### Quick Start (Windows)

```powershell
# 1. Start test environment
.\setup_remote_tests.ps1

# 2. Run tests
pytest tests/integration/test_convert_index_to_remote.py -v

# 3. Stop environment
docker-compose -f test-environments/compose/docker-compose.test.yml down -v
```

### Manual Setup

If you prefer manual setup:

```bash
# 1. Start services
docker-compose -f test-environments/compose/docker-compose.test.yml up -d

# 2. Wait for services to be ready (30-60 seconds)
# Check OpenSearch
curl https://localhost:19200/_cluster/health

# Check LocalStack
curl http://localhost:4566/_localstack/health

# 3. Create S3 buckets
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

aws --endpoint-url=http://localhost:4566 s3 mb s3://test-curator-snapshots
aws --endpoint-url=http://localhost:4566 s3 mb s3://test-remote-segments
aws --endpoint-url=http://localhost:4566 s3 mb s3://test-remote-translogs

# 4. Set environment variables
export TEST_ES_SERVER=https://localhost:19200
export LOCALSTACK_ENDPOINT=http://localhost:4566

# 5. Run tests
pytest tests/integration/test_convert_index_to_remote.py -v
```

## Test Cases

### Test Suite Coverage

| Test Case | Description | Verifies |
|-----------|-------------|----------|
| `test_convert_single_index_no_deletion` | Basic conversion without deletion | Snapshot, restore, document count |
| `test_convert_with_alias_creation` | Conversion with alias and deletion | Alias creation, safe deletion |
| `test_convert_multiple_indices` | Batch conversion | Multiple index handling |
| `test_convert_with_existing_snapshot` | Use existing snapshot | Snapshot reuse logic |
| `test_convert_with_custom_suffix` | Custom suffix for remote indices | Naming flexibility |
| `test_dry_run_mode` | Dry-run without changes | Dry-run mode |
| `test_document_count_verification_failure` | Verification logic | Safety checks |
| `test_missing_repository_error` | Error handling | Exception handling |
| `test_snapshot_already_in_progress` | Concurrent operation handling | SnapshotInProgress error |
| `test_verify_storage_type_parameter` | Code inspection | `storage_type='remote_snapshot'` |

### Running Specific Tests

```bash
# Run single test
pytest tests/integration/test_convert_index_to_remote.py::TestConvertIndexToRemote::test_convert_single_index_no_deletion -v

# Run with coverage
pytest tests/integration/test_convert_index_to_remote.py --cov=curator.actions.convert_index_to_remote --cov-report=html

# Run with detailed output
pytest tests/integration/test_convert_index_to_remote.py -v -s

# Run and stop on first failure
pytest tests/integration/test_convert_index_to_remote.py -x
```

## Troubleshooting

### Services Not Starting

**Problem:** OpenSearch or LocalStack fails to start

**Solutions:**
```bash
# Check Docker logs
docker-compose -f test-environments/compose/docker-compose.test.yml logs opensearch
docker-compose -f test-environments/compose/docker-compose.test.yml logs localstack

# Restart services
docker-compose -f test-environments/compose/docker-compose.test.yml restart

# Clean start
docker-compose -f test-environments/compose/docker-compose.test.yml down -v
docker-compose -f test-environments/compose/docker-compose.test.yml up -d
```

### Connection Refused Errors

**Problem:** Tests fail with connection errors

**Solutions:**
```bash
# Verify services are running
docker ps

# Check service health
curl https://localhost:19200/_cluster/health
curl http://localhost:4566/_localstack/health

# Check if ports are available
netstat -an | grep 19200
netstat -an | grep 4566
```

### S3 Bucket Errors

**Problem:** Bucket creation or access fails

**Solutions:**
```bash
# List buckets
aws --endpoint-url=http://localhost:4566 s3 ls

# Recreate buckets
aws --endpoint-url=http://localhost:4566 s3 rb s3://test-curator-snapshots --force
aws --endpoint-url=http://localhost:4566 s3 mb s3://test-curator-snapshots

# Verify bucket contents
aws --endpoint-url=http://localhost:4566 s3 ls s3://test-curator-snapshots/
```

### Remote Store Not Working

**Problem:** Indices don't become remote-backed

**Check:**
```bash
# Verify OpenSearch remote store configuration
curl https://localhost:19200/_cluster/settings?include_defaults=true | jq | grep remote_store

# Check index settings
curl https://localhost:19200/test-convert-1_remote/_settings | jq

# Verify repository is registered
curl https://localhost:19200/_snapshot
```

### Test Failures

**Problem:** Tests fail unexpectedly

**Debug steps:**
```bash
# Run with verbose output
pytest tests/integration/test_convert_index_to_remote.py -v -s

# Enable OpenSearch logging
# Add to test-environments/compose/docker-compose.test.yml:
# - logger.org.opensearch=DEBUG

# Check OpenSearch logs
docker-compose -f test-environments/compose/docker-compose.test.yml logs -f opensearch
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TEST_ES_SERVER` | `https://localhost:19200` | OpenSearch endpoint |
| `LOCALSTACK_ENDPOINT` | `http://localhost:4566` | LocalStack endpoint |
| `AWS_ACCESS_KEY_ID` | `test` | AWS access key (LocalStack) |
| `AWS_SECRET_ACCESS_KEY` | `test` | AWS secret key (LocalStack) |
| `AWS_DEFAULT_REGION` | `us-east-1` | AWS region |

## Cleanup

### Stop and Remove Everything

```bash
# Stop services and remove volumes
docker-compose -f test-environments/compose/docker-compose.test.yml down -v

# Remove Docker images (optional)
docker rmi opensearchproject/opensearch:3.2.0
docker rmi localstack/localstack:latest
```

### Keep Data for Debugging

```bash
# Stop services but keep volumes
docker-compose -f test-environments/compose/docker-compose.test.yml down

# Restart with existing data
docker-compose -f test-environments/compose/docker-compose.test.yml up -d
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test Remote Index Conversion

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      opensearch:
        image: opensearchproject/opensearch:3.2.0
        ports:
          - 19200:9200
        env:
          discovery.type: single-node
          DISABLE_SECURITY_PLUGIN: true
          
      localstack:
        image: localstack/localstack:latest
        ports:
          - 4566:4566
        env:
          SERVICES: s3
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -e ".[test]"
          pip install boto3 botocore
      
      - name: Setup test environment
        run: ./setup_remote_tests.sh
      
      - name: Run tests
        run: pytest tests/integration/test_convert_index_to_remote.py -v
```

## Performance Notes

### Test Execution Time

- **Setup:** ~30-60 seconds (service startup)
- **Per test:** ~5-15 seconds (snapshot/restore operations)
- **Full suite:** ~2-5 minutes (10 tests)

### Resource Usage

- **Memory:** ~2GB (OpenSearch + LocalStack)
- **Disk:** ~1GB (Docker images + volumes)
- **CPU:** Moderate during snapshot/restore

## Additional Resources

- [OpenSearch Remote Store Documentation](https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/remote-store/)
- [LocalStack Documentation](https://docs.localstack.cloud/)
- [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [pytest Documentation](https://docs.pytest.org/)

## Contributing

When adding new tests:

1. Follow existing test patterns
2. Use descriptive test names
3. Clean up resources in `tearDown()`
4. Document expected behavior
5. Test both success and failure cases
6. Include verification steps

## Support

For issues or questions:
- Check existing GitHub issues
- Review troubleshooting section above
- Run tests with `-v -s` for detailed output
- Check Docker logs for service errors
