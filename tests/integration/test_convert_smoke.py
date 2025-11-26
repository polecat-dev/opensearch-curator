"""
Quick smoke test for ConvertIndexToRemote action
Tests basic functionality without requiring full remote store configuration
"""

import os
import time
import pytest
from curator import IndexList
from curator.actions import ConvertIndexToRemote
from curator.exceptions import ActionError, MissingArgument

# Check if test environment is available
OPENSEARCH_URL = os.environ.get('TEST_ES_SERVER', 'http://localhost:9200')
LOCALSTACK_URL = os.environ.get('LOCALSTACK_ENDPOINT', 'http://localhost:4566')


def test_import_action():
    """Test that the action can be imported"""
    from curator.actions import ConvertIndexToRemote

    assert ConvertIndexToRemote is not None
    assert hasattr(ConvertIndexToRemote, 'do_action')
    assert hasattr(ConvertIndexToRemote, 'do_dry_run')


def test_action_in_class_map():
    """Test that action is registered in CLASS_MAP"""
    from curator.actions import CLASS_MAP

    assert 'convert_index_to_remote' in CLASS_MAP
    assert CLASS_MAP['convert_index_to_remote'] == ConvertIndexToRemote


def test_action_in_all_actions():
    """Test that action is registered in settings"""
    from curator.defaults.settings import all_actions

    actions = all_actions()
    assert 'convert_index_to_remote' in actions


def test_storage_type_parameter_in_code():
    """Test that storage_type='remote_snapshot' is in the restore method"""
    import inspect

    source = inspect.getsource(ConvertIndexToRemote._restore_as_remote)
    assert "storage_type='remote_snapshot'" in source
    print("✓ storage_type parameter found in code")


def test_missing_repository_error():
    """Test that missing repository raises appropriate error"""
    # This test doesn't require OpenSearch to be running
    # We're testing the validation logic
    from unittest.mock import Mock, MagicMock

    # Create a mock client
    mock_client = Mock()
    mock_client.snapshot = Mock()

    # Create a mock IndexList
    mock_ilo = Mock()
    mock_ilo.client = mock_client
    mock_ilo.indices = ['test-index']
    mock_ilo.empty_list_check = Mock()

    # Mock repository_exists to return False
    import curator.actions.convert_index_to_remote as cir_module

    original_repo_exists = cir_module.repository_exists
    cir_module.repository_exists = Mock(return_value=False)

    # Mock verify_index_list
    original_verify = cir_module.verify_index_list
    cir_module.verify_index_list = Mock()

    try:
        # This should raise ActionError due to missing repository
        with pytest.raises(ActionError) as exc_info:
            action = ConvertIndexToRemote(
                mock_ilo,
                repository='non-existent-repo',
                snapshot_name='test-snapshot',
            )

        assert 'missing repository' in str(exc_info.value).lower()
        print("✓ Missing repository error raised correctly")
    finally:
        # Restore original functions
        cir_module.repository_exists = original_repo_exists
        cir_module.verify_index_list = original_verify


def test_missing_snapshot_name_error():
    """Test that missing snapshot_name raises appropriate error"""
    from unittest.mock import Mock

    mock_client = Mock()
    mock_ilo = Mock()
    mock_ilo.client = mock_client
    mock_ilo.indices = ['test-index']
    mock_ilo.empty_list_check = Mock()

    import curator.actions.convert_index_to_remote as cir_module

    cir_module.verify_index_list = Mock()
    cir_module.repository_exists = Mock(return_value=True)

    # Missing snapshot_name should raise MissingArgument
    with pytest.raises(MissingArgument) as exc_info:
        action = ConvertIndexToRemote(
            mock_ilo,
            repository='test-repo',
            snapshot_name=None,  # Missing!
        )

    assert 'snapshot_name' in str(exc_info.value).lower()
    print("✓ Missing snapshot_name error raised correctly")


def test_dry_run_mode():
    """Test that dry-run mode doesn't require actual services"""
    from unittest.mock import Mock
    import curator.actions.convert_index_to_remote as cir_module

    mock_client = Mock()
    mock_ilo = Mock()
    mock_ilo.client = mock_client
    mock_ilo.indices = ['test-index-1', 'test-index-2']
    mock_ilo.empty_list_check = Mock()

    # Mock dependencies
    cir_module.verify_index_list = Mock()
    cir_module.repository_exists = Mock(return_value=True)
    cir_module.parse_datemath = Mock(return_value='test-snapshot-20241110')
    cir_module.parse_date_pattern = Mock(return_value='test-snapshot-%Y%m%d')

    action = ConvertIndexToRemote(
        mock_ilo,
        repository='test-repo',
        snapshot_name='test-snapshot-%Y%m%d',
        remote_index_suffix='_remote',
        create_alias=True,
        delete_after=False,
    )

    # Dry-run should not raise any errors
    action.do_dry_run()
    print("✓ Dry-run mode works correctly")


def test_action_initialization():
    """Test that action initializes with correct parameters"""
    from unittest.mock import Mock
    import curator.actions.convert_index_to_remote as cir_module

    mock_client = Mock()
    mock_ilo = Mock()
    mock_ilo.client = mock_client
    mock_ilo.indices = ['test-index']
    mock_ilo.empty_list_check = Mock()

    cir_module.verify_index_list = Mock()
    cir_module.repository_exists = Mock(return_value=True)
    cir_module.parse_datemath = Mock(return_value='snapshot-20241110')
    cir_module.parse_date_pattern = Mock(return_value='snapshot-%Y%m%d')

    action = ConvertIndexToRemote(
        mock_ilo,
        repository='test-repo',
        snapshot_name='snapshot-%Y%m%d',
        use_existing_snapshot=False,
        remote_store_repository='remote-repo',
        remote_index_suffix='_remote_v2',
        create_alias=True,
        alias_name='custom-alias',
        delete_after=True,
        verify_availability=True,
        ignore_unavailable=False,
        partial=False,
        wait_for_completion=True,
        wait_interval=15,
        max_wait=300,
        skip_repo_fs_check=False,
    )

    # Verify all parameters were set correctly
    assert action.repository == 'test-repo'
    assert action.remote_store_repository == 'remote-repo'
    assert action.snapshot_name == 'snapshot-20241110'
    assert action.use_existing_snapshot == False
    assert action.remote_index_suffix == '_remote_v2'
    assert action.create_alias == True
    assert action.alias_name == 'custom-alias'
    assert action.delete_after == True
    assert action.verify_availability == True
    assert action.wait_for_completion == True
    assert action.wait_interval == 15
    assert action.max_wait == 300

    print("✓ Action initialization works correctly")


if __name__ == '__main__':
    print("Running smoke tests for ConvertIndexToRemote...")
    print("=" * 60)

    test_import_action()
    test_action_in_class_map()
    test_action_in_all_actions()
    test_storage_type_parameter_in_code()
    test_missing_repository_error()
    test_missing_snapshot_name_error()
    test_dry_run_mode()
    test_action_initialization()

    print("=" * 60)
    print("✅ All smoke tests passed!")
    print("")
    print("Note: Full integration tests require:")
    print("  - OpenSearch 3.x with remote store configuration")
    print("  - LocalStack with S3 service")
    print("  - Use: pytest tests/integration/test_convert_index_to_remote.py")
