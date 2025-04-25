from dataclasses import dataclass, field
import uuid
from typing import Dict, Any, Optional


@dataclass
class SpringBootServer:
    name: str
    url: str
    username: Optional[str] = None
    password: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpringBootServer":
        """Create a SpringBootServer instance from a dictionary."""
        return cls(
            name=data["name"],
            url=data["url"],
            username=data.get("username"),
            password=data.get("password"),
            id=data.get("id", str(uuid.uuid4())),
        )
