"""Test opensearch_client Builder with OpenSearch config"""

from opensearch_client.builder import Builder
from dotmap import DotMap

print("Testing opensearch_client Builder...")

config = DotMap({
    'opensearch': {
        'client': {
            'hosts': ['http://localhost:19200']
        },
        'other_settings': {
            'skip_version_test': True  # OpenSearch version checking will be implemented later
        }
    }
})

try:
    # Test with autoconnect=True to establish connection during initialization
    builder = Builder(configdict=config, autoconnect=True)
    client = builder.client
    info = client.info()
    
    print(f"✅ Connected to OpenSearch {info['version']['number']}")
    print(f"   Cluster: {info['cluster_name']}")
    print(f"   Node: {info['name']}")
    
    # Test cluster health
    health = client.cluster.health()
    print(f"   Health: {health['status']}")
    
    print("\n✅ opensearch_client Builder works!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
