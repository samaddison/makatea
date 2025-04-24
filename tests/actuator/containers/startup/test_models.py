import pytest
from datetime import datetime
from src.actuator.containers.startup import Startup, Timeline, Event, StartupStep, Tag


def test_startup_model_parsing():
    # Test JSON data (simplified version of the actual data)
    json_data = {
        "timeline": {
            "startTime": "2025-04-23T10:23:43.019433500Z",
            "events": [
                {
                    "endTime": "2025-04-23T10:23:43.051192200Z",
                    "duration": "PT0.0256489S",
                    "startTime": "2025-04-23T10:23:43.025543300Z",
                    "startupStep": {
                        "name": "spring.boot.application.starting",
                        "id": 0,
                        "tags": [
                            {
                                "key": "mainApplicationClass",
                                "value": "au.com.patrick.springbootdemoapp.SpringBootDemoAppApplication"
                            }
                        ]
                    }
                },
                {
                    "endTime": "2025-04-23T10:23:43.305673600Z",
                    "duration": "PT0.1963843S",
                    "startTime": "2025-04-23T10:23:43.109289300Z",
                    "startupStep": {
                        "name": "spring.boot.application.environment-prepared",
                        "id": 1,
                        "tags": []
                    }
                },
                {
                    "endTime": "2025-04-23T10:23:45.561227800Z",
                    "duration": "PT0.0067954S",
                    "startTime": "2025-04-23T10:23:45.554432400Z",
                    "startupStep": {
                        "name": "spring.boot.application.started",
                        "id": 559,
                        "tags": []
                    }
                },
                {
                    "endTime": "2025-04-23T10:23:45.563636700Z",
                    "duration": "PT0S",
                    "startTime": "2025-04-23T10:23:45.563636700Z",
                    "startupStep": {
                        "name": "spring.boot.application.ready",
                        "id": 560,
                        "tags": []
                    }
                }
            ]
        },
        "springBootVersion": "3.4.4"
    }

    # Parse the JSON
    startup = Startup.model_validate(json_data)

    # Test basic properties
    assert startup.spring_boot_version == "3.4.4"
    
    # Test timeline
    timeline = startup.timeline
    assert isinstance(timeline, Timeline)
    assert isinstance(timeline.start_time, datetime)
    assert timeline.start_time.isoformat()[:19] == "2025-04-23T10:23:43"  # Skip milliseconds/microseconds
    assert len(timeline.events) == 4
    
    # Test first event
    event = timeline.events[0]
    assert isinstance(event, Event)
    assert isinstance(event.start_time, datetime)
    assert isinstance(event.end_time, datetime)
    assert event.duration == "PT0.0256489S"
    
    # Test startup step
    step = event.startup_step
    assert isinstance(step, StartupStep)
    assert step.name == "spring.boot.application.starting"
    assert step.id == 0
    assert len(step.tags) == 1
    
    # Test tag
    tag = step.tags[0]
    assert isinstance(tag, Tag)
    assert tag.key == "mainApplicationClass"
    assert tag.value == "au.com.patrick.springbootdemoapp.SpringBootDemoAppApplication"
    
    # Test helper methods
    assert abs(startup.get_total_startup_time() - 2.544) < 0.01  # Approximately 2.544 seconds
    
    starting_events = startup.get_steps_by_name("spring.boot.application.starting")
    assert len(starting_events) == 1
    assert starting_events[0].startup_step.id == 0
    
    ready_event = startup.get_steps_by_name("spring.boot.application.ready")[0]
    assert ready_event.startup_step.id == 560
    
    # Test get_step_by_id
    step_1 = startup.get_step_by_id(1)
    assert step_1 is not None
    assert step_1.startup_step.name == "spring.boot.application.environment-prepared"
    
    # Test non-existent step
    assert startup.get_step_by_id(999) is None
    
    # Test phases
    phases = startup.get_startup_phases()
    assert len(phases) == 4  # We have 4 of the main phases in our test data
    assert "spring.boot.application.starting" in phases
    assert abs(phases["spring.boot.application.starting"] - 0.0256489) < 0.0001
    assert "spring.boot.application.environment-prepared" in phases
    assert abs(phases["spring.boot.application.environment-prepared"] - 0.1963843) < 0.0001


def test_minimal_startup():
    # Test minimal JSON data
    json_data = {
        "timeline": {
            "startTime": "2025-04-23T00:00:00Z",
            "events": []
        },
        "springBootVersion": "3.4.4"
    }
    
    # Parse the JSON
    startup = Startup.model_validate(json_data)
    
    # Verify minimal startup
    assert startup.spring_boot_version == "3.4.4"
    assert len(startup.timeline.events) == 0
    assert startup.get_total_startup_time() == 0.0
    assert startup.get_steps_by_name("any-step") == []
    assert startup.get_step_by_id(0) is None
    assert startup.get_startup_phases() == {}