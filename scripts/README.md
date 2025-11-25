# Scripts Directory

This directory contains utility scripts for development, deployment, and testing.

## 📋 Script Categories

### Test Execution (Root Directory)
- **../run_tests.ps1** - PowerShell test runner with .env loading
- **../run_curator.py** - Run curator CLI tool
- **../run_es_repo_mgr.py** - Run repository manager
- **../run_singleton.py** - Run singleton commands

### Docker Build
- **post4docker.py** - Post-processing for Docker builds
- **alpine4docker.sh** - Alpine Linux binary building script

### Remote Testing Setup
- **setup_remote_tests.ps1** - Windows setup for remote testing
- **setup_remote_tests.sh** - Linux/Mac setup for remote testing

### Environment Management
- **start-opensearch.bat** - Start OpenSearch (Windows)
- **start-opensearch.sh** - Start OpenSearch (Linux/Mac)
- **stop-opensearch.bat** - Stop OpenSearch (Windows)
- **stop-opensearch.sh** - Stop OpenSearch (Linux/Mac)
- **generate_test_certs.py** - Create TLS assets for docker-compose test stack
- **load_test_data.py** - Populate OpenSearch with synthetic log data for manual testing

### Repository Maintenance
- **cleanup_plan.ps1** - Repository cleanup and organization script

## 📖 Usage

### Running Tests
```powershell
# From repository root (Windows)
.\run_tests.ps1 tests/integration/ -q

# From repository root (Linux/Mac)
python run_tests.ps1 tests/integration/
```

### Building Docker Image
```bash
# Using Dockerfile (from repository root)
docker build -t opensearch-curator:latest .

# The Dockerfile will call:
# - scripts/alpine4docker.sh for Alpine binary
# - scripts/post4docker.py for post-processing
```

### Remote Testing Setup
```powershell
# Windows
.\scripts\setup_remote_tests.ps1

# Linux/Mac
./scripts/setup_remote_tests.sh
```

### Starting OpenSearch for Testing
```bash
# Linux/Mac
./scripts/start-opensearch.sh

# Windows
.\scripts\start-opensearch.bat

# Or use Docker Compose (preferred)
docker-compose -f docker-compose.test.yml up -d
```

### Generating TLS Assets (required for docker-compose.test.yml)
```bash
python scripts/generate_test_certs.py --password curatorssl
# Outputs to certs/generated/ (gitignored) and prints next steps
```

The compose stack expects `certs/generated/` to exist and the password to be
available through `OPENSEARCH_TEST_SSL_PASSWORD`. Update your `.env` using the
`certs/generated/passwords.env` snippet that the script creates.

### Loading Sample Data
```powershell
# Example: create 10 daily indices with 2k docs each on localhost:19200
python -m scripts.load_test_data --days 10 --docs-per-day 2000 --prefix logstash --alias logs-write
```

Run `python -m scripts.load_test_data --help` to see all connection and data-shaping options. The script
targets `https://localhost:19200` by default and generates `PREFIX-YYYY.MM.DD` indices filled with synthetic
log documents.

### Repository Cleanup
```powershell
# Review and organize documentation files
.\scripts\cleanup_plan.ps1
```

## 🔍 Script Details

### cleanup_plan.ps1
**Purpose:** Organize repository documentation and remove temporary files

**What it does:**
- Creates `docs/archive/` directory
- Archives outdated documentation
- Identifies files for consolidation
- Lists temporary files for removal
- Creates organization structure

**Usage:**
```powershell
.\scripts\cleanup_plan.ps1
```

### setup_remote_tests.ps1 / setup_remote_tests.sh
**Purpose:** Configure environment for testing ConvertIndexToRemote action

**What it does:**
- Sets up remote-enabled OpenSearch cluster
- Configures S3-compatible storage (MinIO or LocalStack)
- Creates necessary buckets and repositories
- Validates environment configuration

**Usage:**
```powershell
# Windows
.\scripts\setup_remote_tests.ps1

# Linux/Mac
./scripts/setup_remote_tests.sh
```

**Environment Variables:**
- `REMOTE_STORE_ENABLED=true`
- `REMOTE_STORE_TYPE=s3`
- `S3_ENDPOINT=http://localhost:9000`
- `S3_BUCKET=opensearch-remote-storage`

### post4docker.py
**Purpose:** Post-processing after Docker binary build

**Called by:** Dockerfile during `cx_Freeze` build

**What it does:**
- Adjusts binary paths
- Configures library dependencies
- Prepares final distribution structure

### alpine4docker.sh
**Purpose:** Build binary on Alpine Linux

**Called by:** Dockerfile

**What it does:**
- Sets up Alpine build environment
- Compiles Python dependencies
- Creates frozen binary with cx_Freeze
- Optimizes for Alpine Linux

## 📚 Related Documentation

- **Testing Guide:** [../docs/dev/TESTING.md](../docs/dev/TESTING.md)
- **CI/CD Guide:** [../.github/workflows/README.md](../.github/workflows/README.md)
- **Docker Testing:** [../docker-compose.test.yml](../docker-compose.test.yml)
- **Remote Tests:** [../tests/integration/README_REMOTE_TESTS.md](../tests/integration/README_REMOTE_TESTS.md)

## 🛠️ Development Workflow

### Typical Development Cycle
1. **Start Services:**
   ```bash
   docker-compose -f docker-compose.test.yml up -d
   ```

2. **Make Code Changes**

3. **Run Tests:**
   ```powershell
   .\run_tests.ps1 tests/integration/test_your_feature.py -v
   ```

4. **Cleanup:**
   ```bash
   docker-compose -f docker-compose.test.yml down
   ```

### Building Release Binary
1. **Build Docker Image:**
   ```bash
   docker build -t curator-builder .
   ```

2. **Extract Binary:**
   ```bash
   docker create --name curator-build curator-builder
   docker cp curator-build:/curator ./curator-binary
   docker rm curator-build
   ```

3. **Test Binary:**
   ```bash
   ./curator-binary/curator --version
   ```

## 🐛 Troubleshooting

### Tests Won't Run
- Check Docker containers: `docker-compose -f docker-compose.test.yml ps`
- Verify OpenSearch: `curl https://localhost:19200/_cluster/health`
- Check environment: Review `.env` file

### Remote Tests Failing
- Run setup script: `.\scripts\setup_remote_tests.ps1`
- Verify S3 endpoint: Check MinIO/LocalStack is running
- Check bucket exists: `aws --endpoint-url http://localhost:9000 s3 ls`

### Binary Build Issues
- Check Alpine script: `./scripts/alpine4docker.sh`
- Review Dockerfile build logs
- Verify cx_Freeze is working: Test locally first

---

**Last Updated:** November 13, 2025  
**Maintainer:** Development Team
