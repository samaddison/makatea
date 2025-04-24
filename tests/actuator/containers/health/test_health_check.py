import pytest
from src.actuator.containers.health import (
    HealthCheck, PingComponent, DiskSpaceComponent, SslComponent, 
    DiskSpaceDetails, SslDetails
)


def test_health_check_model_parsing():
    json_data = {
        "status": "UP",
        "components": {
            "diskSpace": {
                "status": "UP",
                "details": {
                    "total": 262854930432,
                    "free": 32719372288,
                    "threshold": 10485760,
                    "path": "C:\\Users\\Example\\Projects\\app\\.",
                    "exists": True
                }
            },
            "ping": {
                "status": "UP"
            },
            "ssl": {
                "status": "UP",
                "details": {
                    "validChains": [],
                    "invalidChains": []
                }
            }
        }
    }

    # Parse the JSON
    health = HealthCheck.model_validate(json_data)

    # Test overall health status
    assert health.status == "UP"
    
    # Test components presence
    assert "diskSpace" in health.components
    assert "ping" in health.components
    assert "ssl" in health.components
    
    # Test components types
    assert isinstance(health.components["diskSpace"], DiskSpaceComponent)
    assert isinstance(health.components["ping"], PingComponent)
    assert isinstance(health.components["ssl"], SslComponent)
    
    # Test ping component
    assert health.components["ping"].status == "UP"
    assert health.components["ping"].details is None
    
    # Test disk space component
    diskspace = health.components["diskSpace"]
    assert diskspace.status == "UP"
    assert isinstance(diskspace.details, DiskSpaceDetails)
    assert diskspace.details.total == 262854930432
    assert diskspace.details.free == 32719372288
    assert diskspace.details.threshold == 10485760
    assert diskspace.details.path == "C:\\Users\\Example\\Projects\\app\\."
    assert diskspace.details.exists is True
    
    # Test ssl component
    ssl = health.components["ssl"]
    assert ssl.status == "UP"
    assert isinstance(ssl.details, SslDetails)
    assert len(ssl.details.valid_chains) == 0
    assert len(ssl.details.invalid_chains) == 0