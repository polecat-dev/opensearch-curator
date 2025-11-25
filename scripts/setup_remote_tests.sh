#!/usr/bin/env bash
#
# Setup script for ConvertIndexToRemote integration tests
# 1. Starts LocalStack (S3) and the secure OpenSearch test stack
# 2. Waits for both services to become healthy
# 3. Creates the S3 buckets required by the tests
# 4. Shows helpful environment variables for manual verification
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
LOCALSTACK_ENDPOINT="${LOCALSTACK_ENDPOINT:-http://localhost:4566}"
OPENSEARCH_ENDPOINT="${OPENSEARCH_ENDPOINT:-https://localhost:19200}"
CA_CERT_PATH="${TEST_ES_CA_CERT:-certs/generated/ca/root-ca.pem}"
OPENSEARCH_USERNAME="${TEST_ES_USERNAME:-admin}"
OPENSEARCH_PASSWORD="${TEST_ES_PASSWORD:-${OPENSEARCH_INITIAL_ADMIN_PASSWORD:-}}"
AWS_ACCESS_KEY="${AWS_ACCESS_KEY_ID:-test}"
AWS_SECRET_KEY="${AWS_SECRET_ACCESS_KEY:-test}"
AWS_REGION="${AWS_DEFAULT_REGION:-us-east-1}"

if [[ -f "$CA_CERT_PATH" ]]; then
    CURL_TLS_ARGS=(--cacert "$CA_CERT_PATH")
    TLS_MESSAGE="Using CA certificate at $CA_CERT_PATH"
else
    CURL_TLS_ARGS=(--insecure)
    TLS_MESSAGE="CA certificate not found; using --insecure for curl"
fi

if [[ -n "$OPENSEARCH_PASSWORD" ]]; then
    CURL_AUTH_ARGS=(--user "${OPENSEARCH_USERNAME}:${OPENSEARCH_PASSWORD}")
else
    CURL_AUTH_ARGS=()
fi

OS_CURL_ARGS=(-sS "${CURL_TLS_ARGS[@]}" "${CURL_AUTH_ARGS[@]}")

echo -e "${GREEN}=== OpenSearch Curator - Remote Index Conversion Test Setup ===${NC}"
echo -e "${YELLOW}${TLS_MESSAGE}${NC}"
echo ""

wait_for_service() {
    local service_name=$1
    shift
    local max_attempts=30
    local attempt=0
    local cmd=("$@")

    echo -e "${YELLOW}Waiting for ${service_name} to be ready...${NC}"
    while [[ $attempt -lt $max_attempts ]]; do
        if "${cmd[@]}" &>/dev/null; then
            echo -e "${GREEN}${service_name} is ready${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done

    echo -e "${RED}${service_name} failed to start${NC}"
    return 1
}

echo -e "${YELLOW}Step 1: Starting services with docker-compose...${NC}"
docker-compose -f docker-compose.test.yml up -d

echo ""
echo -e "${YELLOW}Step 2: Waiting for LocalStack...${NC}"
wait_for_service "LocalStack" curl -f "${LOCALSTACK_ENDPOINT}/_localstack/health"

echo ""
echo -e "${YELLOW}Step 3: Waiting for OpenSearch...${NC}"
wait_for_service "OpenSearch" curl -f "${OS_CURL_ARGS[@]}" "${OPENSEARCH_ENDPOINT}/_cluster/health"

echo ""
echo -e "${YELLOW}Step 4: Creating S3 buckets in LocalStack...${NC}"
export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_KEY
export AWS_DEFAULT_REGION=$AWS_REGION

buckets=("test-curator-snapshots" "test-remote-segments" "test-remote-translogs")
for bucket in "${buckets[@]}"; do
    echo -n "  Creating bucket: $bucket... "
    if aws --endpoint-url="$LOCALSTACK_ENDPOINT" s3 mb "s3://$bucket" 2>/dev/null; then
        echo -e "${GREEN}done${NC}"
    elif aws --endpoint-url="$LOCALSTACK_ENDPOINT" s3 ls "s3://$bucket" &>/dev/null; then
        echo -e "${YELLOW}already exists${NC}"
    else
        echo -e "${RED}failed${NC}"
        exit 1
    fi
done

echo ""
echo -e "${YELLOW}Step 5: Verifying OpenSearch remote store configuration...${NC}"
cluster_settings=$(curl "${OS_CURL_ARGS[@]}" "${OPENSEARCH_ENDPOINT}/_cluster/settings?include_defaults=true")
if echo "$cluster_settings" | grep -q "remote_store"; then
    echo -e "${GREEN}Remote store configuration detected${NC}"
else
    echo -e "${YELLOW}Remote store configuration not found (may be disabled)${NC}"
fi

echo ""
echo -e "${YELLOW}Step 6: Checking registered repositories...${NC}"
repos=$(curl "${OS_CURL_ARGS[@]}" "${OPENSEARCH_ENDPOINT}/_snapshot")
echo "Repositories: $repos"

echo ""
echo -e "${GREEN}=== Test Environment Ready ===${NC}"
echo "Services:"
echo "  OpenSearch: ${OPENSEARCH_ENDPOINT}"
echo "  LocalStack: ${LOCALSTACK_ENDPOINT}"
echo ""
echo "Environment variables to export:"
echo "  export TEST_ES_SERVER=${OPENSEARCH_ENDPOINT}"
echo "  export TEST_ES_CA_CERT=${CA_CERT_PATH}"
echo "  export TEST_ES_USERNAME=${OPENSEARCH_USERNAME}"
echo "  export TEST_ES_PASSWORD=${OPENSEARCH_PASSWORD}"
echo "  export LOCALSTACK_ENDPOINT=${LOCALSTACK_ENDPOINT}"
echo "  export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY}"
echo "  export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_KEY}"
echo ""
echo "To run tests:"
echo "  pytest tests/integration/test_convert_index_to_remote.py -v"
echo ""
echo "To stop services:"
echo "  docker-compose -f docker-compose.test.yml down -v"
echo ""
