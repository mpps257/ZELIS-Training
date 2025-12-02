from cachetools import TTLCache, LRUCache

lru_cache = LRUCache(maxsize=5000)
ttl_cache = TTLCache(maxsize=5000, ttl=6000)

def get_from_cache(key: str):
    return ttl_cache.get(key) or lru_cache.get(key)

def save_to_cache(key: str, data):
    ttl_cache[key] = data
    lru_cache[key] = data
