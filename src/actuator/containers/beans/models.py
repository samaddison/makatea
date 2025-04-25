from typing import Dict, List

from pydantic import Field

from ..common.extra_base_model import ExtraBaseModel


class Bean(ExtraBaseModel):
    """Represents a Spring Bean definition."""

    aliases: List[str] = Field(default_factory=list)
    scope: str
    type: str
    resource: str = ""
    dependencies: List[str] = Field(default_factory=list)


class Context(ExtraBaseModel):
    """Represents a Spring application context.

    The beans dictionary maps bean names (as strings) to Bean objects.
    """

    beans: Dict[str, Bean] = Field(default_factory=dict)


class Beans(ExtraBaseModel):
    """Container for Spring Bean information.

    The contexts dictionary maps context names (as strings) to Context objects.
    The context name is typically the application name, which can vary.
    """

    contexts: Dict[str, Context] = Field(default_factory=dict)

    def get_context_names(self) -> List[str]:
        """Get the names of all available contexts.

        Returns:
            A list of context names.
        """
        return list(self.contexts.keys())

    def get_bean_names(self, context_name: str) -> List[str]:
        """Get the names of all beans in a specific context.

        Args:
            context_name: The name of the context

        Returns:
            A list of bean names, or an empty list if the context doesn't exist.
        """
        if context_name in self.contexts:
            return list(self.contexts[context_name].beans.keys())
        return []

    def get_bean(self, context_name: str, bean_name: str) -> Bean | None:
        """Get a specific bean from a specific context.

        Args:
            context_name: The name of the context
            bean_name: The name of the bean

        Returns:
            The Bean object, or None if not found.
        """
        if (
            context_name in self.contexts
            and bean_name in self.contexts[context_name].beans
        ):
            return self.contexts[context_name].beans[bean_name]
        return None
