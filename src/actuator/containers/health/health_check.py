from typing import Dict, Any, Type
from pydantic import Field

from ..common.extra_base_model import ExtraBaseModel
from .components import Component
from .ping_component import PingComponent
from .disk_space_component import DiskSpaceComponent
from .ssl_component import SslComponent


class HealthCheck(ExtraBaseModel):
    status: str
    components: Dict[str, Component] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        # Map component types based on their keys
        component_mapping: Dict[str, Type[Component]] = {
            "ping": PingComponent,
            "diskSpace": DiskSpaceComponent,
            "ssl": SslComponent,
        }

        # Convert generic components to their specific types
        for key, component in list(self.components.items()):
            if key in component_mapping:
                model_cls = component_mapping[key]
                specific_component = model_cls(**component.model_dump())
                self.components[key] = specific_component
