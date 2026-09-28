from models.errors import KeyNotFound
from models.constants import CACHE_ITEM_LIMIT
from datetime import datetime
from collections import OrderedDict
from models.models import Entry
from abc import abstractmethod
from abc import ABC


class CacheStrategy(ABC):

    def __init__(self):
        pass
    
    @abstractmethod
    def get(self, key: str):
        pass

    @abstractmethod
    def put(self, key: str, value):
        pass

    @abstractmethod
    def delete(self, key):
        pass


class LRUCache(CacheStrategy):

    def __init__(self):
        
        super().__init__()
        
        self.cache: OrderedDict[str, Entry] = OrderedDict()

    def _is_capacity_full(self):
        if len(self.cache.keys()) >= CACHE_ITEM_LIMIT:
            return True
        return False


    def get(self, key):
        entry = self.cache.get(key, None)
        if entry is not None:
            self.cache.move_to_end(key)
        return entry

    def put(self, key, value):

        entry = self.cache.get(key, None)
        if entry is not None:
            entry.value = value
        
        evication = False
        if self._is_capacity_full() and entry is None:
            evication = self._evication()

        entry = Entry(
            key=key,
            value=value,
            timestamp=datetime.now()
        )

        self.cache[key] = entry
        self.cache.move_to_end(key)

        
        return True, evication, self._get_current_size()

    def delete(self, key):
        deleted = self.cache.pop(key, None)
        if deleted:
            return True, self._get_current_size()
        raise KeyNotFound() 


    def _get_current_size(self):
        return len(self.cache.keys())

    def _evication(self):
        self.cache.popitem(last=False)
        return True




class FIFOCache(CacheStrategy):

    def __init__(self):
        super().__init__()

        self.cache: OrderedDict[str, Entry] = OrderedDict()

    def _is_capacity_full(self):
        if len(self.cache.keys()) >= CACHE_ITEM_LIMIT:
            return True
        return False

    def get(self, key):
        entry = self.cache.get(key, None)
        return entry

    def put(self, key, value):
        entry = self.cache.get(key, None)
        if entry is not None:
            entry.value = value
        
        evication = False
        if self._is_capacity_full() and entry is None:
            evication = self._evication()

        entry = Entry(
            key=key,
            value=value,
            timestamp=datetime.now()
        )

        self.cache[key] = entry
        self.cache.move_to_end(key)

        
        return True, evication, self._get_current_size()

    def delete(self, key):
        deleted = self.cache.pop(key, None)
        if deleted:
            return True, self._get_current_size()
        raise KeyNotFound() 


    def _get_current_size(self):
        return len(self.cache.keys())

    def _evication(self):
        self.cache.popitem(last=False)
        return True