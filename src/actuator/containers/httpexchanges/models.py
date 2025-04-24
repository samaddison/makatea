from datetime import datetime
from typing import Dict, List, Optional
from pydantic import Field

from ..common.extra_base_model import ExtraBaseModel


class HttpRequest(ExtraBaseModel):
    """Represents an HTTP request."""
    uri: str
    method: str
    headers: Dict[str, List[str]] = Field(default_factory=dict)
    
    def get_header(self, name: str) -> Optional[str]:
        """Get the first value of a header (case-insensitive).
        
        Args:
            name: The header name
            
        Returns:
            The first value of the header, or None if not found
        """
        # Headers in HTTP are case-insensitive
        lower_name = name.lower()
        for key, values in self.headers.items():
            if key.lower() == lower_name and values:
                return values[0]
        return None


class HttpResponse(ExtraBaseModel):
    """Represents an HTTP response."""
    status: int
    headers: Dict[str, List[str]] = Field(default_factory=dict)
    
    def get_header(self, name: str) -> Optional[str]:
        """Get the first value of a header (case-insensitive).
        
        Args:
            name: The header name
            
        Returns:
            The first value of the header, or None if not found
        """
        # Headers in HTTP are case-insensitive
        lower_name = name.lower()
        for key, values in self.headers.items():
            if key.lower() == lower_name and values:
                return values[0]
        return None


class HttpExchange(ExtraBaseModel):
    """Represents a complete HTTP exchange (request and response)."""
    timestamp: datetime
    request: HttpRequest
    response: HttpResponse
    time_taken: str = Field(alias="timeTaken")


class HttpExchanges(ExtraBaseModel):
    """Container for a list of HTTP exchanges."""
    exchanges: List[HttpExchange] = Field(default_factory=list)