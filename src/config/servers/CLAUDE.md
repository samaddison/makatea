# Server Management

## Overview
The server management module provides a way to store, retrieve, and manage Spring Boot server configurations. It uses a JSON file stored in the user's home directory under `~/.makatea/servers.json`.

## Components

### SpringBootServer
A dataclass that represents a Spring Boot server configuration with the following attributes:
- `name`: Display name for the server
- `url`: URL to connect to the server
- `username`: Optional username for authentication
- `password`: Optional password for authentication
- `id`: UUID that uniquely identifies the server (auto-generated if not provided)

### ServerManager
A class that manages SpringBootServer instances, providing methods to:
- Add new servers
- Remove servers
- Edit existing servers
- Retrieve servers by ID
- List all servers

All changes are automatically persisted to the configuration file.

## Usage Examples

### Creating and Managing Servers

```python
from src.config.servers.server_manager import ServerManager
from src.config.servers.spring_boot_server import SpringBootServer

# Initialize the server manager
manager = ServerManager()

# Create a new server
server = SpringBootServer(
    name="Production Server",
    url="https://production.example.com/actuator",
    username="admin",
    password="secure_password"
)

# Add the server to the manager
manager.add_server(server)

# Remember the server ID for later use
server_id = server.id

# List all servers
all_servers = manager.list_servers()
for server in all_servers:
    print(f"Server: {server.name}, URL: {server.url}")

# Get a specific server by ID
retrieved_server = manager.get_server(server_id)
if retrieved_server:
    print(f"Retrieved: {retrieved_server.name}")

# Edit a server
manager.edit_server(
    server_id,
    name="Updated Production Server",
    url="https://new-prod.example.com/actuator"
)

# Remove a server
manager.remove_server(server_id)
```

### Creating Servers Programmatically

```python
# Basic server with no authentication
basic_server = SpringBootServer(
    name="Development Server",
    url="http://localhost:8080/actuator"
)

# Server with authentication
auth_server = SpringBootServer(
    name="Staging Server",
    url="https://staging.example.com/actuator",
    username="admin",
    password="password123"
)

# Create a server from existing configuration data
config_data = {
    "name": "Config Server",
    "url": "https://config.example.com/actuator",
    "username": "user",
    "password": "pass"
}
imported_server = SpringBootServer.from_dict(config_data)
```

## Implementation Details

### Data Storage
Server configurations are stored in `~/.makatea/servers.json` as a JSON array of server objects. Each server is serialized using the `asdict()` function from the `dataclasses` module.

### Server Identification
Each server is assigned a unique UUID when created. This UUID is used for all operations that target a specific server (edit, remove, get). The UUID ensures that servers can be uniquely identified even if their other attributes change.

### Thread Safety
The current implementation is not thread-safe. If you need to use the ServerManager from multiple threads, you should implement appropriate synchronization.

### Security Considerations
- Passwords are stored in plain text in the configuration file
- Consider implementing encryption for sensitive information in production environments
- The configuration directory (`~/.makatea`) is created with default permissions

## Error Handling

The ServerManager provides boolean return values for operations that might fail:
- `remove_server()` returns `True` if a server was removed, `False` if the server was not found
- `edit_server()` returns `True` if a server was edited, `False` if the server was not found
- `get_server()` returns the server instance if found, or `None` if not found

Operations that modify servers (`add_server()`, `remove_server()`, `edit_server()`) automatically save changes to the configuration file.