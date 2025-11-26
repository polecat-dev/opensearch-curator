#!/usr/bin/env bash
# Start the secure OpenSearch + LocalStack test environment

set -euo pipefail

COMPOSE_FILE="test-environments/compose/docker-compose.test.yml"
ENDPOINT="${TEST_ES_SERVER:-https://localhost:19200}"
USERNAME="${TEST_ES_USERNAME:-admin}"
PASSWORD="${TEST_ES_PASSWORD:-${OPENSEARCH_INITIAL_ADMIN_PASSWORD:-}}"
CA_CERT="${TEST_ES_CA_CERT:-certs/generated/ca/root-ca.pem}"

echo "Starting OpenSearch test environment with ${COMPOSE_FILE}..."
docker-compose -f "${COMPOSE_FILE}" up -d

echo "Waiting for OpenSearch to report a healthy cluster..."
curl_args=(--silent --show-error --fail "${ENDPOINT}/_cluster/health")
if [[ -n "${PASSWORD}" ]]; then
    curl_args=(--user "${USERNAME}:${PASSWORD}" "${curl_args[@]}")
fi
if [[ -f "${CA_CERT}" ]]; then
    curl_args=(--cacert "${CA_CERT}" "${curl_args[@]}")
else
    curl_args=(--insecure "${curl_args[@]}")
fi

attempts=0
until curl "${curl_args[@]}" >/dev/null 2>&1; do
    attempts=$((attempts + 1))
    if [[ $attempts -ge 45 ]]; then
        echo ""
        echo "OpenSearch failed to start within 90 seconds."
        echo "Inspect logs with: docker-compose -f ${COMPOSE_FILE} logs opensearch"
        exit 1
    fi
    printf '.'
    sleep 2
done
echo ""

echo ""
echo "OpenSearch is running!"
echo "  Endpoint : ${ENDPOINT}"
echo "  Dashboards: https://localhost:5601"
echo ""
echo "To stop  : ./scripts/stop-opensearch.sh"
echo "To logs  : docker-compose -f ${COMPOSE_FILE} logs -f opensearch"
