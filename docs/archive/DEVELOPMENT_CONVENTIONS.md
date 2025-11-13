# Development Conventions & Best Practices

**Project:** OpenSearch Curator  
**Last Updated:** November 5, 2025

---

## Python Module Execution

### ⚠️ IMPORTANT: Always use `python -m` for module execution

**Convention:** All Python-based tools and modules must be run using `python -m` prefix.

### Examples:

#### ✅ CORRECT:
```powershell
# pytest
python -m pytest

# pytest with options
python -m pytest opensearch_client/tests/unit -v
python -m pytest --cov=curator --cov-report=term-missing

# pip
python -m pip install opensearch-py

# Other modules
python -m black .
python -m mypy curator
python -m ruff check .
```

#### ❌ INCORRECT (Do NOT use):
```powershell
pytest                    # Wrong - don't use directly
pip install opensearch-py # Wrong - don't use directly
black .                   # Wrong - don't use directly
```

### Why?
- Ensures correct Python interpreter is used
- Avoids PATH issues
- Works consistently across environments (venv, conda, system Python)
- Prevents module not found errors
- More explicit and reliable

### Curator Commands:
```powershell
# Also use python -m for curator modules
python -m curator.cli --help
python -m curator.singletons show_indices --hosts http://localhost:19200
```

---

## Makefile Usage

### ⚠️ IMPORTANT: Makefile is Linux/Mac only - Use WSL on Windows

**Convention:** The `Makefile` is designed for Linux/Mac environments. On Windows, it must be run through WSL (Windows Subsystem for Linux).

### Windows Users:

#### ✅ CORRECT - Use WSL:
```powershell
# Install WSL if not already installed
wsl --install

# Run make commands in WSL
wsl make docker-up
wsl make test
wsl make install
```

#### ❌ INCORRECT - Don't use make directly on Windows PowerShell:
```powershell
make docker-up  # Won't work in PowerShell
```

### Alternative for Windows (PowerShell):
Instead of make commands, use direct commands:

```powershell
# Instead of: make docker-up
docker-compose up -d

# Instead of: make test
python -m pytest

# Instead of: make test-opensearch-client
python -m pytest opensearch_client/tests/unit -v

# Instead of: make install
python -m pip install -e .

# Instead of: make install-dev
python -m pip install -e ".[test]"

# Instead of: make lint
python -m ruff check .
python -m black --check .

# Instead of: make format
python -m black .
python -m ruff check --fix .
```

### Quick Reference Table:

| Make Command | Windows PowerShell Equivalent |
|--------------|-------------------------------|
| `make install` | `python -m pip install -e .` |
| `make install-dev` | `python -m pip install -e ".[test]"` |
| `make test` | `python -m pytest` |
| `make test-unit` | `python -m pytest tests/unit` |
| `make test-opensearch-client` | `python -m pytest opensearch_client/tests/unit -v` |
| `make docker-up` | `docker-compose up -d` |
| `make docker-down` | `docker-compose down` |
| `make lint` | `python -m ruff check . ; python -m black --check .` |
| `make format` | `python -m black . ; python -m ruff check --fix .` |
| `make build` | `python -m build` or `hatch build` |
| `make clean` | See cleanup commands below |

### Cleanup Commands (PowerShell):
```powershell
# Clean build artifacts
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Directory __pycache__ | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Filter *.pyc | Remove-Item -Force
```

---

## Hatch Environment Commands

### ✅ Hatch works on all platforms (Windows/Linux/Mac):

```powershell
# Create environment
hatch env create

# Run tests
hatch run test:pytest

# Run with coverage
hatch run test:pytest-cov

# Run linting
hatch run lint:all

# Build package
hatch build
```

---

## UV Package Manager

### ✅ UV works on all platforms:

```powershell
# Install UV
python -m pip install uv

# Use UV for faster installs
uv pip install -e .
uv pip install -e ".[test]"

# Hatch will automatically use UV if installed
hatch run test:pytest  # Uses UV automatically
```

---

## Docker Commands

### ✅ Docker Compose works on all platforms:

```powershell
# Start OpenSearch
docker-compose up -d

# With specific file
docker-compose -f docker-compose.secure.yml up -d

# Stop
docker-compose down

# Clean all data
docker-compose down -v

# View logs
docker-compose logs -f opensearch

# Check status
docker-compose ps
```

---

## Testing Workflow (Windows PowerShell)

### Complete testing workflow without make:

```powershell
# 1. Start OpenSearch
docker-compose up -d
Start-Sleep -Seconds 30  # Wait for startup

# 2. Verify OpenSearch is running
curl http://localhost:19200/_cluster/health

# 3. Run opensearch_client tests
python -m pytest opensearch_client/tests/unit -v

# 4. Run curator tests
python -m pytest tests/unit -v

# 5. Run with coverage
python -m pytest --cov=curator --cov-report=term-missing

# 6. Stop OpenSearch
docker-compose down
```

---

## CI/CD Note

When setting up CI/CD pipelines, always use:
- `python -m pytest` instead of `pytest`
- `python -m pip install` instead of `pip install`
- Direct docker-compose commands (works on all platforms)

Example GitHub Actions:
```yaml
- name: Install dependencies
  run: python -m pip install -e ".[test]"

- name: Run tests
  run: python -m pytest -v

- name: Start OpenSearch
  run: docker-compose up -d
```

---

## Summary

### Remember:
1. ✅ **Always use `python -m` for Python modules** (pytest, pip, black, etc.)
2. ✅ **Makefile only works in WSL on Windows** - Use direct commands in PowerShell
3. ✅ **Docker Compose works everywhere** - Use for test environment
4. ✅ **Hatch works everywhere** - Preferred for environment management
5. ✅ **UV works everywhere** - Optional for faster installs

### Don't Repeat Mistakes:
- ❌ Don't use `pytest` directly → Use `python -m pytest`
- ❌ Don't use `pip` directly → Use `python -m pip`
- ❌ Don't use `make` on Windows PowerShell → Use WSL or direct commands
- ❌ Don't forget the port is 19200 not 9200 for local testing

---

**Keep this file updated as new conventions are established!**
