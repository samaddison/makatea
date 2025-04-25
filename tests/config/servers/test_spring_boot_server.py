import pytest
from dataclasses import asdict
import uuid
from src.config.servers.spring_boot_server import SpringBootServer


def test_spring_boot_server_creation():
    """Test basic creation of a SpringBootServer instance."""
    server = SpringBootServer(name="Test Server", url="http://localhost:8080")

    assert server.name == "Test Server"
    assert server.url == "http://localhost:8080"
    assert server.username is None
    assert server.password is None
    assert server.id is not None  # Should have auto-generated UUID


def test_spring_boot_server_with_credentials():
    """Test creation with username and password."""
    server = SpringBootServer(
        name="Auth Server",
        url="http://localhost:8080",
        username="admin",
        password="secret",
    )

    assert server.name == "Auth Server"
    assert server.url == "http://localhost:8080"
    assert server.username == "admin"
    assert server.password == "secret"
    assert server.id is not None


def test_spring_boot_server_with_custom_id():
    """Test creation with a specific UUID."""
    custom_id = str(uuid.uuid4())
    server = SpringBootServer(
        name="Custom ID Server", url="http://localhost:8080", id=custom_id
    )

    assert server.id == custom_id


def test_spring_boot_server_from_dict():
    """Test creating a server from a dictionary."""
    server_dict = {
        "name": "Dict Server",
        "url": "http://localhost:8080",
        "username": "user",
        "password": "pass",
        "id": "12345678-1234-5678-1234-567812345678",
    }

    server = SpringBootServer.from_dict(server_dict)

    assert server.name == "Dict Server"
    assert server.url == "http://localhost:8080"
    assert server.username == "user"
    assert server.password == "pass"
    assert server.id == "12345678-1234-5678-1234-567812345678"


def test_spring_boot_server_from_dict_minimal():
    """Test creating a server from a minimal dictionary."""
    server_dict = {"name": "Minimal Server", "url": "http://localhost:8080"}

    server = SpringBootServer.from_dict(server_dict)

    assert server.name == "Minimal Server"
    assert server.url == "http://localhost:8080"
    assert server.username is None
    assert server.password is None
    assert server.id is not None  # Should have auto-generated UUID


def test_spring_boot_server_to_dict():
    """Test converting a server to a dictionary."""
    server = SpringBootServer(
        name="Dict Test Server",
        url="http://localhost:8080",
        username="admin",
        password="secret",
    )

    server_dict = asdict(server)

    assert server_dict["name"] == "Dict Test Server"
    assert server_dict["url"] == "http://localhost:8080"
    assert server_dict["username"] == "admin"
    assert server_dict["password"] == "secret"
    assert server_dict["id"] == server.id
