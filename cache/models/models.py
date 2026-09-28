from datetime import datetime


class Entry:
    
    def __init__(self, key:str, value, timestamp: datetime, last_hit: datetime = None, hits: int = 0):
        self.key = key
        self.value = value
        self.timestamp = timestamp
        self.last_hit = last_hit
        self.hits = hits

