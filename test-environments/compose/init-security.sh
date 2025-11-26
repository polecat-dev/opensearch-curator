#!/bin/bash
# Wait for OpenSearch to be ready
echo "Waiting for OpenSearch to start..."
until curl -sSfk https://localhost:9200 > /dev/null 2>&1; do
    echo "OpenSearch not ready yet, waiting..."
    sleep 5
done

echo "OpenSearch is up, initializing security..."

# Run securityadmin to initialize security index
cd /usr/share/opensearch/plugins/opensearch-security/tools

./securityadmin.sh \
    -cd /usr/share/opensearch/config/opensearch-security/ \
    -cacert /usr/share/opensearch/config/certs/ca/root-ca.pem \
    -cert /usr/share/opensearch/config/certs/admin/admin.crt \
    -key /usr/share/opensearch/config/certs/admin/admin.key \
    -keypass curatorssl \
    -icl \
    -nhnv

if [ $? -eq 0 ]; then
    echo "Security initialization successful!"
else
    echo "Security initialization failed!"
    exit 1
fi
