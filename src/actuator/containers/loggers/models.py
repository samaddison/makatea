from typing import Dict, List, Optional

from pydantic import Field

from ..common.extra_base_model import ExtraBaseModel


class Logger(ExtraBaseModel):
    """Represents a logger configuration in Spring Boot."""
    configured_level: Optional[str] = Field(None, alias="configuredLevel")
    effective_level: str = Field(alias="effectiveLevel")


class LoggerGroup(ExtraBaseModel):
    """Represents a logger group in Spring Boot."""
    members: List[str] = Field(default_factory=list)


class Loggers(ExtraBaseModel):
    """Container for Spring Boot loggers information."""
    levels: List[str] = Field(default_factory=list)
    loggers: Dict[str, Logger] = Field(default_factory=dict)
    groups: Dict[str, LoggerGroup] = Field(default_factory=dict)
    
    def get_logger_names(self) -> List[str]:
        """Get all logger names.
        
        Returns:
            A list of logger names.
        """
        return list(self.loggers.keys())
    
    def get_logger(self, logger_name: str) -> Logger | None:
        """Get a specific logger by name.
        
        Args:
            logger_name: The name of the logger
            
        Returns:
            The Logger object, or None if not found.
        """
        return self.loggers.get(logger_name)
    
    def get_group_names(self) -> List[str]:
        """Get all logger group names.
        
        Returns:
            A list of logger group names.
        """
        return list(self.groups.keys())
    
    def get_group(self, group_name: str) -> LoggerGroup | None:
        """Get a specific logger group by name.
        
        Args:
            group_name: The name of the logger group
            
        Returns:
            The LoggerGroup object, or None if not found.
        """
        return self.groups.get(group_name)
    
    def get_group_members(self, group_name: str) -> List[str]:
        """Get the members of a specific logger group by name.
        
        Args:
            group_name: The name of the logger group
            
        Returns:
            A list of logger names in the group, or an empty list if the group is not found.
        """
        group = self.get_group(group_name)
        return group.members if group else []