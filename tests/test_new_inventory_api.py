import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from ..new_inventory_api import InventoryThread, detail_handling, inventory_handling, resource_inventory, list_used_resources

# Test InventoryThread Initialization
def test_inventory_thread_initialization():
    thread = InventoryThread('category', 'region_name', 'resource', 'boto_resource_name', {'key': 'value'}, 'key', lambda x: x)
    assert thread.category == 'category'
    assert thread.region_name == 'region_name'
    assert thread.resource == 'resource'
    assert thread.boto_resource_name == 'boto_resource_name'
    assert thread.node_details == {'key': 'value'}
    assert thread.key == 'key'
    assert thread.progress_callback is not None

# Mock boto3 client
@pytest.fixture
def mock_boto3_client():
    with patch('new_inventory_api.boto3.client') as mock:
        yield mock

# Test detail_handling Function
def test_detail_handling(mock_boto3_client: MagicMock | AsyncMock):
    client = mock_boto3_client.return_value
    inventory = {'key': [('item', {'detail': 'value'})]}
    node_details = {'key': {'details': {'detail': {'item_search_id': 'id', 'detail_function': 'function', 'detail_param': 'param'}}}}
    detail_handling(client, inventory, node_details, 'resource', 'key')
    client.function.assert_called()

# Test inventory_handling Function
def test_inventory_handling(mock_boto3_client: MagicMock | AsyncMock):
    client = mock_boto3_client.return_value
    node_details = {'item': {'function': 'list_buckets'}}
    inventory_handling('category', 'region_name', 'resource', 'boto_resource_name', node_details, 'key', lambda x: x)
    client.list_buckets.assert_called()

# Test resource_inventory Function
def test_resource_inventory():
    thread_list = []
    progress_callback = lambda x: x
    node_details = {'node': {'details': {}}}
    resource_inventory(progress_callback, thread_list, 'category', 'resource', 'boto_resource_name', node_details, 'region_name')
    assert len(thread_list) == 1
    assert isinstance(thread_list[0], InventoryThread)

# Test list_used_resources Function
@patch('new_inventory_api.get_all_regions', return_value=[{'RegionName': 'us-east-1'}])
@patch('new_inventory_api.boto3.client')
def test_list_used_resources(mock_boto3_client: MagicMock | AsyncMock, mock_get_all_regions):
    mock_sts_client = mock_boto3_client.return_value
    mock_sts_client.get_caller_identity.return_value = {"Account": "123456789012"}
    inventory_structure = [{'resource': {'category': 'cat', 'boto_resource_name': 'res', 'region_type': ['local'], 'inventory_nodes': {}}}]
    results = list_used_resources(inventory_structure)
    assert 'regions' in results

# Test Command-Line Arguments
def test_command_line_args(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr('sys.argv', ['new_inventory_api.py', '--resource-dir', 'resources', '--with-meta', '--with-extra', '--with-empty'])
    import new_inventory_api
    assert new_inventory_api.resource_dir == 'resources'
    assert new_inventory_api.with_meta is True
    assert new_inventory_api.with_extra is True
    assert new_inventory_api.with_empty is True