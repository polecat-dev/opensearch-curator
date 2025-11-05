#!/bin/bash
# Start OpenSearch test environment

set -e

echo "🚀 Starting OpenSearch test environment..."

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed"
    exit 1
fi

# Start OpenSearch
docker-compose up -d

echo "⏳ Waiting for OpenSearch to be healthy..."

# Wait for OpenSearch to be healthy (max 60 seconds)
timeout 60 bash -c 'until curl -f -s http://localhost:9200/_cluster/health > /dev/null 2>&1; do 
    echo -n "."
    sleep 2
done' || {
    echo ""
    echo "❌ OpenSearch failed to start within 60 seconds"
    echo "Check logs with: docker-compose logs opensearch"
    exit 1
}

echo ""
echo "✅ OpenSearch is running!"
echo ""
echo "📊 Cluster health:"
curl -s http://localhost:9200/_cluster/health?pretty
echo ""
echo "🔗 OpenSearch: http://localhost:9200"
echo "🔗 Dashboards: http://localhost:5601"
echo ""
echo "To stop: ./scripts/stop-opensearch.sh"
echo "To view logs: docker-compose logs -f opensearch"
