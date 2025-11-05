# Important Notes - Read First! 📋

## Critical Development Conventions

### 1. ⚠️ Always Use `python -m` for Python Modules

**WHY:** Ensures correct interpreter and avoids PATH issues

```powershell
# ✅ CORRECT
python -m pytest
python -m pip install package
python -m black .
python -m mypy curator

# ❌ WRONG - Don't do this!
pytest
pip install package
black .
```

### 2. ⚠️ Makefile vs PowerShell

**On Windows:**
- ✅ Use `.\make.ps1` (PowerShell script)
- ✅ Or use direct commands
- ❌ `Makefile` only works in WSL

```powershell
# Windows PowerShell - Use these:
.\make.ps1 test
.\make.ps1 docker-up

# Or direct commands:
python -m pytest
docker-compose up -d
```

**On Linux/Mac/WSL:**
- ✅ Use `make` commands
- ✅ Or use direct commands

```bash
# Linux/Mac/WSL
make test
make docker-up
```

### 3. 🔌 Port Configuration

OpenSearch runs on **port 19200** (not 9200) due to Windows restrictions.

```powershell
# Connect to:
http://localhost:19200

# Not:
http://localhost:9200  # ❌ Wrong port!
```

---

## Quick Commands Reference

### Windows PowerShell:

```powershell
# Start OpenSearch
docker-compose up -d

# Run tests
python -m pytest opensearch_client/tests/unit -v

# Install dependencies
python -m pip install -e ".[test]"

# Format code
python -m black .

# Or use the PowerShell helper:
.\make.ps1 docker-up
.\make.ps1 test-client
```

### Linux/Mac/WSL:

```bash
# Use Makefile
make docker-up
make test-client

# Or direct commands work too
python -m pytest opensearch_client/tests/unit -v
```

---

## Complete Documentation

See these files for full details:

1. **[DEVELOPMENT_CONVENTIONS.md](DEVELOPMENT_CONVENTIONS.md)** - ⭐ Read this first!
   - Python module execution rules
   - Makefile vs PowerShell guidance
   - Command reference table

2. **[QUICKSTART.md](QUICKSTART.md)** - Quick testing guide
   - Start/stop OpenSearch
   - Create test data
   - Run basic tests

3. **[DOCKER_TESTING.md](DOCKER_TESTING.md)** - Docker environment guide
   - Docker Compose configurations
   - Security settings
   - Troubleshooting

4. **[RECENT_UPDATES.md](RECENT_UPDATES.md)** - Latest changes
   - What was just completed
   - Testing instructions
   - Next steps

---

## Don't Repeat These Mistakes! 🚫

Common errors to avoid:

1. ❌ Using `pytest` directly → Use `python -m pytest`
2. ❌ Using `pip` directly → Use `python -m pip`
3. ❌ Using `make` on Windows PowerShell → Use `.\make.ps1` or WSL
4. ❌ Connecting to port 9200 → Use port 19200
5. ❌ Forgetting to start OpenSearch → `docker-compose up -d`

---

**Keep this in mind for all development work!** 💡
