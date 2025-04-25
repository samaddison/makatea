from src.actuator.containers.metrics import (
    Metric,
    Measurement,
    Tag,
    format_bytes,
    format_time,
)


def test_metric_model_parsing():
    # Test JSON data based on docs/actuator/json/metrics/disk.free.json
    json_data = {
        "name": "disk.free",
        "description": "Usable space for path",
        "baseUnit": "bytes",
        "measurements": [{"statistic": "VALUE", "value": 32716156928}],
        "availableTags": [
            {
                "tag": "path",
                "values": [
                    "C:\\Users\\Juan Miguel Garcia\\IdeaProjects\\spring-boot-demo-app\\spring-boot-demo-app\\."
                ],
            }
        ],
    }

    # Parse the JSON
    metric = Metric.model_validate(json_data)

    # Test basic properties
    assert metric.name == "disk.free"
    assert metric.description == "Usable space for path"
    assert metric.base_unit == "bytes"

    # Test measurements
    assert len(metric.measurements) == 1
    measurement = metric.measurements[0]
    assert isinstance(measurement, Measurement)
    assert measurement.statistic == "VALUE"
    assert measurement.value == 32716156928

    # Test tags
    assert len(metric.available_tags) == 1
    tag = metric.available_tags[0]
    assert isinstance(tag, Tag)
    assert tag.tag == "path"
    assert len(tag.values) == 1
    assert (
        tag.values[0]
        == "C:\\Users\\Juan Miguel Garcia\\IdeaProjects\\spring-boot-demo-app\\spring-boot-demo-app\\."
    )

    # Test helper methods
    assert metric.get_value() == 32716156928
    assert metric.get_value("NON_EXISTENT") is None

    assert metric.get_tag_values("path") == [
        "C:\\Users\\Juan Miguel Garcia\\IdeaProjects\\spring-boot-demo-app\\spring-boot-demo-app\\."
    ]
    assert metric.get_tag_values("non-existent") == []

    assert metric.has_tag("path") is True
    assert metric.has_tag("non-existent") is False

    # Test value formatting
    formatted = metric.format_value()
    assert formatted == "30.47 GB"


def test_cpu_count_metric():
    # Test JSON data based on docs/actuator/json/metrics/system.cpu.count.json
    json_data = {
        "name": "system.cpu.count",
        "description": "The number of processors available to the Java virtual machine",
        "measurements": [{"statistic": "VALUE", "value": 16}],
        "availableTags": [],
    }

    # Parse the JSON
    metric = Metric.model_validate(json_data)

    # Test basic properties
    assert metric.name == "system.cpu.count"
    assert (
        metric.description
        == "The number of processors available to the Java virtual machine"
    )
    assert metric.base_unit is None

    # Test measurements
    assert len(metric.measurements) == 1
    assert metric.get_value() == 16

    # Test no tags
    assert len(metric.available_tags) == 0
    assert metric.has_tag("any") is False

    # Test value formatting with no base unit
    formatted = metric.format_value()
    assert formatted == "16"


def test_threads_states_metric():
    # Test JSON data based on docs/actuator/json/metrics/jvm.threads.states.json
    json_data = {
        "name": "jvm.threads.states",
        "description": "The current number of threads",
        "baseUnit": "threads",
        "measurements": [{"statistic": "VALUE", "value": 46}],
        "availableTags": [
            {
                "tag": "state",
                "values": [
                    "timed-waiting",
                    "new",
                    "runnable",
                    "blocked",
                    "waiting",
                    "terminated",
                ],
            }
        ],
    }

    # Parse the JSON
    metric = Metric.model_validate(json_data)

    # Test basic properties
    assert metric.name == "jvm.threads.states"
    assert metric.description == "The current number of threads"
    assert metric.base_unit == "threads"

    # Test tag values
    assert metric.has_tag("state") is True
    state_values = metric.get_tag_values("state")
    assert len(state_values) == 6
    assert "runnable" in state_values
    assert "waiting" in state_values

    # Test value formatting
    formatted = metric.format_value()
    assert formatted == "46"


def test_format_bytes():
    assert format_bytes(500) == "500 B"
    assert format_bytes(1500) == "1.46 KB"
    assert format_bytes(1024 * 1024) == "1 MB"
    assert format_bytes(1024 * 1024 * 1024) == "1 GB"
    assert format_bytes(1234567890) == "1.15 GB"
    assert format_bytes(1024 * 1024 * 1024 * 1024 * 2.5) == "2.5 TB"


def test_format_time():
    assert format_time(50) == "50 ms"
    assert format_time(50.5) == "50.5 ms"
    assert format_time(1500) == "1.5 s"
    assert format_time(60000) == "1 m"
    assert format_time(90000) == "1.5 m"
    assert format_time(3600000) == "1 h"
    assert format_time(5400000) == "1.5 h"


def test_minimal_metric():
    # Test minimal JSON data
    json_data = {
        "name": "minimal.metric",
        "description": "A minimal metric",
        "measurements": [],
        "availableTags": [],
    }

    # Parse the JSON
    metric = Metric.model_validate(json_data)

    # Test minimal metric
    assert metric.name == "minimal.metric"
    assert metric.description == "A minimal metric"
    assert metric.base_unit is None
    assert len(metric.measurements) == 0
    assert len(metric.available_tags) == 0

    # Test helper methods with minimal data
    assert metric.get_value() is None
    assert metric.format_value() == "N/A"
