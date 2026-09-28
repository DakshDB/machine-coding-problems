

from models.errors import InvalidCacheCapacity
from core.cache_strategy import LRUCache
from core.cache_strategy import CacheStrategy
from datetime import datetime
from models.models import Entry
from models.constants import CACHE_ITEM_LIMIT
class Cache:

    def __init__(self, cache: CacheStrategy = None):

        if CACHE_ITEM_LIMIT <= 0 :
            raise InvalidCacheCapacity()

        self.cache = cache or LRUCache()
        self.usage_stats: dict = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "current_size": 0,
        }

    def get(self, key):
        entry = self.cache.get(key)
        if entry:
            
            # Update Entry Details
            entry.last_hit = datetime.now()
            entry.hits += 1

            # Update stats
            self.usage_stats['hits'] += 1

            return True, entry.value

        self.usage_stats['misses'] += 1
        return False, None

    def put(self, key, value):
        stored, evication, current_size = self.cache.put(key, value)
        if evication:
            self.usage_stats['evictions'] += 1
        
        self.usage_stats['current_size'] = current_size

        return stored


    def delete(self, key):
        deleted, current_size = self.cache.delete(key)
        self.usage_stats['current_size'] = current_size

        return deleted


    def stats(self):
        return self.usage_stats

