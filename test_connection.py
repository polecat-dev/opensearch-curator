"""Test OpenSearch connection using opensearch_client"""

from opensearchpy import OpenSearch

# Direct connection test (no builder)
print("Testing direct OpenSearch connection...")
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 19200}],
    http_compress=True,
    use_ssl=False,
    verify_certs=False
)

info = client.info()
print(f"✅ Connected to OpenSearch {info['version']['number']}")
print(f"   Cluster: {info['cluster_name']}")
print(f"   Node: {info['name']}")

# Test cluster health
health = client.cluster.health()
print(f"   Health: {health['status']}")

# List indices
indices = client.cat.indices(format='json')
print(f"   Indices: {len(indices)}")

print("\n✅ All tests passed!")
