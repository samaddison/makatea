from datetime import datetime
from src.actuator.containers.auditevents import AuditEvents, AuditEvent, AuditEventData


def test_audit_events_model_parsing():
    # Test JSON data
    json_data = {
        "events": [
            {
                "timestamp": "2025-04-23T10:24:55.240133900Z",
                "principal": "anonymous",
                "type": "INFO_ACCESS",
                "data": {"endpoint": "/api/info"},
            },
            {
                "timestamp": "2025-04-23T10:25:00.123456789Z",
                "principal": "user123",
                "type": "AUTHORIZATION_FAILURE",
                "data": {"endpoint": "/api/admin", "error": "Access denied"},
            },
        ]
    }

    # Parse the JSON
    audit_events = AuditEvents.model_validate(json_data)

    # Test the number of events
    assert len(audit_events.events) == 2

    # Test first event
    event1 = audit_events.events[0]
    assert isinstance(event1, AuditEvent)
    assert isinstance(event1.timestamp, datetime)
    assert (
        event1.timestamp.isoformat()[:19] == "2025-04-23T10:24:55"
    )  # Just check date and time without microseconds
    assert event1.principal == "anonymous"
    assert event1.type == "INFO_ACCESS"
    assert isinstance(event1.data, AuditEventData)
    assert event1.data.endpoint == "/api/info"

    # Test second event with extra data field
    event2 = audit_events.events[1]
    assert isinstance(event2, AuditEvent)
    assert isinstance(event2.timestamp, datetime)
    assert event2.principal == "user123"
    assert event2.type == "AUTHORIZATION_FAILURE"
    assert isinstance(event2.data, AuditEventData)
    assert event2.data.endpoint == "/api/admin"
    assert (
        event2.data.error == "Access denied"
    )  # Extra field handled through ExtraBaseModel


def test_empty_audit_events():
    # Test empty JSON data
    json_data = {"events": []}

    # Parse the JSON
    audit_events = AuditEvents.model_validate(json_data)

    # Verify empty events list
    assert len(audit_events.events) == 0
