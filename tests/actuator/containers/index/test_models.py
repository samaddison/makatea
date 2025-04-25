from src.actuator.containers.index import Actuator, Link


def test_actuator_model_parsing():
    # Test JSON data based on docs/actuator/json/actuator.json
    json_data = {
        "_links": {
            "self": {"href": "http://localhost:9090/actuator", "templated": False},
            "health": {
                "href": "http://localhost:9090/actuator/health",
                "templated": False,
            },
            "health-path": {
                "href": "http://localhost:9090/actuator/health/{*path}",
                "templated": True,
            },
            "metrics": {
                "href": "http://localhost:9090/actuator/metrics",
                "templated": False,
            },
            "metrics-requiredMetricName": {
                "href": "http://localhost:9090/actuator/metrics/{requiredMetricName}",
                "templated": True,
            },
        }
    }

    # Parse the JSON
    actuator = Actuator.model_validate(json_data)

    # Test basic properties
    assert len(actuator.links) == 5

    # Test self link
    self_link = actuator.links["self"]
    assert isinstance(self_link, Link)
    assert self_link.href == "http://localhost:9090/actuator"
    assert self_link.templated is False

    # Test helper methods
    endpoints = actuator.get_available_endpoints()
    assert len(endpoints) == 4  # All links except 'self'
    assert "health" in endpoints
    assert "health-path" in endpoints
    assert "metrics" in endpoints
    assert "metrics-requiredMetricName" in endpoints
    assert "self" not in endpoints

    # Test getting links
    health_link = actuator.get_link("health")
    assert health_link is not None
    assert health_link.href == "http://localhost:9090/actuator/health"

    # Test getting URLs
    metrics_url = actuator.get_endpoint_url("metrics")
    assert metrics_url == "http://localhost:9090/actuator/metrics"

    # Test templated check
    assert actuator.is_templated("health") is False
    assert actuator.is_templated("health-path") is True
    assert actuator.is_templated("non-existent") is False

    # Test getting non-existent endpoints
    assert actuator.get_link("non-existent") is None
    assert actuator.get_endpoint_url("non-existent") is None


def test_minimal_actuator():
    # Test minimal JSON data
    json_data = {"_links": {"self": {"href": "http://localhost:9090/actuator"}}}

    # Parse the JSON
    actuator = Actuator.model_validate(json_data)

    # Test minimal actuator
    assert len(actuator.links) == 1
    assert "self" in actuator.links
    assert actuator.links["self"].href == "http://localhost:9090/actuator"
    assert actuator.links["self"].templated is False  # Default value

    # Test helper methods with minimal data
    assert len(actuator.get_available_endpoints()) == 0
