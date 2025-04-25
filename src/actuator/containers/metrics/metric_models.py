from typing import List, Dict, Any, Optional
from pydantic import Field

from ..common.extra_base_model import ExtraBaseModel


class Measurement(ExtraBaseModel):
    """Represents a single measurement for a metric."""

    statistic: str
    value: float


class Tag(ExtraBaseModel):
    """Represents a tag with its possible values for a metric."""

    tag: str
    values: List[str] = Field(default_factory=list)


class Metric(ExtraBaseModel):
    """Represents a detailed metric from Spring Boot Actuator."""

    name: str
    description: str
    base_unit: Optional[str] = Field(None, alias="baseUnit")
    measurements: List[Measurement] = Field(default_factory=list)
    available_tags: List[Tag] = Field(default_factory=list, alias="availableTags")

    def get_value(self, statistic: str = "VALUE") -> Optional[float]:
        """Get the value of a specific statistic.

        Args:
            statistic: The statistic to get (default: "VALUE")

        Returns:
            The value of the statistic, or None if not found.
        """
        for measurement in self.measurements:
            if measurement.statistic == statistic:
                return measurement.value
        return None

    def get_tag_values(self, tag_name: str) -> List[str]:
        """Get all possible values for a specific tag.

        Args:
            tag_name: The name of the tag

        Returns:
            A list of tag values, or an empty list if the tag doesn't exist.
        """
        for tag in self.available_tags:
            if tag.tag == tag_name:
                return tag.values
        return []

    def has_tag(self, tag_name: str) -> bool:
        """Check if a specific tag is available.

        Args:
            tag_name: The name of the tag

        Returns:
            True if the tag is available, False otherwise.
        """
        return any(tag.tag == tag_name for tag in self.available_tags)

    def format_value(self) -> str:
        """Format the primary value of the metric with its base unit.

        Returns:
            A formatted string representation of the metric value.
        """
        value = self.get_value()
        if value is None:
            return "N/A"

        # Format the value based on its magnitude and base unit
        if self.base_unit == "bytes":
            return format_bytes(value)
        elif self.base_unit == "milliseconds" or self.base_unit == "ms":
            return format_time(value)
        elif self.base_unit == "percent":
            return f"{value:.1f}%"
        else:
            # For most metrics, just round to 2 decimal places if needed
            return f"{value:.2f}" if value % 1 != 0 else f"{int(value)}"


def format_bytes(bytes_value: float) -> str:
    """Format a byte value into a human-readable string.

    Args:
        bytes_value: The value in bytes

    Returns:
        A formatted string with appropriate units (B, KB, MB, GB, TB).
    """
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0

    while bytes_value >= 1024 and unit_index < len(units) - 1:
        bytes_value /= 1024
        unit_index += 1

    # Format with up to 2 decimal places, but remove trailing zeros
    formatted = (
        f"{bytes_value:.2f}".rstrip("0").rstrip(".")
        if bytes_value % 1 != 0
        else f"{int(bytes_value)}"
    )
    return f"{formatted} {units[unit_index]}"


def format_time(ms_value: float) -> str:
    """Format a time value in milliseconds into a human-readable string.

    Args:
        ms_value: The value in milliseconds

    Returns:
        A formatted string with appropriate units (ms, s, m, h).
    """
    if ms_value < 1000:
        return (
            f"{ms_value:.1f} ms".rstrip("0").rstrip(".")
            if ms_value % 1 != 0
            else f"{int(ms_value)} ms"
        )

    seconds = ms_value / 1000
    if seconds < 60:
        return (
            f"{seconds:.1f} s".rstrip("0").rstrip(".")
            if seconds % 1 != 0
            else f"{int(seconds)} s"
        )

    minutes = seconds / 60
    if minutes < 60:
        return (
            f"{minutes:.1f} m".rstrip("0").rstrip(".")
            if minutes % 1 != 0
            else f"{int(minutes)} m"
        )

    hours = minutes / 60
    return (
        f"{hours:.1f} h".rstrip("0").rstrip(".")
        if hours % 1 != 0
        else f"{int(hours)} h"
    )
