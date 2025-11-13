#!/usr/bin/env bash
#
# Setup script for ConvertIndexToRemote integration tests
#
# This script:
# 1. Starts LocalStack (S3) and OpenSearch with remote store configuration
# 2. Waits for services to be healthy
# 3. Creates S3 buckets in LocalStack
# 4. Registers snapshot repository in OpenSearch
# 5. Runs integration tests
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
LOCALSTACK_ENDPOINT="http://localhost:4566"
OPENSEARCH_ENDPOINT="http://localhost:19200"
AWS_ACCESS_KEY="test"
AWS_SECRET_KEY="test"
AWS_REGION="us-east-1"

echo -e "${GREEN}=== OpenSearch Curator - Remote Index Conversion Test Setup ===${NC}"
echo ""

# Function to check if a service is healthy
wait_for_service() {
    local service_name=$1
    local health_check=$2
    local max_attempts=30
    local attempt=0

    echo -e "${YELLOW}Waiting for $service_name to be ready...${NC}"
    
    while [ $attempt -lt $max_attempts ]; do
        if eval "$health_check" &>/dev/null; then
            echo -e "${GREEN}✓ $service_name is ready${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done
    
    echo -e "${RED}✗ $service_name failed to start${NC}"
    return 1
}

# Step 1: Start services
echo -e "${YELLOW}Step 1: Starting services with docker-compose...${NC}"
docker-compose -f docker-compose.test.yml up -d

# Step 2: Wait for LocalStack
echo ""
echo -e "${YELLOW}Step 2: Waiting for LocalStack...${NC}"
wait_for_service "LocalStack" "curl -f ${LOCALSTACK_ENDPOINT}/_localstack/health"

# Step 3: Wait for OpenSearch
echo ""
echo -e "${YELLOW}Step 3: Waiting for OpenSearch...${NC}"
wait_for_service "OpenSearch" "curl -f ${OPENSEARCH_ENDPOINT}/_cluster/health"

# Step 4: Create S3 buckets
echo ""
echo -e "${YELLOW}Step 4: Creating S3 buckets in LocalStack...${NC}"

export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_KEY
export AWS_DEFAULT_REGION=$AWS_REGION

buckets=("test-curator-snapshots" "test-remote-segments" "test-remote-translogs")

for bucket in "${buckets[@]}"; do
    echo -n "  Creating bucket: $bucket... "
    if aws --endpoint-url=$LOCALSTACK_ENDPOINT s3 mb s3://$bucket 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        # Bucket might already exist
        if aws --endpoint-url=$LOCALSTACK_ENDPOINT s3 ls s3://$bucket &>/dev/null; then
            echo -e "${YELLOW}✓ (already exists)${NC}"
        else
            echo -e "${RED}✗ Failed${NC}"
            exit 1
        fi
    fi
done

# Step 5: Verify OpenSearch remote store configuration
echo ""
echo -e "${YELLOW}Step 5: Verifying OpenSearch remote store configuration...${NC}"
cluster_settings=$(curl -s ${OPENSEARCH_ENDPOINT}/_cluster/settings?include_defaults=true)

if echo "$cluster_settings" | grep -q "remote_store"; then
    echo -e "${GREEN}✓ Remote store configuration detected${NC}"
else
    echo -e "${YELLOW}⚠ Remote store configuration not found (may not be enabled)${NC}"
fi

# Step 6: List registered repositories
echo ""
echo -e "${YELLOW}Step 6: Checking registered repositories...${NC}"
repos=$(curl -s ${OPENSEARCH_ENDPOINT}/_snapshot)
echo "Repositories: $repos"

# Step 7: Display service information
echo ""
echo -e "${GREEN}=== Test Environment Ready ===${NC}"
echo ""
echo "Services:"
echo "  OpenSearch: ${OPENSEARCH_ENDPOINT}"
echo "  LocalStack: ${LOCALSTACK_ENDPOINT}"
echo ""
echo "S3 Buckets:"
for bucket in "${buckets[@]}"; do
    echo "  - $bucket"
done
echo ""
echo "Environment variables:"
echo "  export TEST_ES_SERVER=${OPENSEARCH_ENDPOINT}"
echo "  export LOCALSTACK_ENDPOINT=${LOCALSTACK_ENDPOINT}"
echo "  export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY}"
echo "  export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_KEY}"
echo ""
echo -e "${GREEN}To run tests:${NC}"
echo "  pytest tests/integration/test_convert_index_to_remote.py -v"
echo ""
echo -e "${GREEN}To stop services:${NC}"
echo "  docker-compose -f docker-compose.test.yml down -v"
echo ""
