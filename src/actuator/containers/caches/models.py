from typing import Dict, List

from pydantic import Field

from ..common.extra_base_model import ExtraBaseModel


class Cache(ExtraBaseModel):
    """Represents a cache in Spring Boot."""

    target: str


class CacheManager(ExtraBaseModel):
    """Represents a cache manager in Spring Boot.

    The caches dictionary maps cache names (as strings) to Cache objects.
    """

    caches: Dict[str, Cache] = Field(default_factory=dict)

    def get_cache_names(self) -> List[str]:
        """Get the names of all caches in this cache manager.

        Returns:
            A list of cache names.
        """
        return list(self.caches.keys())

    def get_cache(self, cache_name: str) -> Cache | None:
        """Get a specific cache by name.

        Args:
            cache_name: The name of the cache

        Returns:
            The Cache object, or None if not found.
        """
        return self.caches.get(cache_name)


class Caches(ExtraBaseModel):
    """Container for Spring Boot cache information.

    The cache_managers dictionary maps cache manager names to CacheManager objects.
    """

    cache_managers: Dict[str, CacheManager] = Field(
        alias="cacheManagers", default_factory=dict
    )

    def get_cache_manager_names(self) -> List[str]:
        """Get the names of all cache managers.

        Returns:
            A list of cache manager names.
        """
        return list(self.cache_managers.keys())

    def get_cache_manager(self, manager_name: str) -> CacheManager | None:
        """Get a specific cache manager by name.

        Args:
            manager_name: The name of the cache manager

        Returns:
            The CacheManager object, or None if not found.
        """
        return self.cache_managers.get(manager_name)

    def get_all_cache_names(self) -> Dict[str, List[str]]:
        """Get all cache names organized by cache manager.

        Returns:
            A dictionary mapping cache manager names to lists of cache names.
        """
        result = {}
        for manager_name, manager in self.cache_managers.items():
            result[manager_name] = manager.get_cache_names()
        return result
