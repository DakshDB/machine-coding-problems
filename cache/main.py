from core.cache_strategy import FIFOCache
from core.cache import Cache
if __name__ == '__main__':
    
    print("Cache")
    cache = Cache(cache=FIFOCache())

    print(f"Stats {cache.stats()}")

    found, value = cache.get("A")
    print(f"Val {value}")

    for i in range(0, 11):
        val2 = cache.put(f"A{i}", f"Sorted {i}")
        print(val2)

        found, value = cache.get(f"A0")
        print(f"Val {value}")

        found, value = cache.get(f"A{i}")
        print(f"Val {value}")

    found, value = cache.get(f"A10")
    print(f"Val {value}")

    found, value = cache.get(f"A1")
    print(f"Val {value}")

    found, value = cache.get(f"A0")
    print(f"Val {value}")

    found, value = cache.get(f"A5")
    print(f"Val {value}")
    
    deleted = cache.delete("A5")

    found, value = cache.get(f"A5")
    print(f"Val {value}")
    
    print(f"Stats {cache.stats()}")
