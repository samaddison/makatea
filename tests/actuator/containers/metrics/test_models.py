import pytest
from src.actuator.containers.metrics import Metrics


def test_metrics_model_parsing():
    # Test JSON data
    json_data = {
        "names": [
            "application.ready.time",
            "application.started.time",
            "disk.free",
            "disk.total",
            "jvm.buffer.count",
            "jvm.memory.used",
            "process.uptime",
            "system.cpu.count"
        ]
    }

    # Parse the JSON
    metrics = Metrics.model_validate(json_data)

    # Test metrics names
    assert len(metrics.names) == 8
    assert "application.ready.time" in metrics.names
    assert "disk.free" in metrics.names
    assert "jvm.buffer.count" in metrics.names
    assert "process.uptime" in metrics.names
    
    # Test contains method
    assert metrics.contains("disk.free") is True
    assert metrics.contains("jvm.memory.used") is True
    assert metrics.contains("non-existent-metric") is False


def test_empty_metrics():
    # Test empty JSON data
    json_data = {"names": []}
    
    # Parse the JSON
    metrics = Metrics.model_validate(json_data)
    
    # Verify empty metrics
    assert len(metrics.names) == 0
    assert metrics.contains("any-metric") is False