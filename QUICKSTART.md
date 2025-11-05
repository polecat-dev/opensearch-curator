# Quick Start - OpenSearch Testing

## ⚠️ Important Notes

- **Port:** OpenSearch runs on http://localhost:19200 (not 9200)
- **Python modules:** Always use `python -m` (e.g., `python -m pytest`)
- **Makefile:** Only works in WSL on Windows - use direct commands in PowerShell
- See [DEVELOPMENT_CONVENTIONS.md](DEVELOPMENT_CONVENTIONS.md) for details

## Port Configuration

Due to Windows port restrictions, the Docker Compose configuration uses:

- **OpenSearch:** http://localhost:19200 (instead of 9200)
- **OpenSearch Dashboards:** http://localhost:5601

## Start OpenSearch

```powershell
# Remove any existing containers
docker rm -f opensearch-curator-test opensearch-dashboards-test

# Start fresh
docker-compose up -d

# Wait a moment for startup, then check health
Start-Sleep -Seconds 10
curl http://localhost:19200/_cluster/health
```

## Test Connection

```powershell
# Check cluster health
curl http://localhost:19200

# Should return something like:
# {
#   "name" : "opensearch-curator-node",
#   "cluster_name" : "opensearch-curator-cluster",
#   "version" : { "number" : "3.2.0" }
# }
```

## Create Test Data

```powershell
# Create test indices
curl -X PUT "http://localhost:19200/test-index-1"
curl -X PUT "http://localhost:19200/test-index-2"
curl -X PUT "http://localhost:19200/test-index-3"

# List indices
curl "http://localhost:19200/_cat/indices?v"
```

## Test Curator

```powershell
# Show indices (use python -m)
python -m curator.singletons show_indices --hosts http://localhost:19200

# Or test opensearch_client
python -c "from opensearch_client.builder import Builder; from dotmap import DotMap; config = DotMap({'opensearch': {'client': {'hosts': ['http://localhost:19200']}}}); builder = Builder(configdict=config); client = builder.client(); print(client.info())"
```

## Stop OpenSearch

```powershell
docker-compose down

# Remove all data
docker-compose down -v
```

## Troubleshooting

### Port already in use
If you get port conflicts, check what's using the port:
```powershell
netstat -ano | findstr :19200
```

### Container name conflicts
Remove existing containers:
```powershell
docker rm -f opensearch-curator-test opensearch-dashboards-test
```

### OpenSearch not starting
Check logs:
```powershell
docker-compose logs opensearch
```

### Clean slate
Remove everything and start fresh:
```powershell
docker-compose down -v
docker system prune -f
docker-compose up -d
```
