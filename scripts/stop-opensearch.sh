#!/usr/bin/env bash
# Stop the secure OpenSearch + LocalStack test environment

set -euo pipefail

COMPOSE_FILE="test-environments/compose/docker-compose.test.yml"

echo "Stopping OpenSearch test environment..."
docker-compose -f "${COMPOSE_FILE}" down
echo "OpenSearch stopped"
echo "To remove all data run: docker-compose -f ${COMPOSE_FILE} down -v"
