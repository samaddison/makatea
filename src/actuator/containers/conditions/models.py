from typing import Dict, List

from pydantic import Field

from ..common.extra_base_model import ExtraBaseModel


class ConditionEvaluation(ExtraBaseModel):
    """Represents a single Spring condition evaluation."""
    condition: str
    message: str


class Context(ExtraBaseModel):
    """Represents a Spring application context with condition evaluations.
    
    The positive_matches and negative_matches dictionaries map class names to lists of
    ConditionEvaluation objects. The keys are class names like 'BeansEndpointAutoConfiguration'.
    """
    positive_matches: Dict[str, List[ConditionEvaluation]] = Field(
        default_factory=dict, alias="positiveMatches"
    )
    negative_matches: Dict[str, List[ConditionEvaluation]] = Field(
        default_factory=dict, alias="negativeMatches"
    )
    unconditional_classes: List[str] = Field(
        default_factory=list, alias="unconditionalClasses"
    )
    
    def get_positive_configurations(self) -> List[str]:
        """Get the names of all positively matched configurations.
        
        Returns:
            A list of configuration names.
        """
        return list(self.positive_matches.keys())
    
    def get_negative_configurations(self) -> List[str]:
        """Get the names of all negatively matched configurations.
        
        Returns:
            A list of configuration names.
        """
        return list(self.negative_matches.keys())
    
    def get_positive_matches(self, configuration: str) -> List[ConditionEvaluation] | None:
        """Get condition evaluations for a specific positive configuration.
        
        Args:
            configuration: The name of the configuration
            
        Returns:
            A list of ConditionEvaluation objects, or None if not found.
        """
        return self.positive_matches.get(configuration)
    
    def get_negative_matches(self, configuration: str) -> List[ConditionEvaluation] | None:
        """Get condition evaluations for a specific negative configuration.
        
        Args:
            configuration: The name of the configuration
            
        Returns:
            A list of ConditionEvaluation objects, or None if not found.
        """
        return self.negative_matches.get(configuration)


class Conditions(ExtraBaseModel):
    """Container for Spring Boot condition evaluations.
    
    The contexts dictionary maps context names (application names) to Context objects.
    """
    contexts: Dict[str, Context] = Field(default_factory=dict)
    
    def get_context_names(self) -> List[str]:
        """Get the names of all contexts.
        
        Returns:
            A list of context names.
        """
        return list(self.contexts.keys())
    
    def get_context(self, context_name: str) -> Context | None:
        """Get a specific context by name.
        
        Args:
            context_name: The name of the context
            
        Returns:
            The Context object, or None if not found.
        """
        return self.contexts.get(context_name)