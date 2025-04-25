from src.actuator.containers.caches import Caches, CacheManager, Cache


def test_caches_model_parsing():
    # Test JSON data
    json_data = {
        "cacheManagers": {
            "cacheManager": {
                "caches": {
                    "otherCache": {
                        "target": "com.github.benmanes.caffeine.cache.BoundedLocalCache$BoundedLocalManualCache"
                    },
                    "greetingCache": {
                        "target": "com.github.benmanes.caffeine.cache.BoundedLocalCache$BoundedLocalManualCache"
                    },
                }
            }
        }
    }

    # Parse the JSON
    caches = Caches.model_validate(json_data)

    # Test cache managers
    manager_names = caches.get_cache_manager_names()
    assert len(manager_names) == 1
    assert "cacheManager" in manager_names

    # Test specific cache manager
    cache_manager = caches.get_cache_manager("cacheManager")
    assert isinstance(cache_manager, CacheManager)

    # Test caches in manager
    cache_names = cache_manager.get_cache_names()
    assert len(cache_names) == 2
    assert "otherCache" in cache_names
    assert "greetingCache" in cache_names

    # Test specific cache
    other_cache = cache_manager.get_cache("otherCache")
    assert isinstance(other_cache, Cache)
    assert (
        other_cache.target
        == "com.github.benmanes.caffeine.cache.BoundedLocalCache$BoundedLocalManualCache"
    )

    greeting_cache = cache_manager.get_cache("greetingCache")
    assert isinstance(greeting_cache, Cache)
    assert (
        greeting_cache.target
        == "com.github.benmanes.caffeine.cache.BoundedLocalCache$BoundedLocalManualCache"
    )

    # Test get_all_cache_names
    all_cache_names = caches.get_all_cache_names()
    assert len(all_cache_names) == 1
    assert "cacheManager" in all_cache_names
    assert len(all_cache_names["cacheManager"]) == 2
    assert "otherCache" in all_cache_names["cacheManager"]
    assert "greetingCache" in all_cache_names["cacheManager"]

    # Test non-existent cache manager and cache
    assert caches.get_cache_manager("non-existent-manager") is None
    assert cache_manager.get_cache("non-existent-cache") is None


def test_empty_caches():
    # Test empty JSON data
    json_data = {"cacheManagers": {}}

    # Parse the JSON
    caches = Caches.model_validate(json_data)

    # Verify empty cache managers
    assert len(caches.get_cache_manager_names()) == 0
    assert caches.get_all_cache_names() == {}
