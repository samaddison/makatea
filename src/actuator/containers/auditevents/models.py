from datetime import datetime
from typing import List

from pydantic import Field

from ..common.extra_base_model import ExtraBaseModel


class AuditEventData(ExtraBaseModel):
    """Data associated with an audit event.

    This is a flexible model that can contain different fields depending on the event type.
    """

    endpoint: str = ""
    # We allow other fields to be added dynamically


class AuditEvent(ExtraBaseModel):
    """Represents a single audit event."""

    timestamp: datetime
    principal: str
    type: str
    data: AuditEventData


class AuditEvents(ExtraBaseModel):
    """Container for a list of audit events."""

    events: List[AuditEvent] = Field(default_factory=list)
