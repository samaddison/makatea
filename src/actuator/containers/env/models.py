from typing import Dict, List, Any, Optional

from pydantic import Field

from ..common.extra_base_model import ExtraBaseModel


class PropertyValue(ExtraBaseModel):
    """Represents a property value in Spring Boot environment."""

    value: Any
    origin: Optional[str] = None


class PropertySource(ExtraBaseModel):
    """Represents a property source in Spring Boot environment."""

    name: str
    properties: Dict[str, PropertyValue] = Field(default_factory=dict)

    def get_property_names(self) -> List[str]:
        """Get all property names in this source.

        Returns:
            A list of property names.
        """
        return list(self.properties.keys())

    def get_property(self, property_name: str) -> PropertyValue | None:
        """Get a specific property by name.

        Args:
            property_name: The name of the property

        Returns:
            The PropertyValue object, or None if not found.
        """
        return self.properties.get(property_name)

    def get_property_value(self, property_name: str) -> Any:
        """Get the value of a specific property by name.

        Args:
            property_name: The name of the property

        Returns:
            The property value, or None if the property is not found.
        """
        property_obj = self.get_property(property_name)
        return property_obj.value if property_obj else None


class Env(ExtraBaseModel):
    """Container for Spring Boot environment information."""

    active_profiles: List[str] = Field(default_factory=list, alias="activeProfiles")
    default_profiles: List[str] = Field(default_factory=list, alias="defaultProfiles")
    property_sources: List[PropertySource] = Field(
        default_factory=list, alias="propertySources"
    )

    def get_property_source_names(self) -> List[str]:
        """Get the names of all property sources.

        Returns:
            A list of property source names.
        """
        return [source.name for source in self.property_sources]

    def get_property_source(self, source_name: str) -> PropertySource | None:
        """Get a specific property source by name.

        Args:
            source_name: The name of the property source

        Returns:
            The PropertySource object, or None if not found.
        """
        for source in self.property_sources:
            if source.name == source_name:
                return source
        return None

    def find_property(self, property_name: str) -> List[tuple[str, PropertyValue]]:
        """Find a property across all property sources.

        Args:
            property_name: The name of the property

        Returns:
            A list of tuples containing (source_name, property_value) for each source
            where the property is found.
        """
        results = []
        for source in self.property_sources:
            property_value = source.get_property(property_name)
            if property_value:
                results.append((source.name, property_value))
        return results
