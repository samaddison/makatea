from typing import Dict, Optional
from pydantic import Field
from ..common.extra_base_model import ExtraBaseModel


class Link(ExtraBaseModel):
    """Represents a hypermedia link in the Spring Boot Actuator API."""

    href: str
    templated: bool = False


class Actuator(ExtraBaseModel):
    """Root container for Spring Boot Actuator API endpoints.

    This class represents the base Actuator endpoint which provides
    links to all other available endpoints in HATEOAS format.
    """

    links: Dict[str, Link] = Field(alias="_links")

    def get_available_endpoints(self) -> list[str]:
        """Get a list of all available endpoint names.

        Returns:
            A list of endpoint names (without the 'self' endpoint).
        """
        return [key for key in self.links.keys() if key != "self"]

    def get_link(self, endpoint_name: str) -> Optional[Link]:
        """Get the Link object for a specific endpoint.

        Args:
            endpoint_name: The name of the endpoint

        Returns:
            The Link object, or None if the endpoint doesn't exist.
        """
        return self.links.get(endpoint_name)

    def get_endpoint_url(self, endpoint_name: str) -> Optional[str]:
        """Get the URL for a specific endpoint.

        Args:
            endpoint_name: The name of the endpoint

        Returns:
            The URL as a string, or None if the endpoint doesn't exist.
        """
        link = self.get_link(endpoint_name)
        return link.href if link else None

    def is_templated(self, endpoint_name: str) -> bool:
        """Check if an endpoint URL is templated.

        Args:
            endpoint_name: The name of the endpoint

        Returns:
            True if the endpoint URL is templated, False otherwise.
            Returns False if the endpoint doesn't exist.
        """
        link = self.get_link(endpoint_name)
        return link.templated if link else False
