from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import Field

from ..common.extra_base_model import ExtraBaseModel


class License(ExtraBaseModel):
    """Represents a license in SBOM."""

    license: Dict[str, str] = Field(default_factory=dict)


class Hash(ExtraBaseModel):
    """Represents a hash in SBOM."""

    alg: str
    content: str


class ExternalReference(ExtraBaseModel):
    """Represents an external reference in SBOM."""

    type: str
    url: str


class Property(ExtraBaseModel):
    """Represents a property in SBOM."""

    name: str
    value: str


class Component(ExtraBaseModel):
    """Represents a component in SBOM."""

    type: str
    bom_ref: Optional[str] = Field(None, alias="bom-ref")
    group: Optional[str] = None
    name: str
    version: str
    description: Optional[str] = None
    author: Optional[str] = None
    hashes: List[Hash] = Field(default_factory=list)
    licenses: List[License] = Field(default_factory=list)
    purl: Optional[str] = None
    modified: bool = False
    external_references: List[ExternalReference] = Field(
        default_factory=list, alias="externalReferences"
    )
    properties: List[Property] = Field(default_factory=list)


class Tool(ExtraBaseModel):
    """Represents a tool in SBOM metadata."""

    components: List[Component] = Field(default_factory=list)
    services: List[Any] = Field(default_factory=list)


class Metadata(ExtraBaseModel):
    """Represents metadata in SBOM."""

    timestamp: datetime
    tools: Tool
    component: Component
    licenses: List[License] = Field(default_factory=list)


class Dependency(ExtraBaseModel):
    """Represents a dependency in SBOM."""

    ref: str
    depends_on: List[str] = Field(default_factory=list, alias="dependsOn")


class SBOM(ExtraBaseModel):
    """Represents a Software Bill of Materials (SBOM)."""

    bom_format: str = Field(alias="bomFormat")
    spec_version: str = Field(alias="specVersion")
    serial_number: str = Field(alias="serialNumber")
    version: int
    metadata: Metadata
    components: List[Component] = Field(default_factory=list)
    dependencies: List[Dependency] = Field(default_factory=list)

    def get_component_by_ref(self, bom_ref: str) -> Optional[Component]:
        """Get a component by its BOM reference.

        Args:
            bom_ref: The BOM reference of the component

        Returns:
            The Component object, or None if not found.
        """
        # First check the main component in metadata
        if (
            self.metadata.component.bom_ref
            and self.metadata.component.bom_ref == bom_ref
        ):
            return self.metadata.component

        # Then check the components list
        for component in self.components:
            if component.bom_ref and component.bom_ref == bom_ref:
                return component

        # Then check tools components
        for tool_component in self.metadata.tools.components:
            if tool_component.bom_ref and tool_component.bom_ref == bom_ref:
                return tool_component

        return None

    def get_dependencies_for(self, bom_ref: str) -> List[str]:
        """Get the dependencies for a component.

        Args:
            bom_ref: The BOM reference of the component

        Returns:
            A list of BOM references for the dependencies, or an empty list if none found.
        """
        for dependency in self.dependencies:
            if dependency.ref == bom_ref:
                return dependency.depends_on
        return []
