from typing import List

from pydantic import Field

from ..common.extra_base_model import ExtraBaseModel


class Metrics(ExtraBaseModel):
    """Container for Spring Boot metrics information."""

    names: List[str] = Field(default_factory=list)

    def contains(self, metric_name: str) -> bool:
        """Check if a specific metric is available.

        Args:
            metric_name: The name of the metric

        Returns:
            True if the metric is available, False otherwise.
        """
        return metric_name in self.names
