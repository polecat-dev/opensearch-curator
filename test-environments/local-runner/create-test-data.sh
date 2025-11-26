#!/bin/bash
# OpenSearch Curator - Local Test Data Creator
# Creates sample indices for testing curator actions

# Configuration
OPENSEARCH_URL="https://localhost:19200"
OPENSEARCH_USER="${OPENSEARCH_USER:-admin}"
OPENSEARCH_PASSWORD="${OPENSEARCH_PASSWORD:-MyStrongPassword123!}"
INDEX_PREFIX="test-"

# Date range: Create indices for last 30 days
DAYS=30
TODAY=$(date +%s)

echo -e "\033[0;36mCreating test indices in OpenSearch at $OPENSEARCH_URL\033[0m"
echo -e "\033[0;36mPrefix: $INDEX_PREFIX\033[0m"
echo -e "\033[0;36mDate range: Last $DAYS days\033[0m"
echo ""

# Function to create index with timestamp
create_test_index() {
    local index_name=$1
    local date_str=$2
    local timestamp=$3
    
    # Create index with mappings
    local body=$(cat <<EOF
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
      "timestamp": {
        "type": "date"
      },
      "message": {
        "type": "text"
      },
      "level": {
        "type": "keyword"
      }
    }
  }
}
EOF
)
    
    # Create the index
    response=$(curl -k -s -u "$OPENSEARCH_USER:$OPENSEARCH_PASSWORD" -X PUT "$OPENSEARCH_URL/$index_name" \
        -H "Content-Type: application/json" \
        -d "$body" 2>&1)
    
    if echo "$response" | grep -q '"acknowledged":true'; then
        echo -e "  \033[0;32m[OK] Created: $index_name\033[0m"
        
        # Add a sample document
        local doc=$(cat <<EOF
{
  "timestamp": "$timestamp",
  "message": "Sample log entry for $date_str",
  "level": "INFO"
}
EOF
)
        
        curl -k -s -u "$OPENSEARCH_USER:$OPENSEARCH_PASSWORD" -X POST "$OPENSEARCH_URL/$index_name/_doc/1" \
            -H "Content-Type: application/json" \
            -d "$doc" > /dev/null 2>&1
    else
        echo -e "  \033[0;31m[FAIL] Failed: $index_name - $(echo $response | head -c 100)\033[0m"
    fi
}

# Create indices for each day
echo -e "\033[0;33mCreating indices...\033[0m"
for ((i=0; i<DAYS; i++)); do
    # Calculate date (TODAY - i days)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS date command
        date_seconds=$((TODAY - (i * 86400)))
        date_str=$(date -r $date_seconds +%Y.%m.%d)
        timestamp=$(date -r $date_seconds -u +%Y-%m-%dT%H:%M:%SZ)
    else
        # Linux date command
        date_str=$(date -d "$i days ago" +%Y.%m.%d)
        timestamp=$(date -d "$i days ago" -u +%Y-%m-%dT%H:%M:%SZ)
    fi
    
    index_name="${INDEX_PREFIX}${date_str}"
    create_test_index "$index_name" "$date_str" "$timestamp"
done

echo ""
echo -e "\033[0;33mCreating additional log indices...\033[0m"

# Create some logs-* indices too
LOG_DAYS=10
for ((i=0; i<LOG_DAYS; i++)); do
    # Calculate date (TODAY - i days)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS date command
        date_seconds=$((TODAY - (i * 86400)))
        date_str=$(date -r $date_seconds +%Y.%m.%d)
        timestamp=$(date -r $date_seconds -u +%Y-%m-%dT%H:%M:%SZ)
    else
        # Linux date command
        date_str=$(date -d "$i days ago" +%Y.%m.%d)
        timestamp=$(date -d "$i days ago" -u +%Y-%m-%dT%H:%M:%SZ)
    fi
    
    index_name="logs-${date_str}"
    create_test_index "$index_name" "$date_str" "$timestamp"
done

# Summary
echo ""
echo -e "\033[0;32mTest data creation complete!\033[0m"
echo ""
echo -e "\033[0;36mVerify with:\033[0m"
echo -e "  \033[0;37mcurl $OPENSEARCH_URL/_cat/indices?v\033[0m"
echo ""
echo -e "\033[0;36mNext steps:\033[0m"
echo -e "  \033[0;37m1. Run: curator --config curator.yml 01-list-all-indices.yml --dry-run\033[0m"
echo -e "  \033[0;37m2. Test other action files\033[0m"
echo -e "  \033[0;37m3. See README.md for full guide\033[0m"
