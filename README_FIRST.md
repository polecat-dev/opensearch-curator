# Important Notes - Read First! ðŸ“‹



## Quick Links



### ðŸŽ¯ Start Here

- ðŸ“Š **[docs/STATUS.md](docs/STATUS.md)** - Current status summary (100% migration complete!)

- ðŸš€ **[docs/NEXT_STEPS.md](docs/NEXT_STEPS.md)** - What to do next (CI/CD, release prep)



###  Developer Guides

- ðŸ§ª **[docs/dev/TESTING.md](docs/dev/TESTING.md)** - Comprehensive guide to running and debugging tests

- ðŸ”§ **[docs/dev/OPENSEARCH_API_FIXES.md](docs/dev/OPENSEARCH_API_FIXES.md)** - OpenSearch-py 3.0 compatibility fixes (8 fixes)

- ðŸ“ˆ **[docs/dev/MIGRATION_PROGRESS.md](docs/dev/MIGRATION_PROGRESS.md)** - Migration status (updated with 100% completion)



### ðŸ¤– Strategic & Planning

- ðŸ—ºï¸ **[docs/dev/AGENTS.md](docs/dev/AGENTS.md)** - Strategic analysis and migration complete status

- ðŸ“š **Main Documentation** - `README.md` (Markdown format)



## Critical Development Conventions



### 1. âš ï¸ Always Use `python -m` for Python Modules



**WHY:** Ensures correct interpreter and avoids PATH issues



```powershell

# âœ… CORRECT

python -m pytest

python -m pip install package

python -m black .

python -m mypy curator



# âŒ WRONG - Don't do this!

pytest

pip install package

black .

```



### 2. âš ï¸ Makefile vs PowerShell



**On Windows:**

- âœ… Use `.\make.ps1` (PowerShell script)

- âœ… Or use direct commands

- âŒ `Makefile` only works in WSL



```powershell

# Windows PowerShell - Use these:

.\make.ps1 test

.\make.ps1 docker-up



# Or direct commands:

python -m pytest

docker-compose -f test-environments/compose/docker-compose.test.yml up -d

```



**On Linux/Mac/WSL:**

- âœ… Use `make` commands

- âœ… Or use direct commands



```bash

# Linux/Mac/WSL

make test

make docker-up

```



### 3. ðŸ”Œ Port Configuration



OpenSearch runs on **port 19200 over HTTPS** (not 9200) due to Windows restrictions.



```powershell

# Connect to:

https://localhost:19200



# Not:

http://localhost:9200  # âŒ Wrong protocol/port!

```



---



## Quick Commands Reference



### Test Environments
- Use `docker-compose -f test-environments/compose/docker-compose.test.yml up -d` to bring up the secure OpenSearch + LocalStack stack.
- Manual action recipes (and helper scripts like `run-curator.sh`) now live in `test-environments/local-runner/`.
- See `test-environments/README.md` for a quick overview of both folders.

### Windows PowerShell:



```powershell

# Start OpenSearch

docker-compose -f test-environments/compose/docker-compose.test.yml up -d



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



1. **[DEVELOPMENT_CONVENTIONS.md](DEVELOPMENT_CONVENTIONS.md)** - â­ Read this first!

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



## Don't Repeat These Mistakes! ðŸš«



Common errors to avoid:



1. âŒ Using `pytest` directly â†’ Use `python -m pytest`

2. âŒ Using `pip` directly â†’ Use `python -m pip`

3. âŒ Using `make` on Windows PowerShell â†’ Use `.\make.ps1` or WSL

4. âŒ Connecting to port 9200 â†’ Use port 19200

5. âŒ Forgetting to start OpenSearch â†’ `docker-compose -f test-environments/compose/docker-compose.test.yml up -d`



---



**Keep this in mind for all development work!** ðŸ’¡
