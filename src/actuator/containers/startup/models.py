from datetime import datetime
from typing import List, Optional, Dict

from pydantic import Field

from ..common.extra_base_model import ExtraBaseModel


class Tag(ExtraBaseModel):
    """Represents a tag in a startup step."""
    key: str
    value: str


class StartupStep(ExtraBaseModel):
    """Represents a startup step in Spring Boot."""
    name: str
    id: int
    tags: List[Tag] = Field(default_factory=list)
    parent_id: Optional[int] = Field(None, alias="parentId")


class Event(ExtraBaseModel):
    """Represents a startup event in Spring Boot."""
    end_time: datetime = Field(alias="endTime")
    duration: str
    start_time: datetime = Field(alias="startTime")
    startup_step: StartupStep = Field(alias="startupStep")


class Timeline(ExtraBaseModel):
    """Represents the startup timeline in Spring Boot."""
    start_time: datetime = Field(alias="startTime")
    events: List[Event] = Field(default_factory=list)


class Startup(ExtraBaseModel):
    """Container for Spring Boot startup information."""
    timeline: Timeline
    spring_boot_version: str = Field(alias="springBootVersion")
    
    def get_total_startup_time(self) -> float:
        """Calculate the total startup time in seconds.
        
        Returns:
            Total startup time in seconds.
        """
        if not self.timeline.events:
            return 0.0
        
        # Find the "ready" event which should be the last one
        for event in reversed(self.timeline.events):
            if event.startup_step.name == "spring.boot.application.ready":
                # Calculate difference between ready event end time and timeline start time
                time_diff = (event.end_time - self.timeline.start_time).total_seconds()
                return time_diff
        
        # If no ready event is found, use the last event's end time
        last_event = self.timeline.events[-1]
        return (last_event.end_time - self.timeline.start_time).total_seconds()
    
    def get_steps_by_name(self, step_name: str) -> List[Event]:
        """Get all events with a specific startup step name.
        
        Args:
            step_name: The name of the startup step to search for
            
        Returns:
            A list of matching Event objects.
        """
        return [event for event in self.timeline.events 
                if event.startup_step.name == step_name]
    
    def get_step_by_id(self, step_id: int) -> Optional[Event]:
        """Get an event with a specific startup step ID.
        
        Args:
            step_id: The ID of the startup step to search for
            
        Returns:
            The matching Event object, or None if not found.
        """
        for event in self.timeline.events:
            if event.startup_step.id == step_id:
                return event
        return None
    
    def get_startup_phases(self) -> Dict[str, float]:
        """Get the main startup phases and their durations.
        
        Returns:
            A dictionary mapping phase names to durations in seconds.
        """
        phases = {}
        
        # Define the main phase step names
        main_phases = [
            "spring.boot.application.starting",
            "spring.boot.application.environment-prepared",
            "spring.boot.application.context-prepared",
            "spring.boot.application.context-loaded",
            "spring.context.refresh",
            "spring.boot.application.started",
            "spring.boot.application.ready"
        ]
        
        # Find each phase and add its duration
        for phase_name in main_phases:
            events = self.get_steps_by_name(phase_name)
            if events:
                # Extract the duration string and convert to seconds
                # Format is typically "PT0.1234S" where 0.1234 is seconds
                duration_str = events[0].duration
                # Remove "PT" prefix and "S" suffix, then convert to float
                if duration_str.startswith("PT") and duration_str.endswith("S"):
                    try:
                        seconds = float(duration_str[2:-1])
                        phases[phase_name] = seconds
                    except ValueError:
                        phases[phase_name] = 0.0
                else:
                    phases[phase_name] = 0.0
        
        return phases