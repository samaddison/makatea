import pytest
import json
import os
import tempfile
import uuid
from unittest.mock import patch, mock_open, MagicMock
from src.config.servers.server_manager import ServerManager
from src.config.servers.spring_boot_server import SpringBootServer


@pytest.fixture
def mock_config_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch("os.path.expanduser", return_value=temp_dir):
            yield temp_dir


@pytest.fixture
def server_manager(mock_config_dir):
    """Create a server manager with a mocked config directory."""
    return ServerManager()


@pytest.fixture
def sample_server():
    """Create a sample server for testing."""
    return SpringBootServer(
        name="Test Server",
        url="http://localhost:8080",
        username="admin",
        password="secret",
    )


def test_server_manager_init(mock_config_dir):
    """Test initialization of ServerManager creates the config directory."""
    manager = ServerManager()
    config_dir = os.path.join(mock_config_dir, ".makatea")

    assert os.path.exists(config_dir)
    assert manager.servers == []


def test_add_server(server_manager, sample_server):
    """Test adding a server to the manager."""
    server_manager.add_server(sample_server)

    assert len(server_manager.servers) == 1
    assert server_manager.servers[0].name == "Test Server"
    assert server_manager.servers[0].url == "http://localhost:8080"

    # Check that the config file was created
    config_file = server_manager.config_file
    assert os.path.exists(config_file)

    # Verify file contents
    with open(config_file, "r") as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["name"] == "Test Server"
        assert data[0]["url"] == "http://localhost:8080"
        assert data[0]["username"] == "admin"
        assert data[0]["password"] == "secret"
        assert "id" in data[0]


def test_remove_server(server_manager, sample_server):
    """Test removing a server from the manager."""
    server_manager.add_server(sample_server)
    server_id = sample_server.id

    result = server_manager.remove_server(server_id)

    assert result is True
    assert len(server_manager.servers) == 0

    # Check that the config file was updated
    with open(server_manager.config_file, "r") as f:
        data = json.load(f)
        assert len(data) == 0


def test_remove_nonexistent_server(server_manager):
    """Test removing a server that doesn't exist."""
    result = server_manager.remove_server("nonexistent-id")

    assert result is False


def test_edit_server(server_manager, sample_server):
    """Test editing a server."""
    server_manager.add_server(sample_server)
    server_id = sample_server.id

    result = server_manager.edit_server(
        server_id, name="Updated Server", url="http://localhost:9090"
    )

    assert result is True
    assert server_manager.servers[0].name == "Updated Server"
    assert server_manager.servers[0].url == "http://localhost:9090"
    # Credentials should remain unchanged
    assert server_manager.servers[0].username == "admin"
    assert server_manager.servers[0].password == "secret"

    # Check that the config file was updated
    with open(server_manager.config_file, "r") as f:
        data = json.load(f)
        assert data[0]["name"] == "Updated Server"
        assert data[0]["url"] == "http://localhost:9090"


def test_edit_nonexistent_server(server_manager):
    """Test editing a server that doesn't exist."""
    result = server_manager.edit_server("nonexistent-id", name="Updated Server")

    assert result is False


def test_get_server(server_manager, sample_server):
    """Test getting a server by ID."""
    server_manager.add_server(sample_server)
    server_id = sample_server.id

    server = server_manager.get_server(server_id)

    assert server is not None
    assert server.name == "Test Server"
    assert server.url == "http://localhost:8080"
    assert server.id == server_id


def test_get_nonexistent_server(server_manager):
    """Test getting a server that doesn't exist."""
    server = server_manager.get_server("nonexistent-id")

    assert server is None


def test_list_servers(server_manager):
    """Test listing all servers."""
    # Add multiple servers
    server1 = SpringBootServer(name="Server 1", url="http://localhost:8081")
    server2 = SpringBootServer(name="Server 2", url="http://localhost:8082")
    server3 = SpringBootServer(name="Server 3", url="http://localhost:8083")

    server_manager.add_server(server1)
    server_manager.add_server(server2)
    server_manager.add_server(server3)

    servers = server_manager.list_servers()

    assert len(servers) == 3
    assert servers[0].name == "Server 1"
    assert servers[1].name == "Server 2"
    assert servers[2].name == "Server 3"


def test_load_servers_on_init():
    """Test that servers are loaded from the config file on initialization."""
    # Create a mock config file
    mock_servers = [
        {
            "name": "Saved Server 1",
            "url": "http://localhost:8081",
            "username": "user1",
            "password": "pass1",
            "id": str(uuid.uuid4()),
        },
        {
            "name": "Saved Server 2",
            "url": "http://localhost:8082",
            "username": None,
            "password": None,
            "id": str(uuid.uuid4()),
        },
    ]

    # Use a context manager to patch both exists and open
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = os.path.join(temp_dir, ".makatea")
        os.makedirs(config_dir)
        config_file = os.path.join(config_dir, "servers.json")

        # Write test data to the config file
        with open(config_file, "w") as f:
            json.dump(mock_servers, f)

        # Patch expanduser to return our temp directory
        with patch("os.path.expanduser", return_value=temp_dir):
            manager = ServerManager()

            # Verify servers were loaded
            assert len(manager.servers) == 2
            assert manager.servers[0].name == "Saved Server 1"
            assert manager.servers[1].name == "Saved Server 2"


def test_edit_server_invalid_attribute(server_manager, sample_server):
    """Test editing a server with an invalid attribute."""
    server_manager.add_server(sample_server)
    server_id = sample_server.id

    # Try to edit a non-existent attribute
    result = server_manager.edit_server(
        server_id,
        name="Updated Server",
        nonexistent_attribute="value",  # This should be ignored
    )

    assert result is True
    assert server_manager.servers[0].name == "Updated Server"
    # Verify the non-existent attribute wasn't added
    assert not hasattr(server_manager.servers[0], "nonexistent_attribute")


def test_uuid_uniqueness():
    """Test that UUIDs are unique across servers."""
    # Create multiple servers
    servers = [
        SpringBootServer(name=f"Server {i}", url=f"http://localhost:{8080 + i}")
        for i in range(100)
    ]

    # Extract all UUIDs
    uuids = [server.id for server in servers]

    # Check uniqueness
    assert len(uuids) == len(set(uuids)), "UUIDs should be unique"
