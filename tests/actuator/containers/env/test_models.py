import pytest
from src.actuator.containers.env import Env, PropertySource, PropertyValue


def test_env_model_parsing():
    # Test JSON data
    json_data = {
        "activeProfiles": [],
        "defaultProfiles": [
            "default"
        ],
        "propertySources": [
            {
                "name": "server.ports",
                "properties": {
                    "local.server.port": {
                        "value": 9090
                    }
                }
            },
            {
                "name": "systemProperties",
                "properties": {
                    "java.specification.version": {
                        "value": "21"
                    },
                    "os.name": {
                        "value": "Windows 11"
                    },
                    "user.timezone": {
                        "value": "Australia/Perth",
                        "origin": "System Environment Property"
                    }
                }
            }
        ]
    }

    # Parse the JSON
    env = Env.model_validate(json_data)

    # Test profiles
    assert len(env.active_profiles) == 0
    assert len(env.default_profiles) == 1
    assert env.default_profiles[0] == "default"

    # Test property sources
    source_names = env.get_property_source_names()
    assert len(source_names) == 2
    assert "server.ports" in source_names
    assert "systemProperties" in source_names

    # Test specific property source
    server_ports = env.get_property_source("server.ports")
    assert isinstance(server_ports, PropertySource)
    assert server_ports.name == "server.ports"
    assert len(server_ports.get_property_names()) == 1
    assert "local.server.port" in server_ports.get_property_names()

    system_props = env.get_property_source("systemProperties")
    assert isinstance(system_props, PropertySource)
    assert len(system_props.get_property_names()) == 3

    # Test specific property
    port_property = server_ports.get_property("local.server.port")
    assert isinstance(port_property, PropertyValue)
    assert port_property.value == 9090
    assert port_property.origin is None

    timezone_property = system_props.get_property("user.timezone")
    assert isinstance(timezone_property, PropertyValue)
    assert timezone_property.value == "Australia/Perth"
    assert timezone_property.origin == "System Environment Property"

    # Test get_property_value shortcut
    assert server_ports.get_property_value("local.server.port") == 9090
    assert system_props.get_property_value("java.specification.version") == "21"
    assert system_props.get_property_value("non-existent") is None

    # Test find_property
    timezone_results = env.find_property("user.timezone")
    assert len(timezone_results) == 1
    assert timezone_results[0][0] == "systemProperties"
    assert timezone_results[0][1].value == "Australia/Perth"

    port_results = env.find_property("local.server.port")
    assert len(port_results) == 1
    assert port_results[0][0] == "server.ports"
    assert port_results[0][1].value == 9090

    # Test non-existent property source and property
    assert env.get_property_source("non-existent-source") is None
    assert env.find_property("non-existent-property") == []


def test_empty_env():
    # Test minimal JSON data
    json_data = {
        "activeProfiles": [],
        "defaultProfiles": [],
        "propertySources": []
    }
    
    # Parse the JSON
    env = Env.model_validate(json_data)
    
    # Verify empty profiles and property sources
    assert len(env.active_profiles) == 0
    assert len(env.default_profiles) == 0
    assert len(env.property_sources) == 0
    assert env.get_property_source_names() == []
    assert env.find_property("any-property") == []