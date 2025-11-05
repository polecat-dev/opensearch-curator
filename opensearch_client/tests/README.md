# OpenSearch Client Tests

This directory contains unit tests for the `opensearch_client` library (migrated from `es_client`).

## Test Structure

```
opensearch_client/tests/
├── unit/
│   ├── test_builder.py      # Tests for Builder class
│   ├── test_config.py        # Tests for configuration handling
│   ├── test_defaults.py      # Tests for default settings
│   ├── test_logging.py       # Tests for logging configuration
│   ├── test_schemacheck.py   # Tests for schema validation
│   ├── test_utils.py         # Tests for utility functions
│   └── __init__.py
├── pytest.ini                # Pytest configuration
└── README.md                 # This file
```

## Running Tests

### Run all opensearch_client tests
```bash
cd opensearch_client/tests
pytest
```

### Run specific test file
```bash
pytest unit/test_builder.py
```

### Run with verbose output
```bash
pytest -v
```

### Run with coverage
```bash
pytest --cov=opensearch_client --cov-report=term-missing
```

### Using Make
```bash
# From project root
make test-opensearch-client
```

### Using Hatch
```bash
# From project root
hatch run test:pytest opensearch_client/tests/unit
```

## Test Categories

### test_builder.py
Tests for the `Builder` class which creates OpenSearch client instances.

**What it tests:**
- Configuration file reading
- Client initialization with various auth methods
- SSL/TLS configuration
- Cloud ID parsing
- API key authentication
- Bearer token authentication

### test_config.py
Tests for configuration validation and parsing.

**What it tests:**
- YAML configuration parsing
- Configuration schema validation
- CLI option handling
- Default value handling
- Config merging

### test_defaults.py
Tests for default settings and constants.

**What it tests:**
- Default configuration values
- Option defaults
- Logging settings
- Schema definitions

### test_logging.py
Tests for logging configuration.

**What it tests:**
- Log level configuration
- Log format settings
- File logging
- Console logging
- ECS logging integration

### test_schemacheck.py
Tests for schema validation using voluptuous.

**What it tests:**
- Schema definition validation
- Password filtering
- Configuration validation
- Error handling

### test_utils.py
Tests for utility functions.

**What it tests:**
- List utilities (`ensure_list`)
- Dictionary utilities (`prune_nones`)
- YAML parsing (`get_yaml`)
- Version checking
- URL validation

## Migration from es_client

These tests were copied from the `es_client` library v8.19.5 and updated to work with OpenSearch:

### Changes Made:
1. **Import statements:**
   - `from es_client.*` → `from opensearch_client.*`
   
2. **Configuration keys:**
   - `elasticsearch:` → `opensearch:`
   - `"elasticsearch"` → `"opensearch"`

3. **Client references:**
   - References to Elasticsearch → OpenSearch (in comments/docs)

### What Stayed the Same:
- Test logic and assertions
- Test structure and organization
- Schema validation approach
- Utility function behavior

## Test Dependencies

Required packages (installed with `pip install -e ".[test]"`):
- pytest >= 7.2.1
- pytest-cov
- requests
- voluptuous
- click
- PyYAML
- opensearch-py >= 3.0.0

## Writing New Tests

### Example test structure:
```python
"""Test module for new feature"""

from unittest import TestCase
import pytest
from opensearch_client.module import function_to_test

class TestFeature(TestCase):
    """Test feature functionality"""

    def test_basic_usage(self):
        """Test basic usage"""
        result = function_to_test()
        assert result is not None

    def test_error_handling(self):
        """Test error handling"""
        with pytest.raises(ValueError):
            function_to_test(invalid_input)
```

### Best Practices:
1. Use descriptive test names
2. Test both success and failure cases
3. Use fixtures for common setup
4. Mock external dependencies (OpenSearch connections)
5. Keep tests isolated and independent

## Mocking OpenSearch

Most tests mock OpenSearch client responses to avoid needing a running instance:

```python
from unittest.mock import Mock, patch

@patch('opensearch_client.builder.OpenSearch')
def test_client_creation(mock_opensearch):
    """Test client creation without real OpenSearch"""
    mock_client = Mock()
    mock_opensearch.return_value = mock_client
    
    builder = Builder(configdict={'opensearch': {'client': {'hosts': ['localhost']}}})
    client = builder.client()
    
    assert client == mock_client
```

## Continuous Integration

These tests run automatically in CI/CD:
- On every commit
- On pull requests
- Before releases

Target: **>90% code coverage** for opensearch_client

## Known Issues

1. **Configuration Format Changes:**
   - Tests still reference old `elasticsearch` keys in some places
   - Need to verify all config examples use `opensearch` keys

2. **Client Behavior Differences:**
   - Some OpenSearch API responses may differ from Elasticsearch
   - Tests may need adjustment based on actual OpenSearch behavior

3. **Version Compatibility:**
   - Tests should verify behavior across OpenSearch 2.x and 3.x

## Contributing

When adding new tests:
1. Follow existing test patterns
2. Add docstrings explaining what's being tested
3. Update this README if adding new test categories
4. Ensure tests pass locally before committing
5. Aim for >90% coverage of new code

## Troubleshooting

### Tests fail with import errors
```bash
# Install opensearch_client in development mode
pip install -e .
```

### Tests fail with missing dependencies
```bash
# Install test dependencies
pip install -e ".[test]"
```

### Tests pass locally but fail in CI
- Check Python version compatibility (3.8-3.12)
- Verify all dependencies are in pyproject.toml
- Check for platform-specific issues

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [unittest documentation](https://docs.python.org/3/library/unittest.html)
- [OpenSearch Python Client](https://opensearch.org/docs/latest/clients/python/)
- [Original es_client tests](https://github.com/untergeek/es_client/tree/master/tests)
