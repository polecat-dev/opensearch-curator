#!/bin/bash
curl -k -X PUT "https://localhost:9200/_plugins/_security/api/internalusers/admin" \
  -H "Content-Type: application/json" \
  --cert /usr/share/opensearch/config/certs/admin/admin.crt \
  --key /usr/share/opensearch/config/certs/admin/admin.key \
  --pass curatorssl \
  -d '{
    "hash": "$2y$12$FfwIfSAX4vjB4T8uMj/.1.ky0gJT1nKi/ySwPbccLst2azl0Khor.",
    "reserved": true,
    "backend_roles": ["admin"],
    "description": "Admin user"
  }'
