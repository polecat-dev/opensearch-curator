# OpenSearch Test Environment

This directory contains Docker Compose configurations for running OpenSearch instances for testing OpenSearch Curator.

## Quick Start

### Start OpenSearch (without security)
```bash
docker-compose -f test-environments/compose/docker-compose.test.yml up -d
```

### Start OpenSearch (with security enabled)
```bash
docker-compose -f test-environments/compose/docker-compose.secure.yml up -d
```

### Check OpenSearch is running
```bash
# No security
curl http://localhost:9200

# With security
curl -k -u admin:MyStrongPassword123! https://localhost:9201
```

### View logs
```bash
docker-compose -f test-environments/compose/docker-compose.test.yml logs -f opensearch
```

### Stop OpenSearch
```bash
docker-compose -f test-environments/compose/docker-compose.test.yml down

# Or with security
docker-compose -f test-environments/compose/docker-compose.secure.yml down
```

### Remove all data (clean slate)
```bash
docker-compose -f test-environments/compose/docker-compose.test.yml down -v

# Or with security
docker-compose -f test-environments/compose/docker-compose.secure.yml down -v
```

## Configurations

### docker-compose.yml (No Security)
- **OpenSearch:** http://localhost:9200
- **OpenSearch Dashboards:** http://localhost:5601
- **Security:** Disabled (DISABLE_SECURITY_PLUGIN=true)
- **Use case:** Basic functionality testing, development

**Connection details:**
```yaml
opensearch:
  client:
    hosts: http://localhost:9200
```

### test-environments/compose/docker-compose.secure.yml (With Security)
- **OpenSearch:** https://localhost:9201 (note different port)
- **OpenSearch Dashboards:** http://localhost:5602
- **Security:** Enabled with demo certificates
- **Username:** admin
- **Password:** MyStrongPassword123!
- **Use case:** Authentication, SSL/TLS testing

**Connection details:**
```yaml
opensearch:
  client:
    hosts: https://localhost:9201
    http_auth:
      - admin
      - MyStrongPassword123!
    verify_certs: false  # Using self-signed cert
```

## Testing OpenSearch Curator

### 1. Start OpenSearch
```bash
docker-compose -f test-environments/compose/docker-compose.test.yml up -d
```

### 2. Wait for healthy status
```bash
# Check health endpoint
curl http://localhost:9200/_cluster/health

# Or use docker-compose
docker-compose ps
```

### 3. Create test data
```bash
# Create some test indices
curl -X PUT "http://localhost:9200/test-index-1"
curl -X PUT "http://localhost:9200/test-index-2"
curl -X PUT "http://localhost:9200/test-index-3"

# Verify indices
curl "http://localhost:9200/_cat/indices?v"
```

### 4. Test curator
```bash
# Show indices (dry run)
python -m curator.singletons show_indices --hosts http://localhost:9200

# Close an index (dry run)
curator_cli --host localhost --port 9200 close --name test-index-1 --dry-run
```

### 5. Run automated tests
```bash
# Set test environment
export OPENSEARCH_URL=http://localhost:9200

# Run tests
pytest tests/integration/

# Or with hatch
hatch run test:pytest
```

## Environment Variables for Testing

Create a `.env` file or set these variables:

```bash
# No security
export OPENSEARCH_URL=http://localhost:9200
export OPENSEARCH_HOST=localhost
export OPENSEARCH_PORT=9200

# With security
export OPENSEARCH_URL=https://localhost:9201
export OPENSEARCH_HOST=localhost
export OPENSEARCH_PORT=9201
export OPENSEARCH_USERNAME=admin
export OPENSEARCH_PASSWORD=MyStrongPassword123!
export OPENSEARCH_VERIFY_CERTS=false
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose -f test-environments/compose/docker-compose.test.yml logs opensearch

# Common issue: vm.max_map_count too low
# Linux:
sudo sysctl -w vm.max_map_count=262144

# Windows (WSL2):
wsl -d docker-desktop sysctl -w vm.max_map_count=262144

# macOS (Docker Desktop):
# Add to Docker Desktop settings: Resources > Advanced
```

### Port already in use
```bash
# Check what's using the port
# Windows:
netstat -ano | findstr :9200

# Linux/Mac:
lsof -i :9200

# Kill the process or change ports in docker-compose.yml
```

### OpenSearch not healthy
```bash
# Check health
curl http://localhost:9200/_cluster/health

# Check detailed node info
curl http://localhost:9200/_nodes/stats?pretty

# Restart with fresh data
docker-compose -f test-environments/compose/docker-compose.test.yml down -v
docker-compose -f test-environments/compose/docker-compose.test.yml up -d
```

### Permission denied errors
```bash
# Linux: Ensure proper permissions on data volume
docker-compose -f test-environments/compose/docker-compose.test.yml down
sudo rm -rf opensearch-data
docker-compose -f test-environments/compose/docker-compose.test.yml up -d
```

## Multiple OpenSearch Versions

You can test against different OpenSearch versions by modifying the image tag:

```yaml
services:
  opensearch:
    image: opensearchproject/opensearch:2.11.0  # or 2.12.0, 3.0.0, 3.1.0, 3.2.0
```

Or create separate compose files:
- `docker-compose.2.11.yml`
- `docker-compose.3.0.yml`
- `docker-compose.3.2.yml`

## CI/CD Integration

### GitHub Actions example:
```yaml
- name: Start OpenSearch
  run: docker-compose -f test-environments/compose/docker-compose.test.yml up -d

- name: Wait for OpenSearch
  run: |
    timeout 60 bash -c 'until curl -f http://localhost:9200/_cluster/health; do sleep 2; done'

- name: Run tests
  run: pytest tests/
  env:
    OPENSEARCH_URL: http://localhost:9200
```

## Advanced Configuration

### Custom OpenSearch settings
Create `opensearch.yml` and mount it:
```yaml
volumes:
  - ./opensearch.yml:/usr/share/opensearch/config/opensearch.yml
  - opensearch-data:/usr/share/opensearch/data
```

### Snapshot repository (S3/filesystem)
```yaml
volumes:
  - ./snapshots:/usr/share/opensearch/snapshots
environment:
  - path.repo=/usr/share/opensearch/snapshots
```

## Resources

- [OpenSearch Documentation](https://opensearch.org/docs/latest/)
- [OpenSearch Docker Hub](https://hub.docker.com/r/opensearchproject/opensearch)
- [OpenSearch Docker Documentation](https://opensearch.org/docs/latest/install-and-configure/install-opensearch/docker/)
