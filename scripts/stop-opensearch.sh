#!/bin/bash
# Stop OpenSearch test environment

echo "🛑 Stopping OpenSearch test environment..."

docker-compose down

echo "✅ OpenSearch stopped"
echo ""
echo "To remove all data: docker-compose down -v"
